pip install SpeechRecognition googletrans==4.0.0-rc1 pyttsx3 pyaudio


import streamlit as st
import speech_recognition as sr
from googletrans import Translator
import pyttsx3
import tempfile
import os

# Initialize Translator & TTS
translator = Translator()
tts_engine = pyttsx3.init()

# Streamlit UI
st.title("🎤 INTRAAAA PADAALIIIIII")

st.write("Click on this button to get into the world of Pantherrrrr")

# Speech Recognition
recognizer = sr.Recognizer()

if st.button("🎙 Start Recording"):
    with sr.Microphone() as source:
        st.write("Listening... Speak in Telugu now.")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            st.write("Processing speech...")

            # Recognize Telugu speech
            telugu_text = recognizer.recognize_google(audio, language="te-IN")
            st.success(f"🗣 Telugu: {telugu_text}")

            # Translate to English
            translation = translator.translate(telugu_text, src="te", dest="en")
            english_text = translation.text
            st.success(f"✅ English Translation: {english_text}")

            # Speak out translation
            tts_engine.save_to_file(english_text, "translation.mp3")
            tts_engine.runAndWait()

            # Provide a download link for the translated speech
            st.audio("translation.mp3", format="audio/mp3")

        except sr.UnknownValueError:
            st.error("❌ Could not understand the audio. Please try again.")
        except sr.RequestError as e:
            st.error(f"⚠️ Speech recognition error: {e}")
        except Exception as e:
            st.error(f"❗ Error: {e}")
