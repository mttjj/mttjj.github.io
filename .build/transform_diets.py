import os
import re
import utils
import markdown
from datetime import date
from datetime import datetime
from calendar import month_name
from collections import defaultdict
from configuration import config

logger = config.logger

DATE_PATTERN = re.compile(r"# (\d{4}-\d{2}-\d{2}):")
MEDIA_PATTERN = re.compile(r"\[\[(.*?)\]\]")


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
                if (
                    parent_dir.isdigit() and len(parent_dir) == 4
                ):  # Verify parent is a year
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
            with open(index_file_path, "w", encoding="utf-8") as f:
                f.write(
                    f"""+++
date = "{frontmatter_date}"
layout = "{layout}"
title = "{title}"
+++"""
                )

            logger.debug(f"Created file: {index_file_path}")


def transform_diet_pages(directory):
    """
    Recursively traverses a directory, modifies markdown files by removing and adding text, and ensures idempotency.

    Args:
        directory: The root directory to start traversal.
    """
    for root, _, files in os.walk(directory):
        for file in [f for f in files if f.endswith(".md")]:
            file_path = os.path.join(root, file)

            try:
                # Read file content at once
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Skip if already processed
                if content.startswith("+++"):
                    logger.debug(f"Skipping already processed file: {file_path}")
                    continue

                lines = content.splitlines()
                if len(lines) < 2:
                    logger.debug(f"Skipping file with insufficient lines: {file_path}")
                    continue

                # Extract date
                date_match = DATE_PATTERN.search(lines[0])
                if not date_match:
                    logger.debug(f"Skipping file with invalid date format: {file_path}")
                    continue

                date_str = date_match.group(1)
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_title = date_obj.strftime("%-d %B %Y (%A)")

                # Process media items
                media_dict = defaultdict(set)  # Using set for unique items
                for line in lines[2:]:
                    matches = MEDIA_PATTERN.findall(line)
                    if len(matches) == 2:
                        media_type, media_item = matches
                        media_type = utils.get_taxonomy(media_type)
                        media_dict[media_type].add(utils.sanitize(media_item).lower())

                # Build front matter using list comprehension and join
                front_matter_lines = [
                    "+++",
                    f'date = "{date_str}"',
                    f'title = "{formatted_title}"',
                    'layout = "daily-diet"',
                ]

                front_matter_lines.extend(
                    f'{media_type} = [{", ".join(f""""{item}\"""" for item in sorted(items))}]'
                    for media_type, items in sorted(media_dict.items())
                )

                front_matter = "\n".join(front_matter_lines) + "\n+++\n\n"

                # Clean content and convert to HTML
                cleaned_content = clean_and_format_content(file_path, lines[2:])

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"{front_matter}{cleaned_content}")

                logger.debug(f"Processed file: {file_path}")

            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")


def process_media_links(text):
    """
    Process custom media links in the format [[type]]:[[item]] to HTML links.

    Args:
        text: String containing markdown content with custom media links

    Returns:
        String with media links converted to HTML
    """

    def replace_media_link(match):
        full_text = match.group(0)
        parts = MEDIA_PATTERN.findall(full_text)

        if len(parts) == 2:
            media_type, media_item = parts
            taxonomy = utils.get_taxonomy(media_type)
            sanitized_item = utils.sanitize(media_item).lower()

            return (
                f'{media_type}: <a href="/{taxonomy}/{sanitized_item}">{media_item}</a>'
            )
        return full_text

    # Pattern to match [[type]]:[[item]] pattern
    pattern = r"\[\[(.*?)\]\]:\s*\[\[(.*?)\]\]"
    return re.sub(pattern, replace_media_link, text)


def add_css_classes(html):
    """
    Add CSS classes to top-level list items that contain media links.

    Args:
        html: HTML string to process

    Returns:
        HTML with CSS classes added to appropriate list items
    """
    # Pattern to find <li> elements with media links
    pattern = r'<li>(.*?<a href="/([^"]+)/([^"]+)".*?)'

    def add_class(match):
        content = match.group(1)
        taxonomy = match.group(2)
        return f'<li class="entry {taxonomy}">{content}'

    return re.sub(pattern, add_class, html)


def clean_and_format_content(file_path, content_lines):
    """
    Process content lines to create HTML using the markdown library.

    Args:
        file_path: Path to the file being processed
        content_lines: List of strings to process

    Returns:
        String with fully processed HTML content
    """
    # Join the content lines
    content = "\n".join(content_lines)

    if "\\<no entries\\>" in content:
        return "<p>&lt;no entries&gt;</p>"

    # Process custom media links before markdown conversion
    content = process_media_links(content)

    # Convert markdown to HTML
    html = markdown.markdown(content, extensions=["extra"], tab_length=2)

    # Add CSS classes to list items with media links
    html = add_css_classes(html)

    return html


if __name__ == "__main__":
    directory = config.paths.media_diet_source

    logger.info("Renaming diet pages")
    rename_diet_pages(directory)

    logger.info("Creating index files")
    create_index_files(directory)

    logger.info("Transforming diet pages")
    transform_diet_pages(directory)
