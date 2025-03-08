#!/usr/bin/env python3
import os
import sys
import subprocess
from configuration import config

logger = config.logger
paths = config.paths


def ensure_venv():
    """Ensure virtual environment exists and has required packages."""
    # Get the directory where this script is located
    script_dir = paths.base_dir

    # Path to the virtual environment within the script directory
    venv_path = os.path.join(script_dir, "venv")
    venv_python = os.path.join(venv_path, "bin", "python")

    # Check if virtual environment exists, if not create it
    if not os.path.exists(venv_path):
        logger.info("Setting up virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
            # Install required packages
            subprocess.run(
                [
                    venv_python,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    os.path.join(script_dir, "requirements.txt"),
                ],
                check=True,
            )

            logger.info("Virtual environment created successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create virtual environment: {e}")
            raise

    return venv_python


def build_site():
    try:
        # Ensure virtual environment exists and get its Python path
        venv_python = ensure_venv()

        logger.debug(f"Python info: {sys.version}")

        logger.info("Exporting Notes")
        subprocess.run([venv_python, paths.base_dir / "export_notes.py"], check=True)

        logger.info("Transforming Taxonomies")
        subprocess.run(
            [venv_python, paths.base_dir / "transform_taxonomies.py"], check=True
        )

        logger.info("Transforming Diet Entries")
        subprocess.run([venv_python, paths.base_dir / "transform_diets.py"], check=True)

        logger.info("Moving Files")
        subprocess.run([venv_python, paths.base_dir / "move_files.py"], check=True)

        logger.info("Performing SCM Operations")
        subprocess.run(
            [venv_python, paths.base_dir / "perform_scm_operations.py"], check=True
        )

        logger.info("Site successfully updated")

    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred while running a script: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    build_site()
