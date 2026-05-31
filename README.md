# motor-de-cumplimiento- 
# Motor de Cumplimiento Normativo para Guías de Estadía Offline
### División de Ingeniería y Tecnologías — Universidad de la Sierra

Este repositorio contiene un sistema automatizado híbrido diseñado para auditar el rigor académico y la estructura formal de las Memorias de Estadía institucionales. El objetivo principal es identificar desviaciones de lenguaje coloquial, asegurar el uso estricto de la **tercera persona (voz impersonal)** en los objetivos y validar la profundidad técnica antes de la entrega final de los proyectos.

---

## Stack Tecnológico

- **Backend:** Python 3.x, Flask (Framework web ligero)
- **Procesamiento de Lenguaje:** Ollama, Phi-3 (Small Language Model de Microsoft)
- **Frontend:** HTML5, CSS3, JavaScript Asíncrono (Fetch API)

---

## Estructura del Proyecto

A continuación se detalla la distribución de los componentes del software en el entorno local:
- `motor.py`: Servidor Flask y procesamiento de filtros de prioridad.
- `reglas.json`: Diccionario normativo institucional.
- `templates/index.html`: Interfaz gráfica de usuario.
- `static/logo_unisierra.png`: Identidad visual de la institución.

---

## Instalación y Configuración Local

Sigue estos pasos para desplegar el entorno de desarrollo local:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/samanthamp002-source/motor-cumplimiento-unisierra.git](https://github.com/samanthamp002-source/motor-cumplimiento-unisierra.git)
cd motor-cumplimiento-unisierra
