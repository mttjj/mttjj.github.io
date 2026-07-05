#!/usr/bin/env python3
import os
import sys
import subprocess
from configuration import config

logger = config.logger
paths = config.paths

PYTHON_BIN = "/Users/matthew/.pyenv/versions/3.13.8/bin/python3"


def get_venv_python():
    """Get path to venv Python, validating it exists."""
    venv_path = os.path.join(paths.base_dir, "venv")
    venv_python = os.path.join(venv_path, "bin", "python")

    if not os.path.exists(venv_python):
        logger.error(
            f"Virtual environment not found at {venv_python}. "
            "Run 'python3 setup.py' in .build/ to initialize it."
        )
        raise FileNotFoundError(
            f"Venv Python not found. Setup required: {paths.base_dir}/setup.py"
        )

    return venv_python


def build_site():
    try:
        # Get the venv Python path (assumes setup.py has already been run)
        venv_python = get_venv_python()

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
