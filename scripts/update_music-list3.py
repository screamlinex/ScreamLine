import os
from bs4 import BeautifulSoup

# Paths
BASE_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine"
MUSIC_HTML = os.path.join(BASE_DIR, "music 3.html")
MUSIC_FOLDER = os.path.join(BASE_DIR, "music")

def limit_title(title, max_words=6):
    words = title.split()
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")

def extract_news_info(filepath):
    """Extract title, date, image, description, and filename from a news HTML file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        
        # Title
        title_tag = soup.find("h1") or soup.find("h3")
        title = title_tag.get_text(strip=True) if title_tag else os.path.basename(filepath).replace("_", " ")

        # Date
        date_tag = soup.find("span", class_="date")
        if not date_tag:
            date_container = soup.find("div", class_="mb-3")
            if date_container:
                spans = date_container.find_all("span")
                if spans:
                    date_tag = spans[-1]
        date = date_tag.get_text(strip=True) if date_tag else "Unknown Date"

        # Image
        img_tag = soup.find("img")
        img_src = img_tag["src"].split("/")[-1] if img_tag else "default.jpg"

        # Description
        p_tag = soup.find("p")
        desc = p_tag.get_text(strip=True) if p_tag else "Read more..."

        return {
            "title": title,
            "date": date,
            "image": img_src,
            "desc": desc,
            "file": os.path.basename(filepath)
        }

    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None

def get_news_files(start_index=28, limit=14):
    """Get sorted news files starting from a certain index (skip first N newest)"""
    html_files = [os.path.join(MUSIC_FOLDER, f) for f in os.listdir(MUSIC_FOLDER) if f.endswith(".html")]
    html_files.sort(key=os.path.getmtime, reverse=True)
    selected_files = html_files[start_index:start_index + limit]
    news_items = [extract_news_info(f) for f in selected_files]
    return [n for n in news_items if n]

def update_music_page():
    news_items = get_news_files(28, 14)  # get news from 29th onward
    if not news_items:
        print("No news to update.")
        return

    with open(MUSIC_HTML, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # --- Update 4 Big News ---
    big_news_divs = soup.select(".col-lg-6 .position-relative.mb-3")[:4]
    for div, news in zip(big_news_divs, news_items[:4]):
        img_tag = div.find("img")
        if img_tag:
            img_tag["src"] = f"/ScreamLine/img/music/{news['image']}"
        
        link_tag = div.find("a", class_="h4")
        if link_tag:
            link_tag.string = limit_title(news["title"])
            link_tag["href"] = f"/ScreamLine/music/{news['file']}"
        
        date_span = div.find_all("span")[-1]
        if date_span:
            date_span.string = news["date"]
        
        p_tag = div.find("p")
        if p_tag:
            p_tag.string = news["desc"][:120] + "..." if news["desc"] else ""

    # --- Update 10 Small News ---
    small_news_container = soup.find_all("div", class_="row")[2]  # adjust if needed
    # remove old small news blocks
    existing_blocks = small_news_container.find_all("div", class_="col-lg-6")
    for block in existing_blocks:
        block.decompose()
    
    for news in news_items[4:14]:
        new_block = BeautifulSoup(f"""
        <div class="col-lg-6">
            <div class="d-flex mb-3">
                <img src="/ScreamLine/img/music/{news['image']}" style="width: 100px; height: 100px; object-fit: cover;"/>
                <div class="w-100 d-flex flex-column justify-content-center bg-light px-3" style="height: 100px;">
                    <div class="mb-1" style="font-size: 13px;">
                        <a class="text-danger" href="">Music</a>
                        <span class="px-1">/</span>
                        <span>{news['date']}</span>
                    </div>
                    <a class="h6 m-0" href="/ScreamLine/music/{news['file']}">{limit_title(news['title'])}</a>
                </div>
            </div>
        </div>
        """, "html.parser")
        small_news_container.append(new_block)

    with open(MUSIC_HTML, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    print("✅ music 2.html updated with 4 big news + 10 small news!")

if __name__ == "__main__":
    update_music_page()