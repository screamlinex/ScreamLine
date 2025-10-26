from bs4 import BeautifulSoup
import os

# Paths
BASE_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine"
INDEX_FILE = os.path.join(BASE_DIR, "index.html")
CATEGORIES = {
    "Music": os.path.join(BASE_DIR, "music"),
    "Global News": os.path.join(BASE_DIR, "global"),
    "Science": os.path.join(BASE_DIR, "scifi"),
    "Movies & TV Shows": os.path.join(BASE_DIR, "movies-tv"),
}

# Map categories to exact folder names for links
CATEGORY_LINK_FOLDER = {
    "Music": "music",
    "Global News": "global",
    "Science": "scifi",
    "Movies & TV Shows": "movies-tv",
}

# Load index.html
with open(INDEX_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")


# Function to extract news data
def extract_news(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        news_soup = BeautifulSoup(f, "html.parser")

    # Title
    title_tag = news_soup.find("h3")
    title = title_tag.get_text(strip=True) if title_tag else "No Title"

    # --- truncate title if more than 6 words ---
    words = title.split()
    if len(words) > 15:
        title = " ".join(words[:15]) + "..."

    # Category
    category_tag = news_soup.select_one(".overlay .mb-3 a.text-danger, .overlay .mb-2 a.text-danger")
    category = category_tag.get_text(strip=True) if category_tag else "Unknown"

    # Date
    mb_div = news_soup.select_one(".overlay .mb-3, .overlay .mb-2")
    date = "Unknown"
    if mb_div:
        spans = mb_div.find_all("span")
        if spans:
            date = spans[-1].get_text(strip=True)

    # Image
    img_tag = news_soup.select_one(".position-relative.mb-3 img, .position-relative img")
    img = img_tag["src"] if img_tag else "/ScreamLine/img/news-placeholder.jpg"

    # Link
    link = os.path.basename(file_path)

    return {"title": title, "category": category, "date": date, "img": img, "link": link}


# Process each category
for category, folder in CATEGORIES.items():
    # Find the carousel under this category heading
    heading = soup.find("h3", string=category)
    if not heading:
        continue
    carousel = heading.find_parent("div", class_="col-lg-6").select_one(".owl-carousel")
    if not carousel:
        continue

    # Clear old items
    for child in carousel.find_all("div", recursive=False):
        child.decompose()

    # Collect latest 4 files
    news_files = [f for f in os.listdir(folder) if f.endswith(".html")]
    news_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)

    for nf in news_files[:4]:
        news = extract_news(os.path.join(folder, nf))

        # Build carousel item
        item = soup.new_tag("div", **{"class": "position-relative"})
        img_tag = soup.new_tag(
            "img",
            src=news["img"],
            **{"class": "img-fluid w-100", "style": "object-fit: cover;"},
        )
        overlay = soup.new_tag("div", **{"class": "overlay position-relative bg-light"})

        # Category + date
        mb_div = soup.new_tag("div", **{"class": "mb-2", "style": "font-size: 13px;"})
        cat_a = soup.new_tag("a", href="", **{"class": "text-danger"})
        cat_a.string = news["category"]
        date_span = soup.new_tag("span", **{"class": "px-1"})
        date_span.string = "/"
        date_text = soup.new_tag("span")
        date_text.string = news["date"]

        mb_div.append(cat_a)
        mb_div.append(date_span)
        mb_div.append(date_text)

        # Title
        # Only Music keeps 'text-black'; others just h4 m-0
        title_class = "h6 m-0 text-black" if category in ["Music"] else "h6 m-0"
        title_a = soup.new_tag(
    "a",
    href=f"/ScreamLine/{CATEGORY_LINK_FOLDER[category]}/{news['link']}",
    **{"class": title_class},
)

        title_a.string = news["title"]

        overlay.append(mb_div)
        overlay.append(title_a)
        item.append(img_tag)
        item.append(overlay)
        carousel.append(item)


# Save changes
with open(INDEX_FILE, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("Category News Sliders updated successfully!")