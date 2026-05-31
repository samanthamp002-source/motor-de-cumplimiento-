import requests
import json

# Ruta local de tu servidor Flask
URL_API = "http://localhost:5000/evaluar"

casos_prueba = [
    # --- 5 ENTRADAS CORRECTAS (Con rigor técnico de ingeniería) ---
    {
        "id": 1,
        "tipo": "Cumple",
        "texto": "El presente proyecto de estadías expone el desarrollo de un Sistema Web para Gestión de Inscripciones utilizando la Metodología Incremental con el framework Laravel y el gestor de bases de datos MySQL."
    },
    {
        "id": 2,
        "tipo": "Cumple",
        "texto": "Para el levantamiento de requerimientos funcionales y no funcionales del software, se utilizó el estándar internacional IEEE 830, garantizando una especificación formal de requisitos que mitiga la ambigüedad."
    },
    {
        "id": 3,
        "tipo": "Cumple",
        "texto": "Se aplicó la Metodología de Desarrollo Incremental, estructurando el proyecto en tres incrementos bien definidos, cada uno acompañado de sus respectivas historias de usuario y diagramas de caso de uso."
    },
    {
        "id": 4,
        "tipo": "Cumple",
        "texto": "El backend de la plataforma fue desarrollado utilizando el lenguaje PHP bajo el patrón de arquitectura MVC (Modelo-Vista-Controlador) provisto por Laravel, asegurando el cumplimiento de los estándares PSR-1."
    },
    {
        "id": 5,
        "tipo": "Cumple",
        "texto": "Para asegurar la calidad y correcto funcionamiento de los módulos del sistema, se diseñó e implementó una suite de pruebas de caja negra y automatización con Selenium, validando los flujos."
    },
    
    # --- 5 ENTRADAS INCORRECTAS (Lenguaje informal, vago o comercial) ---
    {
        "id": 6,
        "tipo": "Falla",
        "texto": "Este proyecto trata sobre una página para vender arte por internet. Se usaron tecnologías modernas para hacer que funcionara correctamente y tuviera varias funciones como registro, productos y compras."
    },
    {
        "id": 7,
        "tipo": "Falla",
        "texto": "Hicimos un sistema para una escuela que guarda las horas de los alumnos en una base de datos. Está bonito el diseño y se supone que jala rápido cuando le picas al botón de guardar."
    },
    {
        "id": 8,
        "tipo": "Falla",
        "texto": "El sistema se conecta a una base de datos normal. No usamos ninguna metodología complicada porque el equipo es chico y preferimos ir programando las pantallas conforme el cliente las iba pidiendo."
    },
    {
        "id": 9,
        "tipo": "Falla",
        "texto": "Introducción: En este trabajo se va a hablar del software que se hizo para controlar los registros de la organización Casa Grande de manera fácil y rápida."
    },
    {
        "id": 10,
        "tipo": "Falla",
        "texto": "Un código que analiza si los documentos están bien o mal usando inteligencia artificial local sin internet para que los maestros revisen rápido los archivos."
    }
]

# Encabezado estético de la tabla
print(f"\n{'ID':<4} | {'TIPO ESPERADO':<15} | {'CUMPLE MOTOR':<12} | {'OBSERVACIÓN EXTRAÍDA DEL MOTOR'}")
print("-" * 120)

# Ejecución y consulta dinámica al motor
for caso in casos_prueba:
    try:
        res = requests.post(URL_API, json={"texto": caso["texto"]}, timeout=30).json()
        cumple = "SÍ" if res.get("cumple_todo") else "NO"
        
        if res.get("incumplimientos"):
            motivo = res["incumplimientos"][0]["motivo"]
        else:
            motivo = "Texto aprobado exitosamente por cumplir estándares técnicos de ingeniería."
            
        print(f"{caso['id']:<4} | {caso['tipo']:<15} | {cumple:<12} | {motivo[:75]}...")
    except Exception:
        print(f"{caso['id']:<4} | {caso['tipo']:<15} | ERROR        | Asegúrate de que motor.py esté corriendo en el puerto 5000.")