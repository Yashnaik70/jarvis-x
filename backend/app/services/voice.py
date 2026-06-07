class VoiceSystem:
    def __init__(self):
        self.active = False
        self.wake_word = "jarvis"

    def get_status(self) -> dict:
        return {
            "active": self.active,
            "wake_word": self.wake_word,
            "description": "Placeholder voice system. Integrate STT/TTS providers for real voice control."
        }

    def wake_word_detected(self, phrase: str) -> bool:
        return phrase.strip().lower().startswith(self.wake_word)

    def transcribe_audio(self, audio_bytes: bytes) -> str:
        return ""  # TODO: integrate STT provider

    def speak_text(self, text: str) -> None:
        pass  # TODO: integrate TTS provider

    def interpret_command(self, text: str) -> str:
        if self.wake_word_detected(text):
            return text[len(self.wake_word):].strip()
        return text
