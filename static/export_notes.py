import sqlite3
import os
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
        filename = filename.replace(char, ' ')
    return filename

def export_notes_by_tag(db_path, target_tags, output_dir):
    logger.debug(f"Starting note export process with {len(target_tags)} tags")
    logger.debug(f"Output directory: {output_dir}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        logger.debug(f"Successfully connected to database: {db_path}")
    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

    for tag_path in target_tags:
        logger.debug(f"Processing tag: {tag_path}")
        full_path = create_directories(output_dir, tag_path)

        try:
            query = """
            SELECT DISTINCT n.ZTITLE, n.ZTEXT
            FROM ZSFNOTE n
            JOIN Z_5TAGS nt ON n.Z_PK = nt.Z_5NOTES
            JOIN ZSFNOTETAG t ON nt.Z_13TAGS = t.Z_PK
            WHERE t.ZTITLE = ? AND n.ZTRASHED = 0
            """

            cursor.execute(query, (tag_path,))
            notes = cursor.fetchall()
            logger.debug(f"Found {len(notes)} notes for tag {tag_path}")

            for title, text in notes:
                if title and text:
                    safe_title = sanitize_filename(title)
                    file_path = os.path.join(full_path, f"{safe_title}.md")

                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(text)
                        logger.debug(f"Successfully exported note: {safe_title}")
                    except IOError as e:
                        logger.error(f"Failed to write note {safe_title}: {str(e)}")
                else:
                    logger.warning(f"Skipped note with missing title or content in tag {tag_path}")

        except sqlite3.Error as e:
            logger.error(f"Database query failed for tag {tag_path}: {str(e)}")
            continue

    conn.close()
    logger.debug("Note export process completed")

def generate_monthly_paths(year):
    # Convert year to string if it's passed as integer
    year_str = str(year)

    # Use list comprehension to create paths for all 12 months
    # zfill(2) ensures months are padded with leading zero if needed
    return [f"media-diet/{year_str}/{str(month).zfill(2)}"
            for month in range(1, 13)]

def main():
    db_path = "/Users/matthew/Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite"
    output_dir = config.path.import_dir

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
    tags_to_export.extend(generate_monthly_paths(2012))
    tags_to_export.extend(generate_monthly_paths(2013))
    tags_to_export.extend(generate_monthly_paths(2014))
    tags_to_export.extend(generate_monthly_paths(2015))
    tags_to_export.extend(generate_monthly_paths(2016))
    tags_to_export.extend(generate_monthly_paths(2017))
    tags_to_export.extend(generate_monthly_paths(2018))
    tags_to_export.extend(generate_monthly_paths(2019))
    tags_to_export.extend(generate_monthly_paths(2020))
    tags_to_export.extend(generate_monthly_paths(2021))
    tags_to_export.extend(generate_monthly_paths(2022))
    tags_to_export.extend(generate_monthly_paths(2023))
    tags_to_export.extend(generate_monthly_paths(2024))
    tags_to_export.extend(generate_monthly_paths(2025))

    export_notes_by_tag(db_path, tags_to_export, output_dir)

if __name__ == "__main__":
    main()
