import os
import logging
from datetime import datetime
from pathlib import Path

class Paths:
    base_dir = Path(__file__).resolve().parent

    logs_dir = base_dir / "logs"

    bear_db = "/Users/matthew/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite"

    import_dir = base_dir / "../import"
    media_source = base_dir / import_dir / "media"
    media_diet_source = base_dir / import_dir / "media-diet"

    content_dir = base_dir / "../content"
    media_destination = content_dir
    media_diet_destination = base_dir / content_dir / "media-diet"

class Logger:
    """Configure logging to write to file and console"""
    # Create logs directory if it doesn't exist
    log_dir = Path(Paths.logs_dir)
    log_dir.mkdir(exist_ok=True)

    # Configure logging
    log_file = log_dir / f"git_operations_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also output to console
        ]
    )
    instance = logging.getLogger(__name__)

class Config:
    paths = Paths()
    logger = Logger.instance

config = Config()