import streamlit as st
import requests
import base64
import time

# Función para convertir imagen a base64
def image_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Dirección de la API de FastAPI
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
        .intro-animation {
            text-align: center;
            margin-top: 50px;
        }
        .emotivoice-text {
            display: inline-block;
            font-size: 40px;
            color: #00BFFF;
            margin: 20px 0;
        }
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 20px;
        }
        .title {
            color: #00BFFF;
            font-size: 35px;
            margin-left: 20px;
        }
        .play-button-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
        }
        .play-button {
            background-color: #00BFFF;
            color: white;
            font-size: 20px;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
            border-radius: 5px;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True
)

# Variable de estado para controlar la introducción
if 'show_intro' not in st.session_state:
    st.session_state.show_intro = True
    st.session_state.audio_played = False  # Añadir estado para el audio

# Contenedor para la animación de introducción
if st.session_state.show_intro:
    intro_container = st.empty()
    intro_container.markdown(
        f"""
        <div class="intro-animation">
            <img src="data:image/png;base64,{logo_base64}" alt="Logo" width="200">
            <h1 class="emotivoice-text">EmotiVoice</h1>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Botón para reproducir la música
    play_button = st.empty()
    if play_button.button("Escucha nuestra canción", key="play_button"):
        st.session_state.audio_played = True
    
    if st.session_state.audio_played:
        audio_file = open("images/Emotivoice-.mp3", "rb").read()
        st.audio(audio_file, format="audio/mp3")

    # Esperar 5 segundos antes de mostrar el contenido
    time.sleep(5)
    # Limpiar el contenedor de introducción
    intro_container.empty()
    play_button.empty()  # Limpiar el botón de reproducción
    # Desactivar la introducción para futuras cargas
    st.session_state.show_intro = False

# Mostrar el resto del contenido
st.markdown(
    f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{logo_base64}" alt="logo" width="100" class="logo">
        <h1 class="title">Análisis de emociones <br> a través de audio</h1>
    </div>
    """, unsafe_allow_html=True
)

# Subir archivo de audio
st.markdown("<h3 class='subheader'> Sube tu archivo de audio para analizar:</h3>", unsafe_allow_html=True)
audio_file_upload = st.file_uploader("Sube tu archivo de audio", type=["wav", "mp3"], label_visibility="collapsed")

# Si se sube un archivo de audio, realizar la predicción
if audio_file_upload is not None:
    # Guardar temporalmente el archivo en Streamlit
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_file_upload.getbuffer())

    # Organizar audio y resultado en dos columnas
    col1, col2 = st.columns(2)

    with col1:
        # Mostrar reproductor de audio
        st.audio(audio_file_upload, format="audio/wav")

    with col2:
        # Enviar archivo a la API FastAPI
        files = {"file": open("temp_audio.wav", "rb")}
        response = requests.post(API_URL, files=files)

        # Mostrar los resultados
        if response.status_code == 200:
            emotion = response.json().get("emotion")
            st.markdown(f"<h5 class='result'>✔️ Emoción detectada: {emotion}</h5>", unsafe_allow_html=True)
        else:
            st.markdown("<h5 class='error'>❌ Ocurrió un error en la predicción</h5>", unsafe_allow_html=True)

# Pie de página personalizado
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>© 2024 - Proyecto de Análisis de Emociones</p>", unsafe_allow_html=True)
