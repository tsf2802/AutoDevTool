#!/usr/bin/env python
import sys
import time
import subprocess
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DjangoRestartHandler(FileSystemEventHandler):
    def __init__(self, process):
        self.process = process
        self.last_restart = time.time()
    
    def on_any_event(self, event):
        # Skip directories and non-Python files
        if event.is_directory or not event.src_path.endswith('.py'):
            return
            
        # Debounce to avoid multiple restarts
        current_time = time.time()
        if current_time - self.last_restart < 1:
            return
            
        print(f"\nDetected change in {event.src_path}")
        print("Restarting Django server...")
        
        # Restart the process
        self.process.terminate()
        self.process.wait()
        self.process = subprocess.Popen(
            ["python", "manage.py", "runserver", "0.0.0.0:8000"],
            preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
        )
        self.last_restart = current_time

def main():
    # Start Django server
    process = subprocess.Popen(
        ["python", "manage.py", "runserver", "0.0.0.0:8000"],
        preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
    )
    
    # Set up file watcher
    event_handler = DjangoRestartHandler(process)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    
    print("Django auto-reload file watcher started.")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        process.terminate()
    
    observer.join()
    process.wait()

if __name__ == "__main__":
    main()
