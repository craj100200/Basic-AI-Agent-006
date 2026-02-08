import sys
from pathlib import Path
from loguru import logger
from app.config import settings

# Remove default handler
logger.remove()

# Add custom handler
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.DEBUG else "INFO"
)

# Optional: Add file logging (create logs dir first)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger.add(
    log_dir / "app.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO"
)
