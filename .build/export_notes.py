import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from configuration import config

logger = config.logger


def create_directories(base_dir, tag_path):
    """Create nested directories from tag path if they don't exist"""
    try:
        full_path = os.path.join(base_dir, tag_path)
        Path(full_path).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory structure for: {full_path}")
        return full_path
    except Exception as e:
        logger.error(f"Failed to create directory {full_path}: {str(e)}")
        raise


def sanitize_filename(filename):
    """Remove or replace invalid filename characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, " ")
    return filename


def export_notes_by_tag(target_tags, output_dir):
    logger.info(f"Starting note export process with {len(target_tags)} tags")
    logger.debug(f"Output directory: {output_dir}")

    for tag_path in target_tags:
        logger.debug(f"Processing tag: {tag_path}")
        full_path = create_directories(output_dir, tag_path)

        try:
            result = subprocess.run(
                [
                    config.paths.bear_cli,
                    "search",
                    "--query",
                    f"!#{tag_path}",
                    "--location",
                    "all",
                    "--format",
                    "json",
                    "--fields",
                    "title,content,location",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            notes = json.loads(result.stdout)
            if not isinstance(notes, list):
                raise ValueError("Expected bearcli search to return a JSON array")
            logger.debug(f"Found {len(notes)} notes for tag {tag_path}")
        except (
            OSError,
            subprocess.CalledProcessError,
            json.JSONDecodeError,
            ValueError,
        ) as e:
            logger.error(f"Failed to export notes for tag {tag_path}: {e}")
            raise

        for note in notes:
            if not isinstance(note, dict):
                raise ValueError(f"Invalid note returned for tag {tag_path}")

            location = note.get("location")
            if location == "trash":
                continue
            if location not in {"notes", "archive"}:
                raise ValueError(f"Invalid note location returned for tag {tag_path}")

            title = note.get("title")
            text = note.get("content")
            if isinstance(title, str) and title and isinstance(text, str) and text:
                safe_title = sanitize_filename(title)
                file_path = os.path.join(full_path, f"{safe_title}.md")

                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    logger.debug(f"Successfully exported note: {safe_title}")
                except IOError as e:
                    logger.error(f"Failed to write note {safe_title}: {str(e)}")
                    raise
            else:
                logger.warning(
                    f"Skipped note with missing title or content in tag {tag_path}"
                )

    logger.info("Note export process completed")


def generate_monthly_paths(year):
    # Convert year to string if it's passed as integer
    year_str = str(year)

    # Use list comprehension to create paths for all 12 months
    # zfill(2) ensures months are padded with leading zero if needed
    return [f"media-diet/{year_str}/{str(month).zfill(2)}" for month in range(1, 13)]


def main():
    output_dir = config.paths.import_dir
    current_year = datetime.now().year

    # List of tags to export (with their directory structure)
    tags_to_export = [
        "media/book",
        "media/comic",
        "media/film",
        "media/graphic-novel",
        "media/live-theatre",
        "media/manga",
        "media/tv-series",
        "media/video-game",
    ]
    for year in range(2011, current_year + 1):
        tags_to_export.extend(generate_monthly_paths(year))

    logger.debug(f"tags to export: {tags_to_export}")
    export_notes_by_tag(tags_to_export, output_dir)


if __name__ == "__main__":
    main()
