import streamlit as st
import requests
from PIL import Image
import base64

# Función para convertir imagen a base64
def image_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Dirección de la API de FastAPI (asegúrate de que tu FastAPI esté corriendo)
API_URL = "http://localhost:8000/sentiment"

# Ocultar Streamlit default style
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Añadir el logo y el título en la misma línea con CSS
logo_path = "images/emotivoice-logo.png"  # Reemplaza con la ruta de tu logo
logo_base64 = image_to_base64(logo_path)

# Estilos CSS para la interfaz
st.markdown(
    """
    <style>
        body {
            background-color: #F5F5F5;
            font-family: 'Arial', sans-serif;
        }
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: left;
            margin: 20px 0;
        }
        .logo {
            margin-right: 20px;
        }
        .title {
            color: #00BFFF;
            font-size: 35px;
            text-align: left;
            text-shadow: 1px 1px 2px #FFFFFF;
        }
        .subheader {
            color: #FF6347;
            font-size: 20px;
            text-align: center;
            margin: 10px 0;
        }
        .result {
            color: #4CAF50;
            font-size: 18px;
            text-align: center;
            margin-top: 20px;
        }
        .error {
            color: #FF6347;
            font-size: 18px;
            text-align: center;
            margin-top: 20px;
        }
        hr {
            border: 1px solid #E0E0E0;
        }
        footer {
            text-align: center;
            margin: 20px 0;
            color: #777;
        }
    </style>
    """, unsafe_allow_html=True
)

# Mostrar el logo y el título
st.markdown(
    f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{logo_base64}" alt="logo" width="100" class="logo">
        <h1 class="title">Análisis de emociones <br> a través de audio</h1>
    </div>
    """, unsafe_allow_html=True
)

# Subir archivo de audio
st.markdown("<h3 class='subheader'>🎵 Sube tu archivo de audio para analizar:</h3>", unsafe_allow_html=True)
audio_file = st.file_uploader("Sube tu archivo de audio", type=["wav", "mp3"], label_visibility="collapsed")

# Si se sube un archivo de audio, realizar la predicción
if audio_file is not None:
    # Guardar temporalmente el archivo en Streamlit
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_file.getbuffer())

    # Organizar audio y resultado en dos columnas
    col1, col2 = st.columns(2)

    with col1:
        # Mostrar reproductor de audio
        st.audio(audio_file, format="audio/wav")

    with col2:
        # Enviar archivo a la API FastAPI
        files = {"file": open("temp_audio.wav", "rb")}
        response = requests.post(API_URL, files=files)

        # Mostrar los resultados
        if response.status_code == 200:
            emotion = response.json().get("emotion")
            st.markdown(f"<h5 class='result'>😊 Emoción detectada: {emotion}</h5>", unsafe_allow_html=True)
        else:
            st.markdown("<h5 class='error'>❌ Ocurrió un error en la predicción</h5>", unsafe_allow_html=True)

# Pie de página personalizado
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>© 2024 - Proyecto de Análisis de Emociones</p>", unsafe_allow_html=True)
