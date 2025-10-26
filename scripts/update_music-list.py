import os
from bs4 import BeautifulSoup

# Paths
MUSIC_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\music"
HTML_FILE = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\music.html"

def limit_title(title, max_words=6):
    words = title.split()
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")

def extract_news_metadata(filepath):
    """Extract title, description, date, and image from a news HTML file"""
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    # Title
    h3 = soup.find("h3", class_="mb-3") or soup.find("h1")
    title = h3.get_text(strip=True) if h3 else os.path.basename(filepath)
    
    # Description (for big news only)
    summary_p = soup.find("p", class_="important") or soup.find("p")
    desc = summary_p.get_text(strip=True).replace("Summary:", "").strip() if summary_p else ""
    
    # Date
    date_span = soup.select_one(".mb-3 span:last-of-type")
    date = date_span.get_text(strip=True) if date_span else "Unknown Date"
    
    # Image
    img_tag = soup.find("img")
    img = img_tag["src"].split("/")[-1] if img_tag and img_tag.get("src") else "default.jpg"
    
    return {
        "title": title,
        "desc": desc,
        "date": date,
        "img": img,
        "file": os.path.basename(filepath)
    }

def get_latest_news(limit=None):
    html_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith(".html")]
    html_files = sorted(
        html_files,
        key=lambda f: os.path.getmtime(os.path.join(MUSIC_DIR, f)),
        reverse=True
    )
    if limit:
        html_files = html_files[:limit]
    return [extract_news_metadata(os.path.join(MUSIC_DIR, f)) for f in html_files]

def update_music_page():
    news_items = get_latest_news(14)  # 4 big + 10 small
    
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    # === Update Big News (first 4) ===
    big_news_divs = soup.select(".col-lg-6 .position-relative.mb-3")[:4]
    for div, item in zip(big_news_divs, news_items[:4]):
        # Image
        img = div.find("img")
        if img:
            img["src"] = f"/ScreamLine/img/music/{item['img']}"
        # Title link
        a_title = div.find("a", class_="h4")
        if a_title:
            a_title.string = limit_title(item["title"])
            a_title["href"] = f"/ScreamLine/music/{item['file']}"
        # Metadata (date)
        metadata_div = div.find("div", style="font-size: 14px;")
        if metadata_div:
            category_a = metadata_div.find("a", class_="text-danger")
            if category_a:
                for sibling in list(category_a.next_siblings):
                    sibling.extract()
                date_span = soup.new_tag("span", class_="px-1")
                date_span.string = item["date"]
                metadata_div.append(date_span)
        # Description
        p = div.find("p")
        if p:
            p.string = item["desc"][:150] + "..." if item["desc"] else ""
    
    # === Update Small News (next 10) ===
    small_news_container = soup.find_all("div", class_="row")[2]  # adjust if needed
    existing_blocks = small_news_container.find_all("div", class_="col-lg-6")
    
    # Remove old small news blocks
    for block in existing_blocks:
        block.decompose()
    
    # Add 10 small news blocks
    for item in news_items[4:14]:
        new_block = BeautifulSoup(f"""
        <div class="col-lg-6">
          <div class="d-flex mb-3">
            <img src="/ScreamLine/img/music/{item['img']}" style="width: 100px; height: 100px; object-fit: cover;"/>
            <div class="w-100 d-flex flex-column justify-content-center bg-light px-3" style="height: 100px;">
              <div class="mb-1" style="font-size: 13px;">
                <a class="text-danger" href="">Music</a>
                <span class="px-1">/</span>
                <span>{item['date']}</span>
              </div>
              <a class="h6 m-0" href="/ScreamLine/music/{item['file']}">{limit_title(item['title'])}</a>
            </div>
          </div>
        </div>
        """, "html.parser")
        small_news_container.append(new_block)
    
    # Save updated HTML
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    
    print("✅ music.html updated with 4 big news + 10 small news!")

if __name__ == "__main__":
    update_music_page()

