import os
import shutil
from pathlib import Path
import time

# --- Folder order for copying ---
# This order ensures final trending sequence = Music (top), Movies-TV, Scifi, Global News
folders = [
    r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\global",
    r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\scifi",
    r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\movies-tv",
    r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\music"
]

# --- Destination folder ---
destination = Path(r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\trending")
destination.mkdir(parents=True, exist_ok=True)

# --- Settings ---
MAX_FILES = 10                # Keep only 10 latest news
OVERWRITE_EXISTING = False    # Skip if same file name already exists

# --- Copy newest files in defined order ---
for folder in folders:
    path = Path(folder)
    html_files = [f for f in path.glob("*.html") if f.is_file()]
    html_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    newest_files = html_files[:2]  # Take 2 newest

    for file in newest_files:
        dest_file = destination / file.name

        # Skip duplicates unless overwrite enabled
        if dest_file.exists() and not OVERWRITE_EXISTING:
            print(f"⚠️ Skipping (already exists): {file.name}")
            continue

        # Copy and adjust timestamp (so the last copied category = newest)
        shutil.copy2(file, dest_file)
        # Update modified time to "now" to preserve order
        os.utime(dest_file, None)
        print(f"✅ Copied: {file.name} -> {destination}")

        # Small delay so each batch keeps timestamp order
        time.sleep(0.5)

# --- Keep only the 10 newest files ---
all_trending_files = [f for f in destination.glob("*.html") if f.is_file()]
all_trending_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

if len(all_trending_files) > MAX_FILES:
    old_files = all_trending_files[MAX_FILES:]
    for old_file in old_files:
        old_file.unlink()
        print(f"🗑️ Deleted old news: {old_file.name}")

print(f"🎵 Done! Trending folder now has {min(len(all_trending_files), MAX_FILES)} files in order:")
print("   1. Music (newest)\n   2. Movies-TV\n   3. Scifi\n   4. Global News (oldest)")


