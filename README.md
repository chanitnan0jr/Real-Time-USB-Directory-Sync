# Real-Time USB Directory Sync 🔄💾

**Python script** that provides **real-time synchronization** of a local folder (`SOURCE`) to a USB folder (`DESTINATION`). It's designed to keep your backup or working copy instantly updated on portable storage by detecting file **creation, modification, and deletion**, while intelligently handling USB **unplug/replug events** for continuous operation.

**!!This script will not sync these files.!!**
## Files starting with . (dot files)
-Examples: .git, .gitignore, .env, .vscode, .idea, .DS_Store

## Files ending with ~ (backup files)
-Examples: file.txt~, backup~

## Files with extensions: .tmp, .swp, .swx
-These are temporary files from editors

---

## ✨ Features

* **Real-Time Sync:** Uses an event-driven mechanism (no polling) for instant sync on file changes.
* **Initial Full Sync:** Guarantees consistency between source and destination when the script first starts.
* **Intelligent USB Handling:** Syncing **automatically pauses** if the USB drive is removed and **resumes** when it's reconnected.
* **Full Change Support:** Correctly manages file **creation, modification, and deletion**.
* **Logging:** Logs all changes and events with timestamps.
* **Debouncing:** Prevents duplicate syncs during rapid file changes.
* **Graceful Stop:** Script stops safely when you type **`q`** or **`quit`** in the console.

---

## 🛠️ Requirements

* **Python 3.8+** (Installed on Windows).
* The **`watchdog`** Python library for folder monitoring.

---

## 🚀 Installation

### 1. Install Python

1.  Download the installer from [python.org](https://www.python.org/downloads/).
2.  **Crucially**, ensure you check **"Add Python to PATH"** during the installation process.

### 2. Install `watchdog` Library

Open your Command Prompt or PowerShell and run:

```bash
pip install watchdog
```

### 3. Download the Script
Save your Python script (e.g., sync.py) to a permanent location on your PC.

## 💻 Usage
### 1. Configure Paths (🚨 Important)
You must edit the sync.py file to set your source and destination directories. Change the example paths below to match your actual folders:

Python
SOURCE = r"Change this to your local folder"

DESTINATION = r"Change this to your USB folder"

### 2. Run Manually
Run the script from your console:

```bash
python sync.py
```

Script Behavior:
Performs an initial full sync.
Watches the source folder for changes and syncs them to the USB in real-time.
Pauses if the USB is removed and resumes upon reconnection.
To stop: Type q or quit in the console window.

### 3. Run Automatically in VS Code (Optional)
You can configure VS Code to start the sync script every time you open the workspace.
In VS Code, go to Terminal → Configure Tasks → Create tasks.json file from template → Others.
Replace the content with the configuration below:

```JSON
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run USB Sync",
            "type": "shell",
            "command": "python",
            "args": ["Your path to Sync.py"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": true,
                "panel": "shared"
            },
            "problemMatcher": []
        }
    ]
}
```
⚠️ IMPORTANT: You must update the path in the args ["Your Path to Sync.py"] to the exact location of your sync.py file. to make this work automatically
Now, every time you open this VS Code workspace, the sync script will start automatically in a shared terminal panel.
