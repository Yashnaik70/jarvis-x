import base64
import io
import os
import tempfile
from typing import Any

from gtts import gTTS

class VoiceSystem:
    def __init__(self):
        self.active = True
        self.wake_word = "jarvis"

    def get_status(self) -> dict:
        return {
            "active": self.active,
            "wake_word": self.wake_word,
            "description": "Local voice system with basic STT and TTS integration.",
            "features": ["stt", "tts", "wake_word_detection"]
        }

    def wake_word_detected(self, phrase: str) -> bool:
        return phrase.strip().lower().startswith(self.wake_word)

    def transcribe_audio(self, audio_base64: str) -> dict:
        try:
            # Import locally to avoid optional dependency failures at startup
            try:
                import speech_recognition as sr
            except ModuleNotFoundError:
                return {"status": "error", "message": "Speech recognition library not installed."}

            audio_bytes = base64.b64decode(audio_base64)
            audio_stream = io.BytesIO(audio_bytes)
            recognizer = sr.Recognizer()
            # speech_recognition expects a real file-like object; write to a temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            try:
                with sr.AudioFile(tmp_path) as source:
                    audio_data = recognizer.record(source)
                transcript = recognizer.recognize_google(audio_data)
                return {"status": "success", "text": transcript}
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
        except sr.UnknownValueError:
            return {"status": "error", "message": "Audio could not be transcribed."}
        except sr.RequestError as exc:
            return {"status": "error", "message": f"Speech recognition service error: {exc}"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    def generate_speech(self, text: str, lang: str = "en") -> dict:
        temp_path = None
        try:
            tts = gTTS(text=text, lang=lang)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                temp_path = tmp_file.name
            tts.save(temp_path)
            with open(temp_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            return {"status": "success", "audio_base64": audio_base64, "content_type": "audio/mpeg"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    def interpret_command(self, text: str) -> str:
        if self.wake_word_detected(text):
            return text[len(self.wake_word):].strip()
        return text
