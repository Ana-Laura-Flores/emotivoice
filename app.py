from fastapi import FastAPI, UploadFile, File, HTTPException
import numpy as np
from pydantic import BaseModel
import librosa
import joblib
import os
from fastapi.responses import JSONResponse
import parselmouth
from parselmouth.praat import call

app = FastAPI()

# Cargar el modelo previamente entrenado
model = joblib.load("modelos/modelo_emociones.pkl")

# Definir la clase para la respuesta de predicción
class PredictionResponse(BaseModel):
    emotion: str

def get_audio_features(y, sr):
    features = {}

    try:
        # Frecuencia de muestreo y duración
        features['frecuencia_muestreo'] = sr
        features['duracion'] = librosa.get_duration(y=y, sr=sr)

        # Amplitud máxima y mínima
        features['amplitud_maxima'] = np.max(np.abs(y))
        features['amplitud_minima'] = np.min(np.abs(y))

        # Tasa de cruce por cero
        features['tasa_cruce_cero'] = np.mean(librosa.feature.zero_crossing_rate(y)[0])

        # Características Chroma
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        features['chroma_stft'] = np.mean(chroma, axis=1)

        # MFCC
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features['mfcc'] = np.mean(mfcc, axis=1)

        # Valor RMS
        features['valor_rms'] = np.mean(librosa.feature.rms(y=y))

        # Entropía espectral
        spectral_entropy = -np.sum(np.square(np.abs(y)) * np.log(np.square(np.abs(y)) + 1e-10))
        features['entropia_espectral'] = spectral_entropy

        # Frecuencia fundamental
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        features['frecuencia_fundamental'] = np.mean(pitches[pitches > 0])

        # Formantes (F1 y F2)
        # Aquí necesitarías una función específica para extraer formantes, puedes usar librosa o otra biblioteca.
        # Este es un ejemplo simple, asegúrate de implementar la extracción de formantes correctamente
        features['formante_f1'] = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        features['formante_f2'] = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))

        # HNR (Harmonicity)
        hnr = librosa.effects.hpss(y)[0]
        features['hnr'] = np.mean(hnr)

        # Mel espectrogramas
        mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
        features['mel_espectrograma'] = np.mean(mel_spectrogram, axis=1)

        # Frecuencia centroidal, rolloff, y bandwidth
        features['frecuencia_centroidal'] = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        features['rolloff'] = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85))
        features['bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
        features['flatness'] = np.mean(librosa.feature.spectral_flatness(y=y))

    except Exception as e:
        print(f"Error al extraer características: {e}")
        features = {key: None for key in features.keys()}

    return features

@app.post("/sentiment", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    try:
        # Crear el directorio temporal si no existe
        os.makedirs("temp_audio", exist_ok=True)

        # Guardar temporalmente el archivo cargado
        audio_path = f"temp_audio/{file.filename}"
        with open(audio_path, "wb") as buffer:
            buffer.write(await file.read())

        # Extraer características del audio
        y, sr = librosa.load(audio_path, sr=None)
        features = get_audio_features(y, sr)

        # Convertir las características a un formato numérico
        features_array = np.array([
            features['frecuencia_muestreo'],
            features['duracion'],
            features['frecuencia_fundamental'],
            features['amplitud_maxima'],
            features['amplitud_minima'],
            features['tasa_cruce_cero'],
            features['valor_rms'],
            features['entropia_espectral'],
            features['formante_f1'],
            features['formante_f2'],
            features['hnr'],
            features['frecuencia_centroidal'],
            features['rolloff'],
            features['bandwidth'],
            features['flatness'],
            # Agregar medias de Chroma y MFCC
            *features['chroma_stft'],  # Asegúrate de que esto sea un arreglo de un tamaño esperado
            *features['mfcc']           # Asegúrate de que esto sea un arreglo de un tamaño esperado
        ]).reshape(1, -1)

        # Verificar que las características sean correctas
        if features_array.shape[1] == 0:
            raise HTTPException(status_code=500, detail="No se extrajeron características válidas.")

        prediction = model.predict(features_array)

        # Mapear la predicción a la emoción correspondiente
        emotion_mapping = {0: "angry", 1: "disgust", 2: "fear", 3: "happy",  4: "neutral",  5: "sad",  6: "surprise"}
        predicted_emotion = emotion_mapping.get(prediction[0], "unknown")

        # Eliminar el archivo temporal
        os.remove(audio_path)

        return {"emotion": predicted_emotion}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la predicción: {str(e)}")
