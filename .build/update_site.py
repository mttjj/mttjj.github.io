import subprocess
from configuration import config

logger = config.logger

def build_site():
    try:
        logger.info("Exporting Notes")
        subprocess.run(["python3", "export_notes.py"], check=True)

        logger.info("Transforming Taxonomies")
        subprocess.run(["python3", "transform_taxonomies.py"], check=True)

        logger.info("Transforming Diet Entries")
        subprocess.run(["python3", "transform_diets.py"], check=True)

        logger.info("Moving Files")
        subprocess.run(["python3", "move_files.py"], check=True)

        logger.info("Performing SCM Operations")
        subprocess.run(["python3", "perform_scm_operations.py"], check=True)

        logger.info("Site successfully updated")

    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred while running a script: {e}")

if __name__ == "__main__":
    build_site()