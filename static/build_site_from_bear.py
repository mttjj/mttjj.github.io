import subprocess
from logger_config import logger

def build_site():
    try:
        logger.info("##### Transforming Taxonomies")
        subprocess.run(["python3", "transform_taxonomies.py"], check=True)

        logger.info("##### Transforming Diet Entries")
        subprocess.run(["python3", "transform_diets.py"], check=True)

        logger.info("##### Moving Files")
        subprocess.run(["python3", "move_files.py"], check=True)

    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred while running a script: {e}")

if __name__ == "__main__":
    build_site()