import json
import os
import tomllib
from collections import defaultdict
from configuration import config

logger = config.logger

MEDIA_TYPES = [
    "books",
    "comics",
    "films",
    "graphic-novels",
    "live-theatre",
    "manga",
    "tv-series",
    "video-games",
]


def parse_front_matter(file_path):
    """
    Extracts and parses the TOML front matter from a daily-diet markdown file.

    :param file_path: Path to the markdown file.
    :return: Parsed front matter as a dict, or None if the file has no front matter.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("+++"):
        return None

    _, front_matter, _ = content.split("+++", 2)
    return tomllib.loads(front_matter)


def collect_stats(media_diet_dir):
    """
    Walks the media-diet content directory and aggregates daily and yearly stats.

    :param media_diet_dir: Root directory containing year/month/day markdown files.
    :return: Tuple of (daily_counts, yearly) dicts ready for JSON serialization.
    """
    daily_counts = {}
    yearly_slugs = defaultdict(lambda: defaultdict(set))
    yearly_days_logged = defaultdict(int)

    for root, _, files in os.walk(media_diet_dir):
        for file in files:
            if file == "_index.md" or not file.endswith(".md"):
                continue

            file_path = os.path.join(root, file)
            front_matter = parse_front_matter(file_path)
            if front_matter is None or "date" not in front_matter:
                logger.debug(f"Skipping file without date front matter: {file_path}")
                continue

            date_str = front_matter["date"]
            year = date_str[:4]

            day_total = 0
            for media_type in MEDIA_TYPES:
                items = front_matter.get(media_type, [])
                day_total += len(items)
                yearly_slugs[year][media_type].update(items)

            daily_counts[date_str] = day_total
            if day_total > 0:
                yearly_days_logged[year] += 1

    yearly = {}
    for year, slugs_by_type in yearly_slugs.items():
        year_stats = {
            media_type: len(slugs) for media_type, slugs in slugs_by_type.items()
        }
        year_stats["total_entries"] = sum(year_stats.values())
        year_stats["days_logged"] = yearly_days_logged[year]
        yearly[year] = year_stats

    return daily_counts, yearly


def write_stats(daily_counts, yearly, output_path):
    """
    Writes the aggregated stats to a JSON file for consumption by Hugo templates.

    :param daily_counts: Dict of date string to entry count.
    :param yearly: Dict of year string to per-type/aggregate stats.
    :param output_path: Path to the output JSON file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {"daily_counts": daily_counts, "yearly": yearly},
            f,
            indent=2,
            sort_keys=True,
        )


if __name__ == "__main__":
    directory = config.paths.media_diet_destination

    logger.info("Collecting media diet stats")
    daily_counts, yearly = collect_stats(directory)

    logger.info("Writing media diet stats")
    write_stats(daily_counts, yearly, config.paths.data_dir / "media_diet_stats.json")
