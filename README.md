# Dashboard académico: Mortalidad en Colombia (2019)

## Introducción
Este proyecto despliega una solución analítica moderna desarrollada enteramente en Python, orientada a la visualización interactiva y el procesamiento de grandes volúmenes de datos. Utilizando bases de datos cruzadas del DANE y los registros CIE-10, la plataforma abstrae un volumen importante de datos crudos sobre las defunciones no fetales colombianas del año 2019, convirtiéndolos en conocimiento geográfico y demográfico útil.

## Objetivo de la iniciativa
El propósito de este aplicativo es proveer una herramienta exploratoria en un entorno en la nube (PaaS). A través de gráficos interactivos de alta legibilidad, el dashboard busca evidenciar patrones ocultos como las concentraciones de violencia (particularmente el uso de armas de fuego), las principales comorbilidades terminales de la población y el agudo índice de la sobremortalidad masculina.

## Estructura del proyecto
* `app.py`: El corazón funcional del sistema. Integra la lógica de limpieza de datos (Pandas), la construcción por capas gráficas (Plotly) y el servidor web frontend (Dash).
* `requirements.txt` / `Procfile`: La orquestación técnica, el motor Gunicorn y dependencias requeridas para la nube.
* `assets/`: Hojas de estilo CSS que garantizan responsividad y el diseño de la cuadrícula.
* `data/`: Insumos primarios e instrumentos cartográficos (.geojson y .xlsx).

## Instalación y ejecución local
1. Asegurar poseer Python 3.9 o superior instalado.
2. Clonar localmente el repositorio mediante el terminal de comandos: `git clone <tu-repositorio>`
3. Ingresar al entorno local: `cd <tu-repositorio>`
4. Proveer las bibliotecas: `pip install -r requirements.txt`
5. Levantar el servidor: `python app.py` y visualizar en `http://127.0.0.1:8050/`.

## Despliegue público (Railway)
Esta herramienta es accesible públicamente sin interrupciones gracias al hospedaje en Railway. El despliegue automático lee el archivo `Procfile` que delega el procesamiento hacia un servidor asíncrono Gunicorn, garantizando una latencia óptima.

## Principales conclusiones
* Existe una brecha fatal de género irrefutable, denominada sobremortalidad masculina, con alta incidencia visual en las barras apiladas departamentales.
* El fallo del sistema cardiovascular humano continúa acaparando el primer escaño de mortalidad a nivel global en el país.
* Existe una concentración alarmante en núcleos urbanos muy específicos de muertes provocadas por agresión con disparo (Código X95), lo cual requiere una lectura más ligada a políticas de seguridad social.

**Entorno tecnológico:** Python 3 | Pandas | Dash | Plotly | Gunicorn | Railway Cloud