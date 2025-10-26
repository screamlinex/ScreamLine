import os
from bs4 import BeautifulSoup
import re

# Paths
BASE_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine"
SCIFI_HTML = os.path.join(BASE_DIR, "scifi 3.html")
SCIFI_FOLDER = os.path.join(BASE_DIR, "scifi")

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

        # Date: span.date or last span in .mb-3 or regex search
        date_tag = soup.find("span", class_="date")
        if not date_tag:
            date_container = soup.find("div", class_="mb-3")
            if date_container:
                spans = date_container.find_all("span")
                if spans:
                    date_tag = spans[-1]
        if not date_tag:
            # fallback regex over spans
            for span in soup.find_all("span"):
                text = span.get_text()
                if re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}", text):
                    date_tag = span
                    break
        date = date_tag.get_text(strip=True) if date_tag else "Unknown Date"

        # Image (use basename)
        img_tag = soup.find("img")
        img_src = img_tag["src"].split("/")[-1] if img_tag and img_tag.get("src") else "default.jpg"

        # Description (first meaningful p)
        p_tag = None
        for p in soup.find_all("p"):
            txt = p.get_text(strip=True)
            if txt:
                p_tag = p
                break
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
    html_files = [os.path.join(SCIFI_FOLDER, f) for f in os.listdir(SCIFI_FOLDER) if f.lower().endswith(".html")]
    html_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    selected = html_files[start_index:start_index + limit]
    items = [extract_news_info(f) for f in selected]
    return [i for i in items if i]

def update_scifi_page():
    news_items = get_news_files(28, 14)  # get news from 15th onward (14 skipped)
    if not news_items:
        print("No news to update.")
        return

    with open(SCIFI_HTML, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # --- Update 4 Big News ---
    big_news_divs = soup.select(".col-lg-6 .position-relative.mb-3")[:4]
    for div, news in zip(big_news_divs, news_items[:4]):
        img_tag = div.find("img")
        if img_tag:
            img_tag["src"] = f"/ScreamLine/img/scifi/{news['image']}"
        link_tag = div.find("a", class_="h4")
        if link_tag:
            link_tag.string = limit_title(news["title"])
            link_tag["href"] = f"/ScreamLine/scifi/{news['file']}"
        date_span = div.find_all("span")[-1]
        if date_span:
            date_span.string = news["date"]
        p_tag = div.find("p")
        if p_tag:
            p_tag.string = news["desc"][:120] + "..." if news["desc"] else ""

    # --- Update 10 Small News ---
    # use the same container approach as the music script
    rows = soup.find_all("div", class_="row")
    if len(rows) < 3:
        print("Cannot find small-news container (expected 3rd .row). Aborting small news update.")
    else:
        small_news_container = rows[2]  # adjust if your page layout differs
        # remove existing small-news col-lg-6 blocks
        existing_blocks = small_news_container.find_all("div", class_="col-lg-6")
        for block in existing_blocks:
            block.decompose()

        # append up to 10 small news (news_items[4:14])
        for news in news_items[4:14]:
            new_block = BeautifulSoup(f"""
            <div class="col-lg-6">
              <div class="d-flex mb-3">
                <img src="/ScreamLine/img/scifi/{news['image']}" style="width: 100px; height: 100px; object-fit: cover;"/>
                <div class="w-100 d-flex flex-column justify-content-center bg-light px-3" style="height: 100px;">
                  <div class="mb-1" style="font-size: 13px;">
                    <a class="text-danger" href="">Sci-Fi</a>
                    <span class="px-1">/</span>
                    <span>{news['date']}</span>
                  </div>
                  <a class="h6 m-0" href="/ScreamLine/scifi/{news['file']}">{limit_title(news['title'])}</a>
                </div>
              </div>
            </div>
            """, "html.parser")
            small_news_container.append(new_block)

    # Save updated HTML
    with open(SCIFI_HTML, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    print("✅ scifi 2.html updated with 4 big news + 10 small news!")

if __name__ == "__main__":
    update_scifi_page()
