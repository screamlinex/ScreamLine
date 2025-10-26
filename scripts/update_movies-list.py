import os
from bs4 import BeautifulSoup

# Paths
MOVIES_TV_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\movies-tv"
HTML_FILE = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\movies-tv.html"

def limit_title(title, max_words=6):
    """Limit title length for display (default = 6 words)."""
    words = title.split()
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")

def extract_metadata(filepath):
    """Extract news metadata from an article HTML file."""
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Title
    h3 = soup.find("h3", class_="mb-3")
    title = h3.get_text(strip=True) if h3 else os.path.basename(filepath)

    # Date (from article body, if available)
    date_span = soup.select_one(".mb-3 span:last-of-type")
    date = date_span.get_text(strip=True) if date_span else None  # Use None if missing

    # Summary (first <p class="important">)
    summary_p = soup.find("p", class_="important")
    desc = summary_p.get_text(strip=True).replace("Summary:", "").strip() if summary_p else ""

    # Image
    img_tag = soup.find("img")
    img = img_tag["src"].split("/")[-1] if img_tag and img_tag.get("src") else "default.jpg"

    return {
        "title": title,
        "desc": desc,
        "date": date,
        "img": img,
        "file": os.path.basename(filepath),
        "path": filepath
    }

def main():
    # Collect all article files
    news_files = [os.path.join(MOVIES_TV_DIR, f) for f in os.listdir(MOVIES_TV_DIR) if f.endswith(".html")]

    # Extract metadata
    news_items_raw = [extract_metadata(f) for f in news_files]
    # Filter out items without a date
    news_items = [item for item in news_items_raw if item["date"]]

    # ✅ Sort by latest modified time (newest first)
    news_items.sort(reverse=True, key=lambda x: os.path.getmtime(x["path"]))

    # Split into big and small news
    big_news = news_items[:4]
    small_news = news_items[4:14]

    # Load main movies-tv.html
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Update big news section
    big_news_divs = soup.select(".col-lg-6 .position-relative.mb-3")[:4]
    for div, item in zip(big_news_divs, big_news):
        img = div.find("img")
        if img:
            img["src"] = f"/ScreamLine/img/movies-tv/{item['img']}"
        a_title = div.find("a", class_="h4")
        if a_title:
            a_title.string = limit_title(item["title"])
            a_title["href"] = f"/ScreamLine/movies-tv/{item['file']}"
        
        # Handle date: Clear siblings after category and insert only article date
        metadata_div = div.find("div", style="font-size: 14px;")
        if metadata_div:
            category_a = metadata_div.find("a", class_="text-danger")
            if category_a:
                for sibling in list(category_a.next_siblings):
                    sibling.extract()
                date_span = soup.new_tag("span", class_="px-1")
                date_span.string = item["date"]
                metadata_div.append(date_span)
        
        p = div.find("p")
        if p:
            p.string = item["desc"][:150] + "..." if item["desc"] else ""

    # Update small news section
    small_news_divs = soup.select("#movies-tv-small-news .d-flex.mb-3")[:10]
    for div, item in zip(small_news_divs, small_news):
        img = div.find("img")
        if img:
            img["src"] = f"/ScreamLine/img/movies-tv/{item['img']}"
        a_title = div.find("a", class_="h6")
        if a_title:
            a_title.string = limit_title(item["title"])
            a_title["href"] = f"/ScreamLine/movies-tv/{item['file']}"
        
        # Handle date: Clear siblings after category and insert only article date
        metadata_div = div.find("div", style="font-size: 13px;")
        if metadata_div:
            category_a = metadata_div.find("a", class_="text-danger")
            if category_a:
                for sibling in list(category_a.next_siblings):
                    sibling.extract()
                date_span = soup.new_tag("span", class_="px-1")
                date_span.string = item["date"]
                metadata_div.append(date_span)

    # Save back the updated movies-tv.html
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    print("✅ movies-tv.html updated with the latest created/modified articles!")

if __name__ == "__main__":
    main()