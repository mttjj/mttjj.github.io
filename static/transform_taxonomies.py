import os
import shutil
from logger_config import logger
from directory_config import dir_media_source

def remove_unwanted_files(dir):
    """
    Recursively traverses a directory to delete directories and files based on conditions.

    :param dir: The root directory to start traversal.
    """
    unwanted_dirs = ["author", "comic-publisher", "radio"]
    unwanted_files = ["Book.md", "Comic.md", "Film.md", "Graphic Novel.md", "Live Theatre.md", "Manga.md", "TV.md", "Video Game.md"]

    for root, dirs, files in os.walk(dir, topdown=False):
        # Delete directories matching the specified names
        for dir_name in dirs:
            if dir_name in unwanted_dirs:
                dir_path = os.path.join(root, dir_name)
                shutil.rmtree(dir_path)
                logger.debug(f"Deleted directory: {dir_path}")

        # Delete files matching the specified names or containing "#~list" on the second line
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # Check if the file name matches
            if file_name in unwanted_files:
                os.remove(file_path)
                logger.debug(f"Deleted file: {file_path}")
                continue

            # Check if "#~list" is on the second line of the file
            if file_name.endswith(".md"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        lines = file.readlines()
                        if len(lines) > 1 and "#~list" in lines[1]:
                            os.remove(file_path)
                            logger.debug(f"Deleted file due to '#list' on second line: {file_path}")
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")

def create_taxonomies(dir):
    """
    Traverses through a directory (not recursively) and renames directories based on a dictionary.

    :param dir: The root directory to traverse.
    """
    taxonomy_names = {"book": "books", "comic": "comics", "film": "films", "graphic-novel": "graphic-novels", "video-game": "video-games"}
    if os.path.exists(dir):
        for item in os.listdir(dir):
            item_path = os.path.join(dir, item)

            # Check if the item is a directory and if its name is in the rename dictionary
            if os.path.isdir(item_path) and item in taxonomy_names:
                new_name = taxonomy_names[item]
                new_path = os.path.join(dir, new_name)

                # Rename the directory
                os.rename(item_path, new_path)
                logger.debug(f"Renamed directory: {item_path} to {new_path}")

def transform_taxonomy_term_file_contents(dir):
    """
    Recursively traverses a directory, modifies markdown files by removing and adding text, and updates their content.

    :param dir: The root directory to start traversal.
    """
    for root, _, files in os.walk(dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    # Check if the file already contains the front matter block
                    if lines and lines[0].strip() == "+++":
                        logger.debug(f"Skipping already processed file: {file_path}")
                        continue

                    # Ensure there are enough lines to process
                    if len(lines) < 2:
                        logger.debug(f"Skipping file with insufficient lines: {file_path}")
                        continue

                    # Extract the first line (title) and remove the first two lines
                    first_line = lines[0].strip()
                    remaining_lines = lines[2:]

                    # Remove '[' and ']' from the remaining lines
                    cleaned_lines = [line.replace("[", "").replace("]", "") for line in remaining_lines if "#quote" not in line]

                    # Create the front matter block
                    title = first_line[1:].strip() if len(first_line) > 0 else ""
                    front_matter = f"+++\ntitle = \"{title}\"\n+++\n\n"

                    # Write the updated content back to the file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(front_matter)
                        f.write("\n".join(cleaned_lines))

                    logger.debug(f"Processed file: {file_path}")
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")

def create_taxonomy_term_structure(dir):
    """
    Recursively traverses a directory, organizes markdown files, and skips files based on the provided names.

    :param dir: The root directory to start traversal.
    """
    index_file_name = "_index.md"

    for root, _, files in os.walk(dir):
        for file in files:
            if file.endswith(".md") and file != index_file_name:
                # Full path to the current file
                file_path = os.path.join(root, file)

                # Directory name based on the markdown file (excluding extension)
                dir_name = os.path.splitext(file)[0]

                # Create the new directory in the same location as the markdown file
                new_dir_path = os.path.join(root, dir_name)
                os.makedirs(new_dir_path, exist_ok=True)

                # Move and rename the markdown file to the new directory
                new_file_path = os.path.join(new_dir_path, index_file_name)
                shutil.move(file_path, new_file_path)

                logger.debug(f"Moved and renamed {file_path} to {new_file_path}")

if __name__ == "__main__":
    directory = dir_media_source

    logger.info(">>>Removing unwanted files")
    remove_unwanted_files(directory)
    logger.info("<<<")

    logger.info(">>>Creating taxonomies")
    create_taxonomies(directory)
    logger.info("<<<")

    logger.info(">>>Transforming files")
    transform_taxonomy_term_file_contents(directory)
    logger.info("<<<")

    logger.info(">>>Creating file structure")
    create_taxonomy_term_structure(directory)
    logger.info("<<<")