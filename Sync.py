import os
import shutil
import time
import threading
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOCAL = r"You Local directory"
USB = r"Your USB directory"

class TwoWaySyncHandler(FileSystemEventHandler):
    def __init__(self, src, dst, name):
        self.src = Path(src)
        self.dst = Path(dst)
        self.name = name  # "LOCAL" or "USB" for logging
        self.last_sync = {}  # Track last sync time to avoid duplicate syncs
        self.syncing = False  # Prevent sync loops
    
    def sync_file(self, src_file_path, is_deletion=False):
        """Sync a single file from source to destination"""
        # Prevent recursive syncing
        if self.syncing:
            return
        
        src_file = Path(src_file_path)
        
        # Skip temporary/hidden files from editors
        if src_file.name.startswith('.') or src_file.name.endswith('~'):
            return
        if src_file.suffix in ['.tmp', '.swp', '.swx']:
            return
        
        # Skip if file is not under source directory
        try:
            rel_path = src_file.relative_to(self.src)
        except ValueError:
            return
        
        dst_file = self.dst / rel_path
        
        # Check if destination exists
        if not self.dst.exists():
            print(f"⚠️  Destination not found at {self.dst}")
            return
        
        # Debounce: avoid syncing same file multiple times rapidly
        current_time = time.time()
        cache_key = str(src_file)
        if cache_key in self.last_sync:
            if current_time - self.last_sync[cache_key] < 0.5:  # 0.5 second debounce (reduced)
                return
        self.last_sync[cache_key] = current_time
        
        try:
            self.syncing = True
            
            if is_deletion:
                # Handle deletion
                if dst_file.exists():
                    dst_file.unlink()
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"🗑️  [{self.name}→] Deleted: {rel_path} at {timestamp}")
            else:
                # Check if source file exists and is a file
                if not src_file.exists() or not src_file.is_file():
                    return
                
                # Wait a tiny bit for file to be fully written (VSCode issue)
                time.sleep(0.1)
                
                # Create destination directory if needed
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(src_file, dst_file)
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"✅ [{self.name}→] Synced: {rel_path} at {timestamp}")
        except Exception as e:
            print(f"❌ [{self.name}→] Error syncing {rel_path}: {e}")
        finally:
            self.syncing = False
    
    def on_modified(self, event):
        if not event.is_directory:
            self.sync_file(event.src_path)
    
    def on_created(self, event):
        if not event.is_directory:
            self.sync_file(event.src_path)
    
    def on_moved(self, event):
        """Handle file moves/renames (common with VSCode)"""
        if not event.is_directory:
            # VSCode often does: create temp → move to actual file
            self.sync_file(event.dest_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.sync_file(event.src_path, is_deletion=True)

def initial_sync_bidirectional(dir1, dir2):
    """Perform initial two-way sync - newer files win"""
    path1 = Path(dir1)
    path2 = Path(dir2)
    
    if not path1.exists():
        print(f"❌ Directory does not exist: {dir1}")
        return False
    
    if not path2.exists():
        print(f"❌ Directory does not exist: {dir2}")
        print("   Please connect your USB drive first!")
        return False
    
    print("🔄 Performing initial two-way sync (newer files win)...")
    files_synced = 0
    
    # Get all files from both directories
    all_files = set()
    
    for root, dirs, files in os.walk(path1):
        for file in files:
            rel_path = Path(root).relative_to(path1) / file
            all_files.add(rel_path)
    
    for root, dirs, files in os.walk(path2):
        for file in files:
            rel_path = Path(root).relative_to(path2) / file
            all_files.add(rel_path)
    
    # Sync each file based on modification time
    for rel_path in all_files:
        file1 = path1 / rel_path
        file2 = path2 / rel_path
        
        try:
            # Both exist - sync newer to older
            if file1.exists() and file2.exists():
                mtime1 = file1.stat().st_mtime
                mtime2 = file2.stat().st_mtime
                
                if mtime1 > mtime2:
                    # Local is newer, copy to USB
                    file2.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file1, file2)
                    files_synced += 1
                    print(f"✅ [LOCAL→USB] {rel_path}")
                elif mtime2 > mtime1:
                    # USB is newer, copy to Local
                    file1.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file2, file1)
                    files_synced += 1
                    print(f"✅ [USB→LOCAL] {rel_path}")
            
            # Only exists in dir1 - copy to dir2
            elif file1.exists():
                file2.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file1, file2)
                files_synced += 1
                print(f"✅ [LOCAL→USB] {rel_path}")
            
            # Only exists in dir2 - copy to dir1
            elif file2.exists():
                file1.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file2, file1)
                files_synced += 1
                print(f"✅ [USB→LOCAL] {rel_path}")
        
        except Exception as e:
            print(f"❌ Error syncing {rel_path}: {e}")
    
    print(f"\n✅ Initial sync complete! {files_synced} files synced.\n")
    return True

if __name__ == "__main__":
    print("="*60)
    print("🔄 TWO-WAY REAL-TIME DIRECTORY SYNC")
    print("="*60)
    print(f"Local:  {LOCAL}")
    print(f"USB:    {USB}")
    print("="*60)
    
    # Perform initial sync
    if not initial_sync_bidirectional(LOCAL, USB):
        print("\n❌ Initial sync failed. Please check your directories.")
        exit(1)
    
    # Start watching BOTH directories
    local_handler = TwoWaySyncHandler(LOCAL, USB, "LOCAL")
    usb_handler = TwoWaySyncHandler(USB, LOCAL, "USB")
    
    observer = Observer()
    observer.schedule(local_handler, LOCAL, recursive=True)
    observer.schedule(usb_handler, USB, recursive=True)
    observer.start()
    
    print("👁️  Watching both directories for changes...")
    print("💡 Type 'q' or 'quit' and press Enter to stop the script")
    print("-"*60)
    
    stop_flag = [False]
    
    def check_usb():
        """Check USB connection in background"""
        last_connected = True
        while not stop_flag[0]:
            time.sleep(5)
            currently_connected = Path(USB).exists()
            
            if last_connected and not currently_connected:
                print("\n⚠️  USB drive disconnected. Waiting for reconnection...")
            elif not last_connected and currently_connected:
                print("✅ USB drive reconnected! Performing sync...")
                initial_sync_bidirectional(LOCAL, USB)
            
            last_connected = currently_connected
    
    # Start USB checking in background thread
    usb_thread = threading.Thread(target=check_usb, daemon=True)
    usb_thread.start()
    
    try:
        while True:
            user_input = input().strip().lower()
            if user_input in ['q', 'quit', 'exit', 'stop']:
                print("\n🛑 Stopping sync service...")
                stop_flag[0] = True
                break
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping sync service...")
        stop_flag[0] = True
    
    observer.stop()
    observer.join()
    print("✅ Sync service stopped.")