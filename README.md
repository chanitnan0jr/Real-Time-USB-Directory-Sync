# Real-Time USB Directory Sync 🔄💾

A powerful **Python script** designed for seamless, **real-time synchronization** of a local directory to a USB drive. It provides a robust, set-it-and-forget-it solution for keeping a backup or working copy on your portable storage up-to-date without manual intervention.

---

## ✨ Features

* **Real-Time Monitoring:** Uses the `watchdog` library to detect file creation, modification, and deletion **instantly**, avoiding resource-heavy polling.
* **Initial Full Sync:** Ensures the destination is consistent with the source when the script first starts.
* **Intelligent USB Handling:** Gracefully handles USB unplug and replug events. Syncing **automatically pauses** when the drive is removed and **resumes** when it's reconnected.
* **Reliable Logging:** Logs all changes and events with **timestamps** for transparency and troubleshooting.
* **Change Debouncing:** Prevents duplicate sync operations during rapid-fire file changes.
* **Full Change Support:** Correctly handles **file creation, modification, and deletion** events.

---

## 🛠️ Requirements

* **Python 3.8+** (Must be installed on Windows).
* The **`watchdog`** Python library.

---

## 🚀 Installation

### 1. Install Python

1.  Download the installer from [python.org](https://www.python.org/downloads/).
2.  **Crucially**, ensure you check the box that says **"Add Python to PATH"** during the installation process.

### 2. Install `watchdog` Library

Open your Command Prompt or PowerShell and execute the following command:

```bash
pip install watchdog

