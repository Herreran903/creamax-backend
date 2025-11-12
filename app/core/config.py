from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    BASE_URL: str
    PRUSA_SLICER_BIN: str
    SLICER_PROFILE_PATH: str
    SLICE_TIMEOUT_SEC: int = 300
    MAX_UPLOAD_MB: int = 200
    TMP_DIR: str

    class Config:
        env_file = ".env"

settings = Settings()
