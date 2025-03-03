import os
import re
import utils
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

                # Clean content and write file
                cleaned_content = clean_and_format_content(file_path, lines[2:])

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"{front_matter}{cleaned_content}")

                logger.debug(f"Processed file: {file_path}")

            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")


def format_content_line(line, indent_level=0):
    """
    Formats a line by converting bracketed media type and item into an HTML link
    and adding appropriate list tags based on indentation.

    Args:
        line: String containing bracketed content
        indent_level: Current indentation level for nested lists

    Returns:
        Tuple of (formatted_html, is_list_item, new_indent_level)
    """
    # line = line.strip()
    if not line:
        return "", False, indent_level

    # Determine indentation level
    leading_spaces = len(line) - len(line.lstrip())
    current_indent = leading_spaces // 2  # Assuming 2 spaces per indent level

    logger.debug(
        f"Processing line: '{line}' with leading spaces: {leading_spaces}, calculated indent: {current_indent}"
    )

    # Check if it's a list item first
    is_list_item = line.lstrip().startswith("*")
    content = line.lstrip()

    if is_list_item:
        # Remove the asterisk and any following whitespace
        content = content[1:].strip()
        logger.debug(f"Found list item at indent {current_indent}: '{content}'")

    # Process brackets for media items
    matches = MEDIA_PATTERN.findall(content)
    if len(matches) == 2:
        media_type, media_item = matches
        taxonomy = utils.get_taxonomy(media_type)
        sanitized_item = utils.sanitize(media_item).lower()

        logger.debug(
            f"Found media item: type={media_type}, taxonomy={taxonomy}, item={media_item}"
        )

        # Replace the [[type]][[item]] pattern with the HTML link
        pattern = f"\\[\\[{media_type}\\]\\]:\\s*\\[\\[{re.escape(media_item)}\\]\\]"
        replacement = (
            f'{media_type}: <a href="/{taxonomy}/{sanitized_item}">{media_item}</a>'
        )
        content = re.sub(pattern, replacement, content).replace("\\", "")

        # Add CSS class only to media items (top-level list items)
        if is_list_item and current_indent == 0:
            css_class = "entry " + media_type
            content = f'<li class="{css_class}">{content}</li>'
            logger.debug("Added media-item class to top-level item")
        elif is_list_item:
            # Regular nested list item without special class
            content = f"<li>{content}</li>"
            logger.debug("Added regular li tag to nested item")
    else:
        # Regular content, just remove brackets
        content = content.replace("[", "").replace("]", "")
        if is_list_item:
            content = f"<li>{content}</li>"
            logger.debug("Added regular li tag to non-media list item")

    logger.debug(
        f"Returning: content='{content}', is_list_item={is_list_item}, indent={current_indent}"
    )
    return content, is_list_item, current_indent


def clean_and_format_content(file_path, content_lines):
    """
    Process content lines to create HTML with proper list nesting.

    Args:
        content_lines: List of strings to process

    Returns:
        String with fully processed HTML content
    """
    html_lines = []
    current_indent = 0
    list_open = False

    logger.debug(f"Starting to process {len(content_lines)} lines")

    for i, line in enumerate(content_lines):
        logger.debug(f"Line {i+1}: Processing '{line}'")
        formatted_line, is_list_item, line_indent = format_content_line(
            line, current_indent
        )

        if not formatted_line:
            logger.debug(f"Line {i+1}: Empty line, skipping")
            continue

        # Handle list opening/closing based on indentation
        if is_list_item:
            logger.debug(
                f"Line {i+1}: List item with indent {line_indent}, current indent {current_indent}"
            )

            # Need to open a new list
            if not list_open:
                html_lines.append("<ul>")
                list_open = True
                logger.debug(f"Line {i+1}: Opening new list")

            # Handle indentation changes for nested lists
            while line_indent > current_indent:
                html_lines.append("<ul>")
                current_indent += 1
                logger.debug(
                    f"Line {i+1}: Increasing indent to {current_indent}, adding <ul>"
                )

            while line_indent < current_indent:
                html_lines.append("</ul>")
                current_indent -= 1
                logger.debug(
                    f"Line {i+1}: Decreasing indent to {current_indent}, adding </ul>"
                )

            html_lines.append(formatted_line)
        else:
            logger.debug(f"Line {i+1}: Non-list item, closing any open lists")

            # Close any open lists
            while list_open:
                html_lines.append("</ul>")
                current_indent -= 1
                list_open = current_indent > -1
                logger.debug(
                    f"Line {i+1}: Closing list, new indent {current_indent}, list_open={list_open}"
                )

            html_lines.append(formatted_line)

    # Close any remaining open lists
    logger.debug(
        f"End of content, current_indent={current_indent}, closing any remaining lists"
    )
    while list_open:
        html_lines.append("</ul>")
        current_indent -= 1
        list_open = current_indent > -1
        logger.debug(f"Added closing </ul>, new indent {current_indent}")

    result = "\n".join(html_lines)
    logger.debug(f"Final HTML has {len(html_lines)} lines")

    # Count opening and closing ul tags as a sanity check
    open_tags = result.count("<ul>")
    close_tags = result.count("</ul>")
    balanced = open_tags == close_tags
    logger.debug(
        f"Tag count check: <ul>: {open_tags}, </ul>: {close_tags}, balanced: {balanced}"
    )

    if not balanced:
        logger.error(f"File has unbalanced list tags: {file_path}")

    return result


if __name__ == "__main__":
    directory = config.paths.media_diet_source

    logger.info("Renaming diet pages")
    rename_diet_pages(directory)

    logger.info("Creating index files")
    create_index_files(directory)

    logger.info("Transforming diet pages")
    transform_diet_pages(directory)
