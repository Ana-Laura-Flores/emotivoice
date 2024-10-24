from fastapi import FastAPI, UploadFile, File, HTTPException
import librosa
import numpy as np
import joblib
import os
import parselmouth
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

app = FastAPI()

# Cargar el modelo previamente entrenado
model = joblib.load("modelos/modelo_emociones-02.pkl")

# Definir la clase para la respuesta de predicción
class PredictionResponse(BaseModel):
    emotion: str

# Crear directorio para archivos temporales si no existe
if not os.path.exists('temp_audio'):
    os.makedirs('temp_audio')

def convert_to_native(value):
    if isinstance(value, np.ndarray):
        return value.tolist()  # Convertir arreglos numpy a listas de Python
    elif isinstance(value, np.generic):
        return value.item()  # Convertir números numpy a números nativos de Python
    else:
        return value  # Devolver el valor si ya es compatible

# Función optimizada para obtener características del audio
def get_audio_features(y, sr, sound):
    features = {}
    try:
        # Frecuencia de muestreo y duración
        features['Frecuencia de muestreo'] = convert_to_native(sr)
        features['Duración (s)'] = convert_to_native(librosa.get_duration(y=y, sr=sr))
        # Amplitud máxima y mínima
        features['Amplitud Máxima'] = convert_to_native(np.max(np.abs(y)))
        features['Amplitud Mínima'] = convert_to_native(np.min(np.abs(y)))
        # Tasa de cruce por cero
        features['Tasa de Cruce por Cero'] = convert_to_native(np.mean(librosa.feature.zero_crossing_rate(y)[0]))
        # Valor RMS
        rms = librosa.feature.rms(y=y)
        features['Valor RMS'] = convert_to_native(np.mean(rms))
        # Entropía espectral
        spectral_entropy = -np.sum(np.square(np.abs(y)) * np.log(np.square(np.abs(y)) + 1e-10))
        features['Entropía Espectral'] = convert_to_native(spectral_entropy)
        # Frecuencia fundamental (pitch)
        pitch = sound.to_pitch()
        if pitch is not None and pitch.selected_array is not None:
            features['Frecuencia Fundamental (Hz)'] = convert_to_native(np.median(pitch.selected_array['frequency']))
        else:
            features['Frecuencia Fundamental (Hz)'] = None
        # Formantes (F1 y F2)
        formants = sound.to_formant_burg()
        if formants is not None:
            features['Formante F1 (Hz)'] = convert_to_native(formants.get_value_at_time(1, 0.5))
            features['Formante F2 (Hz)'] = convert_to_native(formants.get_value_at_time(2, 0.5))
        else:
            features['Formante F1 (Hz)'] = None
            features['Formante F2 (Hz)'] = None
        # Armónicos a ruido (HNR)
        harmonicity = sound.to_harmonicity_cc()
        if harmonicity is not None:
            harmonicity_values = harmonicity.values
            features['HNR (Harmonicity)'] = convert_to_native(np.mean(harmonicity_values)) if len(harmonicity_values) > 0 else None
        else:
            features['HNR (Harmonicity)'] = None
        # Mel espectogramas
        mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
        features['Mel espectogramas'] = convert_to_native(np.mean(mel_spectrogram))
        # Frecuencia Centroidal
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        features['Frecuencia Centroidal'] = convert_to_native(np.mean(spectral_centroid))
        # Rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        features['Rolloff'] = convert_to_native(np.mean(spectral_rolloff))
        # Bandwidth
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        features['Bandwidth'] = convert_to_native(np.mean(bandwidth))
        # Flatness
        flatness = librosa.feature.spectral_flatness(y=y)
        features['Flatness'] = convert_to_native(np.mean(flatness))
        # Añadir ceros adicionales
        features['0'] = 0

        print(f"Características: {features}")
    except Exception as e:
        print(f"Error al obtener características: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener características: {str(e)}")

    return features

@app.post("/sentiment")
async def predict(file: UploadFile = File(...)):
    try:
        # Guarda el archivo temporalmente
        audio_path = f"temp_audio/{file.filename}"
        with open(audio_path, "wb") as buffer:
            buffer.write(await file.read())

        # Intentar cargar el archivo de audio
        try:
            y, sr = librosa.load(audio_path, sr=None)
            sound = parselmouth.Sound(audio_path)
            print(f"Audio loaded. y: {y.shape}, sr: {sr}")

            if librosa.get_duration(y=y, sr=sr) <= 0.1:
                os.remove(audio_path)  # Elimina el archivo si la duración es muy corta
                raise HTTPException(status_code=400, detail="La duración del audio es demasiado corta.")

            # Extrae características
            features = get_audio_features(y, sr, sound)
            print(f"Características extraídas: {features}")

            # Seleccionar solo las características esperadas por el modelo (18 características)
            selected_features = [
                'Duración (s)',
                'Frecuencia Fundamental (Hz)',
                'Amplitud Máxima',
                'Tasa de Cruce por Cero',
                'Valor RMS',
                'Entropía Espectral',
                'Formante F1 (Hz)',
                'Formante F2 (Hz)',
                'HNR (Harmonicity)',
                'Mel espectogramas',
                'Frecuencia Centroidal',
                'Rolloff',
                'Bandwidth',
                'Flatness'
                
            ]

            features_array = np.array([features[feature] for feature in selected_features]).reshape(1, -1)
            print(f"Características preparadas para el modelo: {features_array}")

            # Verificar que las características sean correctas
            if features_array.shape[1] != 14:
                raise HTTPException(status_code=500, detail="No se extrajeron características válidas.")

            # Predicción del modelo
            prediction = model.predict(features_array)
            predicted_label = prediction[0]
            print(f"Predicción: {predicted_label}")
            
            # Imprimir las clases del modelo
            print(f"Clases del modelo: {model.classes_}")

            # Mapear la predicción a la emoción correspondiente
            emotion_mapping = {0: "angry", 1: "disgust", 2: "fear", 3: "happy", 4: "neutral", 5: "sad", 6: "surprise"}
            predicted_emotion = emotion_mapping.get(model.classes_.tolist().index(predicted_label), "unknown")
            print(f"Emoción predicha: {predicted_emotion}")

        except Exception as load_error:
            os.remove(audio_path)  # Elimina el archivo si hay un error
            print(f"Error al cargar el audio: {load_error}")
            raise HTTPException(status_code=400, detail=f"Error al cargar el audio: {str(load_error)}")

        # Elimina el archivo temporal
        os.remove(audio_path)
        return PredictionResponse(emotion=predicted_emotion)

    except Exception as e:
        print(f"Error en el procesamiento de la solicitud: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en el procesamiento de la solicitud: {str(e)}")