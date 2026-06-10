from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "JARVIS-X"
    host: str = "127.0.0.1"
    port: int = 8000
    environment: str = "development"
    jarvisx_api_key: str | None = None
    serpapi_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()
