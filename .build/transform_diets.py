import os
import re
import utils
from datetime import date
from datetime import datetime
from calendar import month_name
from collections import defaultdict
from configuration import config

logger = config.logger

def rename_diet_pages(dir):
    """
    Recursively traverses a directory, renames markdown files based on the 9th and 10th
    characters of their current name, and ensures idempotency.

    :param dir: The root directory to start traversal.
    """
    for root, _, files in os.walk(dir):
        for file in files:
            if file.endswith(".md"):
                # Ensure the file name has at least 10 characters (excluding extension)
                if len(file) < 13:  # 10 for chars + 3 for ".md"
                    logger.debug(f"Skipping file with insufficient length: {file}")
                    continue

                # Extract the new name from the 9th and 10th characters
                new_name = file[8:10] + ".md"

                # Check if the current file name already matches the intended new name
                if file == new_name:
                    logger.debug(f"Skipping already renamed file: {file}")
                    continue

                # Rename the file
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, new_name)

                if not os.path.exists(new_path):
                    os.rename(old_path, new_path)
                    logger.debug(f"Renamed {old_path} to {new_path}")
                else:
                    logger.debug(f"Skipping rename, target file exists: {new_path}")

def create_index_files(dir):
    """
    Recursively traverses a directory and creates a `_index.md` file in each directory.

    The frontmatter will be:
      - For year directories: date = <first day of year>, layout = "year", title = <year>
      - For month directories: date = <first day of month>, layout = "month", title = <Month Year>

    :param dir: The root directory to start traversal.
    """
    for root, dirs, _ in os.walk(dir):
        for directory in dirs:
            dir_path = os.path.join(root, directory)
            index_file_path = os.path.join(dir_path, "_index.md")

            # Check if the directory name is a year
            if directory.isdigit() and len(directory) == 4:
                year = int(directory)
                frontmatter_date = date(year, 1, 1).isoformat()
                layout = "year"
                title = directory

            # Check if the directory name is a month number
            elif directory.isdigit() and 1 <= int(directory) <= 12:
                parent_dir = os.path.basename(os.path.dirname(dir_path))
                if parent_dir.isdigit() and len(parent_dir) == 4:  # Verify parent is a year
                    month = int(directory)
                    year = int(parent_dir)
                    frontmatter_date = date(year, month, 1).isoformat()
                    layout = "month"
                    title = f"{month_name[month]} {year}"
                else:
                    continue
            else:
                continue

            # Ensure idempotency
            if os.path.exists(index_file_path):
                logger.debug(f"Skipping existing file: {index_file_path}")
                continue

            # Write the `_index.md` file
            with open(index_file_path, 'w', encoding='utf-8') as f:
                f.write(f"""+++
date = "{frontmatter_date}"
layout = "{layout}"
title = "{title}"
+++""")

            logger.debug(f"Created file: {index_file_path}")

def transform_diet_pages(dir):
    """
    Recursively traverses a directory, modifies markdown files by removing and adding text, and ensures idempotency.

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

                    # Extract the date from the first line (format: "# 2025-01-04: Saturday")
                    first_line = lines[0].strip()
                    date_match = re.search(r"# (\d{4}-\d{2}-\d{2}):", first_line)
                    if not date_match:
                        logger.debug(f"Skipping file with invalid date format: {file_path}")
                        continue

                    date_str = date_match.group(1)
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    formatted_title = date_obj.strftime("%-d %B %Y (%A)")  # e.g., "4 January 2025 (Saturday)"

                    remaining_lines = lines[2:]

                    # Initialize a dictionary to hold media types and their items
                    media_dict = defaultdict(list)

                    # Process each remaining line for media types and items
                    for line in remaining_lines:
                        matches = re.findall(r"\[\[(.*?)\]\]", line)
                        if len(matches) == 2:
                            media_type, media_item = matches

                            # Map media type to replacement text if it exists
                            media_type = utils.get_taxonomy(media_type)
                            media_dict[media_type].append(media_item)

                    # Create the front matter block
                    front_matter = f"""+++
date = "{date_str}"
title = "{formatted_title}"
layout = "daily-diet"
"""

                    for media_type, media_items in media_dict.items():
                        media_items_str = ", ".join(f'"{utils.sanitize(item).lower()}"' for item in media_items)
                        front_matter += f"{media_type} = [{media_items_str}]\n"

                    front_matter += "+++\n\n"

                    # Remove '[' and ']' from the remaining lines
                    cleaned_lines = [line.replace("[", "").replace("]", "") for line in remaining_lines]

                    # Write the updated content back to the file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(front_matter)
                        f.writelines(cleaned_lines)

                    logger.debug(f"Processed file: {file_path}")
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {e}")

if __name__ == "__main__":
    directory = config.paths.media_diet_source

    logger.info("Renaming diet pages")
    rename_diet_pages(directory)

    logger.info("Creating index files")
    create_index_files(directory)

    logger.info("Transforming diet pages")
    transform_diet_pages(directory)