from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    WORKSPACE_DIR: Path = Path("workspace")
    MAX_SLIDES: int = 20
    MAX_CONTENT_LINES_PER_SLIDE: int = 10
    
    class Config:
        env_file = ".env"


settings = Settings()

# Create workspace directories on import
(settings.WORKSPACE_DIR / "input").mkdir(parents=True, exist_ok=True)
(settings.WORKSPACE_DIR / "slides").mkdir(parents=True, exist_ok=True)
(settings.WORKSPACE_DIR / "videos").mkdir(parents=True, exist_ok=True)
