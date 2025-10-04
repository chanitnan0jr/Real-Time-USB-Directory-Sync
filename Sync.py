import os
import shutil
import time
import threading
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SOURCE = r"Your USB Directory"
DESTINATION = r"Your USB Directory"

class SyncHandler(FileSystemEventHandler):
    def __init__(self, src, dst):
        self.src = Path(src)
        self.dst = Path(dst)
        self.last_sync = {}  # Track last sync time to avoid duplicate syncs
    
    def sync_file(self, src_file_path):
        """Sync a single file from source to destination"""
        src_file = Path(src_file_path)
        
        # Check if source file exists and is a file (not directory)
        if not src_file.exists() or not src_file.is_file():
            return
        
        # Skip if file is not under source directory
        try:
            rel_path = src_file.relative_to(self.src)
        except ValueError:
            return
        
        dst_file = self.dst / rel_path
        
        # Check if USB destination exists
        if not self.dst.exists():
            print(f"⚠️  USB not found at {self.dst}")
            return
        
        # Debounce: avoid syncing same file multiple times rapidly
        current_time = time.time()
        if src_file_path in self.last_sync:
            if current_time - self.last_sync[src_file_path] < 1:  # 1 second debounce
                return
        self.last_sync[src_file_path] = current_time
        
        try:
            # Create destination directory if needed
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(src_file, dst_file)
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"✅ Synced: {rel_path} at {timestamp}")
        except Exception as e:
            print(f"❌ Error syncing {rel_path}: {e}")
    
    def on_modified(self, event):
        if not event.is_directory:
            print(f"🔄 Modified: {event.src_path}")
            self.sync_file(event.src_path)
    
    def on_created(self, event):
        if not event.is_directory:
            print(f"➕ Created: {event.src_path}")
            self.sync_file(event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            # Optionally handle deletions
            src_file = Path(event.src_path)
            try:
                rel_path = src_file.relative_to(self.src)
                dst_file = self.dst / rel_path
                if dst_file.exists():
                    dst_file.unlink()
                    print(f"🗑️  Deleted: {rel_path}")
            except Exception as e:
                print(f"❌ Error deleting {event.src_path}: {e}")

def initial_sync(src, dst):
    """Perform initial full sync"""
    src_path = Path(src)
    dst_path = Path(dst)
    
    if not src_path.exists():
        print(f"❌ Source directory does not exist: {src}")
        return False
    
    if not dst_path.exists():
        print(f"❌ Destination directory does not exist: {dst}")
        print("   Please connect your USB drive first!")
        return False
    
    print("🔄 Performing initial sync...")
    files_synced = 0
    
    for root, dirs, files in os.walk(src_path):
        rel_path = Path(root).relative_to(src_path)
        dst_dir = dst_path / rel_path
        
        if not dst_dir.exists():
            dst_dir.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            src_file = Path(root) / file
            dst_file = dst_dir / file
            
            try:
                if not dst_file.exists() or src_file.stat().st_mtime > dst_file.stat().st_mtime:
                    shutil.copy2(src_file, dst_file)
                    files_synced += 1
                    print(f"✅ Synced: {rel_path / file}")
            except Exception as e:
                print(f"❌ Error syncing {rel_path / file}: {e}")
    
    print(f"\n✅ Initial sync complete! {files_synced} files synced.\n")
    return True

if __name__ == "__main__":
    print("="*60)
    print("🔄 REAL-TIME DIRECTORY SYNC")
    print("="*60)
    print(f"Source: {SOURCE}")
    print(f"Destination: {DESTINATION}")
    print("="*60)
    
    # Perform initial sync
    if not initial_sync(SOURCE, DESTINATION):
        print("\n❌ Initial sync failed. Please check your directories.")
        exit(1)
    
    # Start watching for changes
    event_handler = SyncHandler(SOURCE, DESTINATION)
    observer = Observer()
    observer.schedule(event_handler, SOURCE, recursive=True)
    observer.start()
    
    print("👁️  Watching for changes...")
    print("💡 Type 'q' or 'quit' and press Enter to stop the script")
    print("-"*60)
    
    stop_flag = [False]  # Use list to make it mutable in nested function
    
    def check_usb():
        """Check USB connection in background"""
        last_connected = True
        while not stop_flag[0]:
            time.sleep(5)
            currently_connected = Path(DESTINATION).exists()
            
            if last_connected and not currently_connected:
                print("\n⚠️  USB drive disconnected. Waiting for reconnection...")
            elif not last_connected and currently_connected:
                print("✅ USB drive reconnected! Performing sync...")
                initial_sync(SOURCE, DESTINATION)
            
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