import os
import shutil
import glob
from datetime import datetime, timedelta
from pathlib import Path

def copy_old_html_files():
    # Define source folders
    source_folders = [
        r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\music",
        r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\movies-tv",
        r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\scifi",
        r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\global"
    ]
    
    # Define destination folder
    destination_folder = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\old news"
    
    # Create destination folder if it doesn't exist
    Path(destination_folder).mkdir(parents=True, exist_ok=True)
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.now() - timedelta(days=0)
    
    # Counter for copied files
    copied_count = 0
    error_count = 0
    
    print(f"Looking for .html files older than 7 days (before {seven_days_ago.strftime('%Y-%m-%d %H:%M:%S')})")
    print("-" * 70)
    
    for folder in source_folders:
        print(f"\nProcessing folder: {folder}")
        
        # Check if source folder exists
        if not os.path.exists(folder):
            print(f"  ❌ Folder does not exist: {folder}")
            error_count += 1
            continue
        
        # Find all .html files in the folder
        html_files = glob.glob(os.path.join(folder, "*.html"))
        
        if not html_files:
            print(f"  ℹ️  No .html files found in {folder}")
            continue
        
        print(f"  Found {len(html_files)} .html files")
        
        for html_file in html_files:
            try:
                # Get file modification time
                file_mtime = datetime.fromtimestamp(os.path.getmtime(html_file))
                
                # Check if file is 7 days old or older
                if file_mtime < seven_days_ago:
                    # Create destination path
                    filename = os.path.basename(html_file)
                    dest_path = os.path.join(destination_folder, filename)
                    
                    # Avoid overwriting if file already exists
                    counter = 1
                    original_dest = dest_path
                    while os.path.exists(dest_path):
                        name, ext = os.path.splitext(original_dest)
                        dest_path = f"{name}_{counter}{ext}"
                        counter += 1
                    
                    # Copy the file
                    shutil.copy2(html_file, dest_path)
                    copied_count += 1
                    print(f"  ✅ Copied: {filename} (modified: {file_mtime.strftime('%Y-%m-%d %H:%M:%S')})")
                    
            except Exception as e:
                print(f"  ❌ Error processing {os.path.basename(html_file)}: {str(e)}")
                error_count += 1
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY:")
    print(f"✅ Files copied: {copied_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📁 Destination: {destination_folder}")
    
    if copied_count > 0:
        print(f"\nAll {copied_count} old .html files have been copied successfully!")
    else:
        print("\nNo files were 7 days old or older.")

if __name__ == "__main__":
    copy_old_html_files()
