from bs4 import BeautifulSoup
import os

# Paths
NEWS_FOLDER = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\trending"
INDEX_FILE = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\index.html"

# Map categories to pages
CATEGORY_LINKS = {
    "Music": "music.html",
    "Global News": "global.html",
    "Sci-Fi": "scifi.html",
    "Movies & TV Shows": "movies-tv.html"
}

# Function to extract news data from a news HTML file
def extract_news(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    # Title
    title_tag = soup.find("h3")
    title = title_tag.get_text(strip=True) if title_tag else "No Title"

    # --- truncate title if more than 6 words ---
    words = title.split()
    if len(words) > 7:
        title = " ".join(words[:7]) + "..."
    
    # Category
    category_tag = soup.select_one(".overlay .mb-3 a.text-danger")
    category = category_tag.get_text(strip=True) if category_tag else "Unknown"
    
    # Date (grab the last span inside .mb-3)
    mb3_div = soup.select_one(".overlay .mb-3")
    date = "Unknown"
    if mb3_div:
        spans = mb3_div.find_all("span")
        if spans:
            date = spans[-1].get_text(strip=True)
    
    # Image
    img_tag = soup.select_one(".position-relative.mb-3 img")
    img = img_tag["src"] if img_tag else "/ScreamLine/img/news-placeholder.jpg"
    
    # Link (relative to index.html)
    link = os.path.join("trending", os.path.basename(file_path)).replace("\\", "/")
    
    return {"title": title, "category": category, "date": date, "img": img, "link": link}

# Load index.html
with open(INDEX_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Select the Featured News Carousel
featured_carousel = soup.select_one(".owl-carousel-2.carousel-item-4")
if not featured_carousel:
    raise Exception("Could not find Featured News Slider carousel.")

# Clear existing items
for child in featured_carousel.find_all("div", recursive=False):
    child.decompose()

# Get all news files sorted by modified time, newest first
news_files = [f for f in os.listdir(NEWS_FOLDER) if f.endswith(".html")]
news_files.sort(key=lambda x: os.path.getmtime(os.path.join(NEWS_FOLDER, x)), reverse=True)

# Limit to 5 latest news
for nf in news_files[:8]:
    news = extract_news(os.path.join(NEWS_FOLDER, nf))
    
    # Build carousel item
    item = soup.new_tag("div", **{"class": "position-relative overflow-hidden", "style": "height: 300px;"})
    img_tag = soup.new_tag("img", src=news["img"], **{"class": "img-fluid w-100 h-100", "style": "object-fit: cover;"})
    overlay = soup.new_tag("div", **{"class": "overlay"})
    
    # Category + date
    mb_div = soup.new_tag("div", **{"class": "mb-1", "style": "font-size: 13px;"})
    cat_a = soup.new_tag("a", href=CATEGORY_LINKS.get(news["category"], ""), **{"class": "text-white"})
    cat_a.string = news["category"]
    date_span = soup.new_tag("span", **{"class": "px-1 text-white"})
    date_span.string = "/"
    date_a = soup.new_tag("a", href="", **{"class": "text-white"})
    date_a.string = news["date"]
    
    mb_div.append(cat_a)
    mb_div.append(date_span)
    mb_div.append(date_a)
    
    # Title
    title_a = soup.new_tag("a", href=news["link"], **{"class": "h4 m-0 text-white"})
    title_a.string = news["title"]
    
    overlay.append(mb_div)
    overlay.append(title_a)
    item.append(img_tag)
    item.append(overlay)
    featured_carousel.append(item)

# Save the updated index.html
with open(INDEX_FILE, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("Featured News Slider updated successfully!")