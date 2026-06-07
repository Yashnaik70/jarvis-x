from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "JARVIS-X"
    host: str = "127.0.0.1"
    port: int = 8000
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
