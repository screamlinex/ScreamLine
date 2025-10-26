import os
import subprocess

# Base path
BASE_PATH = r"C:\Users\LOQ\Downloads\ScreamLine"

# Paths to folders
NEWS_GEN_FOLDER = os.path.join(BASE_PATH, "News-Gen")
SCRIPTS_FOLDER = os.path.join(BASE_PATH, "scripts")

# Function to run scripts in a folder
def run_scripts_in_folder(folder, folder_name):
    if not os.path.isdir(folder):
        print(f"Warning: Folder '{folder}' does not exist. Skipping.")
        return
    scripts = [f for f in os.listdir(folder) if f.endswith(".py")]
    if not scripts:
        print(f"No Python scripts found in '{folder_name}'.")
        return

    # If this is the scripts folder, ensure bottom-news-update.py runs last
    if folder_name == "scripts" and "bottom-news-update.py" in scripts:
        scripts.remove("bottom-news-update.py")
        scripts.append("bottom-news-update.py")

    for script in scripts:
        script_path = os.path.join(folder, script)
        print(f"Running {folder_name}/{script}...")
        result = subprocess.run(["python", script_path])
        if result.returncode == 0:
            print(f"{script} finished successfully.\n")
        else:
            print(f"{script} failed with return code {result.returncode}.\n")

# Step 1: Run scripts in News-Gen first
print("Starting with News-Gen folder...\n")
run_scripts_in_folder(NEWS_GEN_FOLDER, "News-Gen")

# Step 2: Then run scripts in scripts folder
print("Now running scripts folder...\n")
run_scripts_in_folder(SCRIPTS_FOLDER, "scripts")

print("All scripts executed!")

