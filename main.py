# # from kivy.app import App
# # from kivy.uix.boxlayout import BoxLayout
# # from kivy.uix.label import Label
# # from kivy.uix.button import Button
# # from kivy.uix.textinput import TextInput
# # import speech_recognition as sr
# # from googletrans import Translator
# # import pyttsx3
# # import threading

# # class TranslatorApp(BoxLayout):
# #     def __init__(self, **kwargs):
# #         super().__init__(orientation='vertical', **kwargs)
# #         self.label = Label(text="🎤 Press the button and speak in Telugu")
# #         self.add_widget(self.label)

# #         self.button = Button(text="Start Listening")
# #         self.button.bind(on_press=self.start_listening)
# #         self.add_widget(self.button)

# #         self.result_label = Label(text="Translation: ")
# #         self.add_widget(self.result_label)

# #         self.recognizer = sr.Recognizer()
# #         self.translator = Translator()
# #         self.tts_engine = pyttsx3.init()

# #     def start_listening(self, instance):
# #         threading.Thread(target=self.process_speech).start()

# #     def process_speech(self):
# #         with sr.Microphone() as source:
# #             self.label.text = "🎤 Listening..."
# #             self.recognizer.adjust_for_ambient_noise(source)
# #             audio = self.recognizer.listen(source)

# #         try:
# #             telugu_text = self.recognizer.recognize_google(audio, language="te-IN")
# #             self.label.text = f"🗣 Telugu: {telugu_text}"

# #             # Translate to English
# #             translation = self.translator.translate(telugu_text, src="te", dest="en").text
# #             self.result_label.text = f"✅ English: {translation}"

# #             # Speak out translation
# #             self.tts_engine.say(translation)
# #             self.tts_engine.runAndWait()

# #         except sr.UnknownValueError:
# #             self.label.text = "❌ Could not understand the audio."
# #         except sr.RequestError as e:
# #             self.label.text = f"⚠️ Speech recognition error: {e}"

# # class TranslatorAppMain(App):
# #     def build(self):
# #         return TranslatorApp()

# # if __name__ == '__main__':
# #     TranslatorAppMain().run()









# from kivy.app import App
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.button import Button
# from kivy.uix.label import Label
# from kivy.clock import Clock
# from kivy.core.audio import SoundLoader
# import speech_recognition as sr
# from googletrans import Translator
# import threading
# import os
# import tempfile
# from gtts import gTTS  # Using gTTS instead of pyttsx3 for Android compatibility

# class TranslatorApp(App):
#     def build(self):
#         self.recognizer = sr.Recognizer()
#         self.translator = Translator()
#         self.is_listening = False
#         self.temp_audio_file = os.path.join(tempfile.gettempdir(), "translation.mp3")
        
#         # Create UI layout
#         layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
#         # Status labels
#         self.status_label = Label(
#             text="Press the button to start listening",
#             font_size='18sp',
#             halign='center',
#             size_hint=(1, 0.2)
#         )
        
#         self.telugu_text_label = Label(
#             text="Telugu text will appear here",
#             font_size='16sp',
#             halign='center',
#             size_hint=(1, 0.3)
#         )
        
#         self.english_text_label = Label(
#             text="English translation will appear here",
#             font_size='16sp',
#             halign='center',
#             size_hint=(1, 0.3)
#         )
        
#         # Listen button
#         self.listen_button = Button(
#             text="Start Listening",
#             font_size='20sp',
#             size_hint=(1, 0.2),
#             background_color=(0.2, 0.7, 0.3, 1)
#         )
#         self.listen_button.bind(on_press=self.toggle_listening)
        
#         # Add widgets to layout
#         layout.add_widget(Label(text="Telugu to English Translator", font_size='24sp', size_hint=(1, 0.2)))
#         layout.add_widget(self.status_label)
#         layout.add_widget(self.telugu_text_label)
#         layout.add_widget(self.english_text_label)
#         layout.add_widget(self.listen_button)
        
#         return layout
    
#     def toggle_listening(self, instance):
#         if not self.is_listening:
#             self.is_listening = True
#             self.listen_button.text = "Stop Listening"
#             self.listen_button.background_color = (0.8, 0.2, 0.2, 1)
#             self.status_label.text = "Listening..."
#             # Start listening in a separate thread to avoid freezing UI
#             threading.Thread(target=self.start_listening).start()
#         else:
#             self.is_listening = False
#             self.listen_button.text = "Start Listening"
#             self.listen_button.background_color = (0.2, 0.7, 0.3, 1)
#             self.status_label.text = "Stopped listening"
    
#     def start_listening(self):
#         try:
#             with sr.Microphone() as source:
#                 Clock.schedule_once(lambda dt: self.update_status("Adjusting for noise..."), 0)
#                 self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
#                 while self.is_listening:
#                     try:
#                         Clock.schedule_once(lambda dt: self.update_status("Listening for Telugu speech..."), 0)
#                         audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        
#                         Clock.schedule_once(lambda dt: self.update_status("Processing speech..."), 0)
#                         telugu_text = self.recognizer.recognize_google(audio, language="te-IN")
                        
#                         # Update telugu text on UI thread
#                         Clock.schedule_once(lambda dt: self.update_telugu_text(telugu_text), 0)
                        
#                         # Translate to English
#                         translation = self.translator.translate(telugu_text, src="te", dest="en")
#                         english_text = translation.text
                        
#                         # Update english text on UI thread
#                         Clock.schedule_once(lambda dt: self.update_english_text(english_text), 0)
                        
#                         # Create audio file for playback
#                         tts = gTTS(text=english_text, lang='en')
#                         tts.save(self.temp_audio_file)
                        
#                         # Play audio on UI thread
#                         Clock.schedule_once(lambda dt: self.play_translation(), 0)
                        
#                     except sr.UnknownValueError:
#                         Clock.schedule_once(lambda dt: self.update_status("Could not understand audio"), 0)
#                     except sr.RequestError as e:
#                         Clock.schedule_once(lambda dt: self.update_status(f"Speech recognition error: {e}"), 0)
#                     except Exception as e:
#                         Clock.schedule_once(lambda dt: self.update_status(f"Error: {e}"), 0)
#         except Exception as e:
#             Clock.schedule_once(lambda dt: self.update_status(f"Microphone error: {e}"), 0)
    
#     def update_status(self, text):
#         self.status_label.text = text
    
#     def update_telugu_text(self, text):
#         self.telugu_text_label.text = f"Telugu: {text}"
    
#     def update_english_text(self, text):
#         self.english_text_label.text = f"English: {text}"
    
#     def play_translation(self):
#         sound = SoundLoader.load(self.temp_audio_file)
#         if sound:
#             sound.play()

# if __name__ == "__main__":
#     TranslatorApp().run()





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
