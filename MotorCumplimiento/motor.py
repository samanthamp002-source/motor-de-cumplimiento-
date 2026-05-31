import os
import json
import re
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
app.json.sort_keys = False

MODEL_NAME = "phi3"  
OLLAMA_HOST_ACTIVO = None

def obtener_host_ollama():
    global OLLAMA_HOST_ACTIVO
    if OLLAMA_HOST_ACTIVO:
        return OLLAMA_HOST_ACTIVO
    hosts_a_probar = ["http://127.0.0.1:11434", "http://localhost:11434"]
    for host in hosts_a_probar:
        try:
            respuesta = requests.get(host, timeout=1.5)
            if respuesta.status_code == 200:
                OLLAMA_HOST_ACTIVO = host
                return OLLAMA_HOST_ACTIVO
        except Exception:
            continue
    return None

def comprobar_ollama():
    return obtener_host_ollama() is not None

def cargar_reglas():
    ruta_reglas = os.path.join(os.path.dirname(__file__), 'reglas.json')
    if os.path.exists(ruta_reglas):
        try:
            with open(ruta_reglas, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"reglas": []}

def extraer_y_limpiar_json(texto_crudo):
    if not texto_crudo:
        return ""
    texto_limpio = texto_crudo.replace('“', '"').replace('’', "'").replace('‘', "'").replace('”', '"')
    match = re.search(r'(\{.*\})', texto_limpio, re.DOTALL)
    if match:
        json_detectado = match.group(1)
    else:
        json_detectado = texto_limpio
    json_detectado = re.sub(r',\s*\}', '}', json_detectado)
    json_detectado = re.sub(r',\s*\]', ']', json_detectado)
    return json_detectado.strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluar', methods=['POST'])
def evaluar():
    data = request.get_json()
    texto_usuario = data.get('texto', '').strip()
    
    if not texto_usuario:
        return jsonify({
            "cumple_todo": False,
            "incumplimientos": [
                {
                    "id_regla": "TEXTO-VACIO", 
                    "motivo": "No se ingresó ningún texto para analizar.", 
                    "sugerencia": "Por favor, pega un fragmento de tu documento de estadía."
                }
            ]
        })

    texto_minusculas = texto_usuario.lower()
    incumplimientos_detectados = []

    #  1. FILTROS PREVIOS CRÍTICOS (MÁXIMA PRIORIDAD - PALABRAS EXACTAS)
 
    palabras_informales = [
        "chamba", "rollo", "desmadre", "despapaye", "cochinero", "enredado", 
        "chafa", "jale al cien", "jale", "picabas", "pique", "trabado", "traba", 
        "guardadita", "robar", "reciclar", "quejando", "tronar", "whatsapp", 
        "padres", "lata", "aburrá", "aburra", "vieja", "viejas", "viejos", "viejo"
    ]
    
    encontradas = []
    for palabra in palabras_informales:
        if re.search(r'\b' + re.escape(palabra) + r'\b', texto_minusculas):
            encontradas.append(palabra)
    
    if encontradas:
        incumplimientos_detectados.append({
            "id_regla": "LENGUAJE-ACADEMICO",
            "motivo": f"El documento emplea vocabulario informal o coloquial no apto para ingeniería (palabras detectadas: {', '.join(encontradas)}).",
            "sugerencia": "Sustituye los términos coloquiales y modismos por tecnicismos formales redactados en tercera persona."
        })

  
    # 📌 2. REGLA INSTITUCIONAL: REDACCIÓN EN TERCERA PERSONA EN OBJETIVOS

    # Verbos o pronombres comunes que indican primera persona (nosotros/yo) o planteamientos informales directos
    delatores_primera_persona = ["podemos", "hice", "voy", "diseñé", "hacer", "crear", "revisar", "programamos", "desarrollé"]
    
    lineas = texto_usuario.split('\n')
    for linea in lineas:
        linea_limpia = linea.strip()
        # Detectamos si la línea pertenece a la declaración de un objetivo
        match_objetivo = re.match(r'^(objetivo\s+general|objetivos\s+específicos|objetivo\s+específico)[\s*:\-]*\s*(.*)$', linea_limpia, re.IGNORECASE)
        
        if match_objetivo:
            contenido_objetivo = match_objetivo.group(2).strip()
            # Quitamos viñetas iniciales (*, -, etc.)
            contenido_objetivo = re.sub(r'^[\*\-\•\s\d\.\)]+', '', contenido_objetivo).strip()
            contenido_obj_min = contenido_objetivo.lower()
            
            if contenido_obj_min:
                detectadas_en_objetivo = []
                for delator in delatores_primera_persona:
                    if re.search(r'\b' + re.escape(delator) + r'\b', contenido_obj_min):
                        detectadas_en_objetivo.append(delator)
                
                # Si se detecta primera persona o falta de rigor formal en objetivos
                if detectadas_en_objetivo:
                    incumplimientos_detectados.append({
                        "id_regla": "OBJETIVOS-TERCERA-PERSONA",
                        "motivo": f"La redacción del objetivo contiene expresiones o verbos que rompen la estructura impersonal o formal (palabras detectadas: {', '.join(detectadas_en_objetivo)}).",
                        "sugerencia": "LOS OBJETIVOS DEBEN DE ESTAR EN TERCERA PERSONA (VOZ IMPERSONAL). Reestructure el enunciado eliminando verbos en primera persona ('podemos') o acciones directas e informales, utilizando conjugaciones neutras y académicas."
                    })

    # Si se acumuló cualquier error (palabras prohibidas o de objetivos), se corta el flujo aquí
    if incumplimientos_detectados:
        return jsonify({
            "cumple_todo": False,
            "incumplimientos": incumplimientos_detectados
        })

    # Filtro complementario anti-plantillas vacías
    if "esta es la primera hoja" in texto_minusculas and len(texto_usuario.split()) < 40:
        return jsonify({
            "cumple_todo": False,
            "incumplimientos": [
                {
                    "id_regla": "REGLA-ESTRUCTURA",
                    "motivo": "Se detectó una plantilla vacía o texto simulado provisional de introducción.",
                    "sugerencia": "Por favor, desarrolle el contenido real de la introducción del proyecto."
                }
            ]
        })

    # ======================================================================
    # 🤖 3. AUDITORÍA CON INTELIGENCIA ARTIFICIAL (OLLAMA - PHI3)
    # ======================================================================
    if comprobar_ollama():
        host_correcto = obtener_host_ollama()
        url_generar = f"{host_correcto}/api/generate"
        base_reglas = cargar_reglas()
        reglas_texto = json.dumps(base_reglas, ensure_ascii=False)

        prompt = f"""
        [SISTEMA]: Eres un Auditor Académico de la Universidad de la Sierra especializado en Ingeniería en Sistemas.
        [REGLAS INSTITUCIONALES]: {reglas_texto}
        [TEXTO DEL ALUMNO]: "{texto_usuario}"
        
        [INSTRUCCIÓN CRÍTICA]: Evalúa el rigor técnico. Si el texto no posee faltas ortográficas graves ni lenguaje informal, responde con cumple_todo: true.
        
        Responde ESTRICTAMENTE en formato JSON limpio:
        {{
            "cumple_todo": true,
            "incumplimientos": []
        }}
        """

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0}
        }

        try:
            response = requests.post(url_generar, json=payload, timeout=25)
            respuesta_cruda = response.json().get('response', '').strip()
            json_extraido = extraer_y_limpiar_json(respuesta_cruda)
            resultado_auditoria = json.loads(json_extraido)
            return jsonify(resultado_auditoria)
        except Exception:
            pass 

    # ======================================================================
    # 🛡️ 4. RESPALDO LÓGICO HEURÍSTICO (Por si la IA está desconectada)
    # ======================================================================
    palabras_tecnicas = ["laravel", "mvc", "scrum", "api", "swagger", "dto", "arquitectura", "git", "php", "base de datos", "flask", "sqlalchemy", "python"]
    conteo_hits = sum(1 for pt in palabras_tecnicas if pt in texto_minusculas)

    if conteo_hits < 2 and len(texto_usuario.split()) < 50:
        return jsonify({
            "cumple_todo": False,
            "incumplimientos": [
                {
                    "id_regla": "PROFUNDIDAD-TECNICA",
                    "motivo": "El fragmento analizado carece de la profundidad técnica requerida o no contiene elementos del stack de software.",
                    "sugerencia": "Desarrolle el apartado integrando herramientas, lenguajes y metodologías utilizadas."
                }
            ]
        })

    return jsonify({
        "cumple_todo": True,
        "incumplimientos": []
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)