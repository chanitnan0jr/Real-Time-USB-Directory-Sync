# Real-Time USB Directory Sync

A Python script that automatically syncs a local folder (`SOURCE`) to a USB folder (`DESTINATION`) in real-time. It detects file creation, modification, and deletion, and handles USB unplug/replug events gracefully.

---

## Features

- Real-time sync on file changes (no polling).  
- Initial full sync on startup.  
- Automatic pause if USB is removed, resumes when reconnected.  
- Logs changes with timestamps.  
- Debounces rapid changes to avoid duplicate syncs.  
- Handles file creation, modification, and deletion.  
- Stop the script gracefully by typing `q` or `quit` in the console.  

---

## Requirements

- **Python 3.8+** installed on Windows.  
- **watchdog** Python library for folder monitoring.  

---

## Installation

### 1. Install Python
Download Python from [python.org](https://www.python.org/downloads/windows/) and make sure to check **Add Python to PATH** during installation.

### 2. Install watchdog library
Open Command Prompt or PowerShell and run:

```bash
pip install watchdog
```
### 3. Download the script
Save your sync.py script (or any name you like) somewhere on your PC.

## Usage
### 1. Set your paths in the script
Important! Change these to match your directories:
python
Copy code
SOURCE = r"Change this to your local folder"         
DESTINATION = r"Change this to your USB folder" 
### 2. Run the script
```bash
python sync.py
```
### 3. Behavior
The script will perform an initial full sync.
It will then watch the source folder for changes and sync them to the USB in real-time.
If the USB is removed, it pauses syncing.
When the USB is reconnected, it automatically resumes and re-syncs.
To stop the script gracefully, type q, quit, exit, or stop in the console and press Enter.
