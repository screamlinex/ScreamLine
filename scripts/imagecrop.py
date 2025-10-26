import os
from PIL import Image

# --- Folders to crop ---
watch_folders = [
    "C:/Users/LOQ/Downloads/ScreamLine/ScreamLine/img/music",
    "C:/Users/LOQ/Downloads/ScreamLine/ScreamLine/img/movies-tv",
    "C:/Users/LOQ/Downloads/ScreamLine/ScreamLine/img/global",
    "C:/Users/LOQ/Downloads/ScreamLine/ScreamLine/img/scifi"
]

# Ensure folders exist
for folder in watch_folders:
    os.makedirs(folder, exist_ok=True)

# --- Cropping function ---
def crop_to_16_9(filepath):
    """Crop image in-place to 16:9 if not already that ratio."""
    try:
        img = Image.open(filepath)
        width, height = img.size
        target_ratio = 16 / 9
        current_ratio = width / height

        # Skip if already approximately 16:9 (small tolerance allowed)
        if abs(current_ratio - target_ratio) < 0.01:
            return  # already 16:9

        # Crop logic
        if current_ratio > target_ratio:  # too wide
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            img = img.crop((left, 0, left + new_width, height))
        else:  # too tall
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            img = img.crop((0, top, width, top + new_height))

        # Overwrite same image
        img.save(filepath)
        print(f"✂️ Cropped to 16:9 → {filepath}")

    except Exception as e:
        print(f"⚠️ Error cropping {filepath}: {e}")


# --- Crop existing images only ---
print("🔍 Checking and cropping existing images (if not 16:9)...")
for folder in watch_folders:
    for file in os.listdir(folder):
        if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            crop_to_16_9(os.path.join(folder, file))

print("✅ Finished cropping existing images.")
