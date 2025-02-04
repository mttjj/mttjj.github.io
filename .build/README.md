## Main Script
* `update_site.py`
* Make sure it's executable: `chmod + x update_site.py`

## Launch Agent
* Copy the file to `~/Library/LaunchAgents/`
* Load the job: `launchctl load ~/Library/LaunchAgents/com.mttjj.update-website.plist`
* Unload the job if required: `launchctl unload ~/Library/LaunchAgents/com.mttjj.update-website.plist`