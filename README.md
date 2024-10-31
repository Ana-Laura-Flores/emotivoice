# Emotivoice

Emotivoice es una aplicación diseñada para analizar las emociones en archivos de audio. Utilizando tecnologías avanzadas de procesamiento de señales y aprendizaje automático, Emotivoice detecta y clasifica las emociones presentes en la voz del hablante.

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Requisitos](#requisitos)
3. [Guía de Usuario](#guía-de-usuario)
4. [API Documentation](#api-documentation)
5. [Guía de Desarrollo](#guía-de-desarrollo)
6. [Pruebas](#pruebas)
7. [Mantenimiento](#mantenimiento)

## Introducción

### Descripción general de la aplicación
Emotivoice es una aplicación diseñada para analizar las emociones en archivos de audio. Utilizando tecnologías avanzadas de procesamiento de señales y aprendizaje automático, Emotivoice detecta y clasifica las emociones presentes en la voz del hablante.

### Funcionalidades principales
- **Carga de archivos de audio**: Permite a los usuarios subir archivos de audio para su análisis.
- **Detección de emociones**: Analiza el audio y predice la emoción predominante.
- **Interfaz interactiva**: Ofrece una interfaz amigable donde los usuarios pueden ver los resultados de la predicción.
- **API accesible**: Proporciona una API RESTful para integraciones con otras aplicaciones.

## Requisitos

### Requisitos de hardware y software
- **Sistema Operativo**: Windows, macOS o Linux.
- **RAM**: Mínimo 4GB.
- **Espacio en disco**: Mínimo 500MB para la instalación de dependencias.
- **Python**: Versión 3.8 o superior.

### Instalación de dependencias
1. **Clona el repositorio**:
```sh
git clone https://github.com/Ana-Laura-Flores/emotivoice
```
 
  2. **Crea un entorno virtual**:
```sh
python3 -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
```
 3. **Instala dependencias requeridas**:
  
```sh
pip install -r requirements.txt
```

## Guía de Usuario

### Cómo usar la aplicación paso a paso
### Inicia la aplicación:
```sh
streamlit run app.py
```

#### Reproduce la música de introducción:
Haz clic en "Escucha nuestra canción".

### Carga un archivo de audio:
Utiliza el botón "Sube tu archivo de audio" para seleccionar un archivo .wav o .mp3.


### Visualiza los resultados:
Una vez procesado el audio, la emoción detectada se mostrará en la interfaz.


## API Documentation
### Endpoints disponibles
POST /sentiment: Recibe un archivo de audio y devuelve la emoción detectada.

### Formato de solicitudes y respuestas
```sh
import requests

url = "http://localhost:8000/sentiment"
files = {"file": open("path_to_your_audio_file", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## Guía de Desarrollo

### Estructura del código

- **app.py**: Archivo principal de la aplicación.
- **modelos/**: Directorio que contiene el modelo de Machine Learning.
- **images/**: Recursos estáticos como imágenes y CSS.


### Cómo agregar nuevas funcionalidades

1. Añade nuevas rutas en FastAPI en `app.py`.
2. Implementa la lógica de la nueva funcionalidad en los controladores.
3. Actualiza  el archivo `front_streamlit.py` si es necesario para reflejar los cambios en la interfaz.
## Pruebas
### Descripción de las pruebas realizadas
Pruebas unitarias: Para validar funciones individuales.

Pruebas de integración: Para asegurar que los diferentes componentes funcionen juntos correctamente.

## ¡Gracias por utilizar Emotivoice!

No dudes en **contribuír** o **reportar problemas** en el repositorio.
