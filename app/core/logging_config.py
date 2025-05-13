import logging
import sys
from pathlib import Path
from datetime import datetime

from app.core.config import DEBUG

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Current date for log filename
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = LOG_DIR / f"dms_{CURRENT_DATE}.log"

# Basic configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
    return logger