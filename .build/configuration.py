import os
import logging

class Path:
    base_dir = os.path.dirname(os.path.abspath(__file__))

    import_dir = os.path.join(base_dir, "../import")

    media_source = os.path.join(base_dir, "../import/media")
    media_destination = os.path.join(base_dir, "../content")
    media_diet_source = os.path.join(base_dir, "../import/media-diet")
    media_diet_destination = os.path.join(base_dir, "../content/media-diet")

class Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    instance = logging.getLogger(__name__)

class Config:
    path = Path()
    logger = Logger.instance

config = Config()