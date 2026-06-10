import base64

from backend.app.services.voice import VoiceSystem


def test_transcribe_audio_invalid_base64():
    voice = VoiceSystem()
    result = voice.transcribe_audio("not-base64")
    assert result["status"] == "error"


def test_generate_speech_returns_base64(monkeypatch):
    class FakeTTS:
        def __init__(self, text, lang="en"):
            self.text = text
            self.lang = lang

        def save(self, path):
            with open(path, "wb") as f:
                f.write(b"FAKE_MP3")

    monkeypatch.setattr("backend.app.services.voice.gTTS", FakeTTS)
    voice = VoiceSystem()
    result = voice.generate_speech("Hello", lang="en")
    assert result["status"] == "success"
    assert result["content_type"] == "audio/mpeg"
    assert base64.b64decode(result["audio_base64"]) == b"FAKE_MP3"
