## Main Script
* `update_site.py`
* Make sure it's executable: `chmod + x update_site.py`

## macOS Permissions
Python needs "full disk permissions" to be able to run without having the annoying popup when it executes as part of this launch daemon.
1. Open System Settings > Privacy & Security > Full Disk Access
2. Open Finder and navigate to `/opt/homebrew/bin/python3`
3. Right-click on the Alias and "Show Original"
4. Drag the actual executable onto the list in System Settings.

Dragging the alias into the list will NOT work! Clicking the + icon and trying to navigate to the python executable will NOT work!

## Launch Agent
* Copy the file to `~/Library/LaunchAgents/`
* Load the job: `launchctl load ~/Library/LaunchAgents/com.mttjj.update-website.plist`
* Unload the job if required: `launchctl unload ~/Library/LaunchAgents/com.mttjj.update-website.plist`