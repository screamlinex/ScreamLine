import os
import time
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# List of folders to watch
watch_folders = [
    "C:/Users/drlun/Downloads/ScreamLine/ScreamLine/img/music",
    "C:/Users/drlun/Downloads/ScreamLine/ScreamLine/img/movies-tv",
    "C:/Users/drlun/Downloads/ScreamLine/ScreamLine/img/paranormal",
    "C:/Users/drlun/Downloads/ScreamLine/ScreamLine/img/scifi"
]

# Folder to save cropped images for each watched folder
save_folders = [
    "C:/Users/drlun/Pictures/Cropped/music",
    "C:/Users/drlun/Pictures/Cropped/movies-tv",
    "C:/Users/drlun/Pictures/Cropped/paranormal",
    "C:/Users/drlun/Pictures/Cropped/scifi"
]

# Ensure save folders exist
for folder in save_folders:
    os.makedirs(folder, exist_ok=True)

class ImageHandler(FileSystemEventHandler):
    def __init__(self, save_folder):
        self.save_folder = save_folder

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                img = Image.open(event.src_path)
                width, height = img.size
                target_ratio = 16 / 9

                # Crop logic
                if width / height > target_ratio:
                    new_width = int(height * target_ratio)
                    left = (width - new_width) // 2
                    img_cropped = img.crop((left, 0, left + new_width, height))
                else:
                    new_height = int(width / target_ratio)
                    top = (height - new_height) // 2
                    img_cropped = img.crop((0, top, width, top + new_height))

                filename = os.path.join(self.save_folder, os.path.basename(event.src_path))
                img_cropped.save(filename)
                print(f"Cropped and saved: {filename}")

            except Exception as e:
                print(f"Error processing {event.src_path}: {e}")

# Set up observers for all folders
observers = []
for watch_folder, save_folder in zip(watch_folders, save_folders):
    observer = Observer()
    event_handler = ImageHandler(save_folder)
    observer.schedule(event_handler, watch_folder, recursive=False)
    observer.start()
    observers.append(observer)

print("Watching all folders for new images... Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    for observer in observers:
        observer.stop()
for observer in observers:
    observer.join()