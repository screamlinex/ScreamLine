import cv2
import os

# --- Configuration ---
FOLDERS = [
    r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\img\global",
    r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\img\scifi",
    r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\img\music",
    r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\img\movies-tv"
]
LOGO_PATH = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\img\screamlinez.png"
COORD_FILE = r"C:\Users\LOQ\Downloads\ScreamLine\scripts\logo_area.txt"

# --- Load logo ---
logo = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED)
if logo is None:
    print("Failed to load the logo.")
    exit()

# --- Load or select logo area ---
if os.path.exists(COORD_FILE):
    # Load saved coordinates
    with open(COORD_FILE, "r") as f:
        rel_x, rel_y, rel_w, rel_h = map(float, f.read().split(","))
else:
    # Select area on first image of first folder
    first_folder = FOLDERS[0]
    first_images = [f for f in os.listdir(first_folder) if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))]
    if not first_images:
        print(f"No images found in {first_folder}!")
        exit()

    first_image_path = os.path.join(first_folder, first_images[0])
    first_img = cv2.imread(first_image_path)
    if first_img is None:
        print("Failed to read the first image.")
        exit()

    print("Select the area to place the logo and press ENTER or SPACE")
    roi = cv2.selectROI("Select Area", first_img, showCrosshair=True, fromCenter=False)
    cv2.destroyAllWindows()
    x, y, w, h = roi

    if w == 0 or h == 0:
        print("No area selected. Exiting.")
        exit()

    # Store relative coordinates
    rel_x, rel_y = x / first_img.shape[1], y / first_img.shape[0]
    rel_w, rel_h = w / first_img.shape[1], h / first_img.shape[0]

    # Save coordinates to file
    with open(COORD_FILE, "w") as f:
        f.write(f"{rel_x},{rel_y},{rel_w},{rel_h}")

# --- Process all folders ---
for folder in FOLDERS:
    images = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))]
    if not images:
        print(f"No images found in {folder}, skipping.")
        continue

    for filename in images:
        img_path = os.path.join(folder, filename)
        img = cv2.imread(img_path)
        if img is None:
            print(f"Failed to read {filename} in {folder}, skipping.")
            continue

        # Check if logo is already applied by looking for a tiny marker
        # (Optional: skip this step if you always want to overwrite)
        
        # Scale coordinates
        x_new = int(rel_x * img.shape[1])
        y_new = int(rel_y * img.shape[0])
        w_new = int(rel_w * img.shape[1])
        h_new = int(rel_h * img.shape[0])

        # Resize logo
        logo_resized = cv2.resize(logo, (w_new, h_new), interpolation=cv2.INTER_AREA)

        # Apply logo with alpha if present
        if logo_resized.shape[2] == 4:
            b, g, r, a = cv2.split(logo_resized)
            overlay_color = cv2.merge((b, g, r))
            mask = cv2.merge((a, a, a)) / 255.0
            img_region = img[y_new:y_new+h_new, x_new:x_new+w_new]
            img[y_new:y_new+h_new, x_new:x_new+w_new] = (overlay_color * mask + img_region * (1 - mask)).astype('uint8')
        else:
            img[y_new:y_new+h_new, x_new:x_new+w_new] = logo_resized

        # Overwrite the image
        cv2.imwrite(img_path, img)
        print(f"Processed {filename} in {folder}")

print("All images processed!")
