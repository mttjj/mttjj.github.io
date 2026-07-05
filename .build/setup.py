#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

PYTHON_BIN = "/Users/matthew/.pyenv/versions/3.13.8/bin/python3"
SCRIPT_DIR = Path(__file__).resolve().parent
VENV_PATH = SCRIPT_DIR / "venv"
VENV_PYTHON = VENV_PATH / "bin" / "python"


def setup_venv():
    """Create and configure virtual environment for the build scripts."""
    if VENV_PATH.exists():
        print(f"✓ Virtual environment already exists at {VENV_PATH}")
        return

    print(f"Creating virtual environment at {VENV_PATH}...")
    try:
        subprocess.run(
            [PYTHON_BIN, "-m", "venv", str(VENV_PATH)],
            check=True,
        )
        print("✓ Virtual environment created")

        print("Installing dependencies...")
        subprocess.run(
            [
                str(VENV_PYTHON),
                "-m",
                "pip",
                "install",
                "-r",
                str(SCRIPT_DIR / "requirements.txt"),
            ],
            check=True,
        )
        print("✓ Dependencies installed")

        print("\n✓ Setup complete!")
        print(f"\nNow add to macOS Full Disk Access:")
        print(f"  {VENV_PATH / 'bin' / 'python'}")

    except subprocess.CalledProcessError as e:
        print(f"✗ Setup failed: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    setup_venv()
