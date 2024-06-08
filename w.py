import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Handler(FileSystemEventHandler):
    def __init__(self):
        self.python_path = os.path.join(os.getcwd(), 'winenv', 'Scripts', 'python.exe')
        self.bot_process = subprocess.Popen([self.python_path, '-m', 'bot'], start_new_session=True)

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"Detected modification in: {event.src_path}")
            print("Terminating existing bot process...")
            self.bot_process.terminate()
            time.sleep(1)  # Give it a second to terminate
            print("Starting new bot process...")
            self.bot_process = subprocess.Popen([self.python_path, '-m', 'bot'], start_new_session=True)

handler = Handler()
observer = Observer()
observer.schedule(handler, path='bot', recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    handler.bot_process.terminate()
    observer.stop()
observer.join()