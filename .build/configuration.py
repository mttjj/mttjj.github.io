import os
import logging
from datetime import datetime
from pathlib import Path

class Paths:
    bear_db = "/Users/matthew/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite"
    base_dir = os.path.dirname(os.path.abspath(__file__))

    import_dir = os.path.join(base_dir, "../import")
    content_dir = os.path.join(base_dir, "../content")
    logs_dir = os.path.join(base_dir, "logs")

    media_source = os.path.join(base_dir, "../import/media")
    media_destination = os.path.join(base_dir, "../content")
    media_diet_source = os.path.join(base_dir, "../import/media-diet")
    media_diet_destination = os.path.join(base_dir, "../content/media-diet")

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