import subprocess
from datetime import datetime
import sys
from configuration import config

logger = config.logger
base_dir = config.paths.base_dir
content_dir = config.paths.content_dir.resolve()

def has_changes():
    """Check if there are any changes in the content directory"""
    result = subprocess.run(
        ['git', 'status', '--porcelain', content_dir],
        capture_output=True,
        text=True,
        cwd=base_dir
    )
    return bool(result.stdout.strip())

def git_stage_content():
    """Stage all changes in the content directory"""
    try:
        subprocess.run(['git', 'add', content_dir],
                      capture_output=True, text=True, cwd=base_dir)
        logger.info("Successfully staged changes in content directory")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error staging changes: {e}")
        logger.error(f"Git output: {e.stderr}")
        return False

def git_commit(message):
    """Create a commit with the staged changes"""
    try:
        result = subprocess.run(['git', 'commit', '-m', message],
                              capture_output=True, text=True, cwd=base_dir)
        logger.info(f"Successfully committed changes with message: {message}")
        logger.debug(f"Commit output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        if "no changes" in e.stderr:
            logger.info("No changes to commit")
            return True
        logger.error(f"Error committing changes: {e}")
        logger.error(f"Git output: {e.stderr}")
        return False

def git_push():
    """Push commits to remote repository"""
    try:
        result = subprocess.run(['git', 'push'],
                              capture_output=True, text=True, cwd=base_dir)
        logger.info("Successfully pushed changes to remote repository")
        logger.debug(f"Push output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        if "Everything up-to-date" in e.stderr:
            logger.info("Remote is up-to-date, nothing to push")
            return True
        logger.error(f"Error pushing changes: {e}")
        logger.error(f"Git output: {e.stderr}")
        return False

def main():
    commit_message = f"{datetime.now().strftime('%Y-%m-%d')} update"

    if has_changes():
        if not git_stage_content():
            logger.error("Failed to stage changes")

        if not git_commit(commit_message):
            logger.error("Failed to commit changes")

        if not git_push():
            logger.error("Failed to push changes")
    else:
        logger.info("No changes detected in content directory")

if __name__ == "__main__":
    main()
