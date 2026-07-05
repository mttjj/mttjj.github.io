## Setup

1. **Initialize the virtual environment** (one-time):
   ```bash
   python3 setup.py
   ```
   This creates the venv and installs dependencies from `requirements.txt`.

2. **Add Python binaries to macOS Full Disk Access**:
   - Open System Settings > Privacy & Security > Full Disk Access
   - Click the + button and add these two binaries:
     - `/Users/matthew/.pyenv/versions/3.13.8/bin/python3` (main interpreter)
     - `.build/venv/bin/python` (venv interpreter)
   
   *Note: Use the + button and navigate directly. Do NOT drag aliases.*

## Launch Agent

1. Copy the plist to LaunchAgents:
   ```bash
   cp com.mttjj.update-website.plist ~/Library/LaunchAgents/
   ```

2. Load the job:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.mttjj.update-website.plist
   ```

3. To unload:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.mttjj.update-website.plist
   ```

## Scripts

- `update_site.py`: Main orchestrator (runs sub-scripts in sequence)
- `setup.py`: One-time initialization (creates venv, installs deps)
- `export_notes.py`, `transform_taxonomies.py`, `transform_diets.py`, `move_files.py`, `perform_scm_operations.py`: Individual tasks
- `configuration.py`: Shared paths and logging
- `utils.py`: Shared utilities