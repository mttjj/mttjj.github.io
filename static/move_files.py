import os
import shutil
from logger_config import logger
from directory_config import *

def move_directories(source_dir, destination_dir):
    """
    Moves all top-level directories from the source directory to the destination directory.
    If directories or files already exist at the destination, they are overwritten.

    :param source_dir: The directory containing the directories to move.
    :param destination_dir: The directory to move the directories to.
    """
    # Ensure destination directory exists
    os.makedirs(destination_dir, exist_ok=True)

    # Iterate over items in the source directory
    if os.path.exists(source_dir):
        for item in os.listdir(source_dir):
            item_path = os.path.join(source_dir, item)

            if os.path.isdir(item_path):
                dest_path = os.path.join(destination_dir, item)

                # Remove the destination path if it already exists
                if os.path.exists(dest_path):
                    if os.path.isdir(dest_path):
                        shutil.rmtree(dest_path)
                    else:
                        os.remove(dest_path)

                # Move the directory
                shutil.move(item_path, dest_path)
                logger.debug(f"Moved: {item_path} -> {dest_path}")

if __name__ == "__main__":
    logger.info(">>>Moving taxonomies")
    move_directories(dir_media_source, dir_media_destination)
    if os.path.exists(dir_media_source):
        shutil.rmtree(dir_media_source)
    logger.info("<<<")

    logger.info(">>>Moving diet entries")
    move_directories(dir_media_diet_source, dir_media_diet_destination)
    if os.path.exists(dir_media_diet_source):
        shutil.rmtree(dir_media_diet_source)
    logger.info("<<<")