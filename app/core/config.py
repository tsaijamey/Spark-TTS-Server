from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # FastAPI/Uvicorn Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Security
    API_KEY: str
    
    # Spark-TTS Configuration
    SPARK_TTS_ROOT_DIR: str  # 新增配置项
    SPARK_TTS_MODEL_DIR: str
    SPARK_TTS_DEVICE: str = "0"
    
    # File Management
    GENERATED_AUDIO_DIR: str = "./generated_audio"
    MAX_PROMPT_SIZE_MB: float = 1.0
    AUDIO_BASE_URL: str = ""
    
    # Prompt Defaults
    DEFAULT_PROMPT_SPEECH_PATH: str = ""
    DEFAULT_PROMPT_TEXT: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()