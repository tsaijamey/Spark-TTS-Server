from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pydantic import Field

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

    # 流媒体相关配置
    STREAM_BASE_URL: str = Field(
        default="/audio", 
        description="流媒体音频文件的基础URL"
    )

    @property
    def PROJECT_FILES_DIR(self) -> str:
        """获取项目文件的存储目录"""
        return os.path.join(os.getcwd(), "generated_audio")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    print(f"--- Loading Settings ---")
    print(f"Loaded API_KEY from env: {settings.API_KEY}")
    # 可以根据需要添加打印其他环境变量
    # print(f"Loaded SPARK_TTS_ROOT_DIR: {settings.SPARK_TTS_ROOT_DIR}")
    print(f"------------------------")
    return settings