import os
from bs4 import BeautifulSoup

# Paths
BASE_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine"
MOVIES_TV_DIR = os.path.join(BASE_DIR, "movies-tv")
HTML_FILE = os.path.join(BASE_DIR, "movies-tv 3.html")

def limit_title(title, max_words=6):
    """Limit title length for display."""
    words = title.split()
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")

def extract_metadata(filepath):
    """Extract title, date, image, description, and filename from a news HTML file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # Title
        h3 = soup.find("h3", class_="mb-3") or soup.find("h1")
        title = h3.get_text(strip=True) if h3 else os.path.basename(filepath)

        # Date
        date_span = soup.select_one(".mb-3 span:last-of-type")
        date = date_span.get_text(strip=True) if date_span else "Unknown Date"

        # Summary
        summary_p = soup.find("p", class_="important")
        desc = summary_p.get_text(strip=True).replace("Summary:", "").strip() if summary_p else "Read more..."

        # Image
        img_tag = soup.find("img")
        img_src = img_tag["src"].split("/")[-1] if img_tag and img_tag.get("src") else "default.jpg"

        return {
            "title": title,
            "desc": desc,
            "date": date,
            "img": img_src,
            "file": os.path.basename(filepath),
            "path": filepath
        }

    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None

def get_news_files(start_index=28, limit=14):
    """Get sorted news files starting from a given offset."""
    html_files = [os.path.join(MOVIES_TV_DIR, f) for f in os.listdir(MOVIES_TV_DIR) if f.endswith(".html")]
    html_files.sort(key=os.path.getmtime, reverse=True)
    selected = html_files[start_index:start_index + limit]
    items = [extract_metadata(f) for f in selected]
    return [i for i in items if i]

def update_movies_tv_page():
    news_items = get_news_files(28, 14)  # Skip first 14, get next 14
    if not news_items:
        print("No news found to update.")
        return

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # --- Update 4 Big News ---
    big_news_divs = soup.select(".col-lg-6 .position-relative.mb-3")[:4]
    for div, item in zip(big_news_divs, news_items[:4]):
        img_tag = div.find("img")
        if img_tag:
            img_tag["src"] = f"/ScreamLine/img/movies-tv/{item['img']}"
        link_tag = div.find("a", class_="h4")
        if link_tag:
            link_tag.string = limit_title(item["title"])
            link_tag["href"] = f"/ScreamLine/movies-tv/{item['file']}"
        date_span = div.find_all("span")[-1]
        if date_span:
            date_span.string = item["date"]
        p_tag = div.find("p")
        if p_tag:
            p_tag.string = item["desc"][:150] + "..." if item["desc"] else ""

    # --- Update 10 Small News ---
    rows = soup.find_all("div", class_="row")
    if len(rows) < 3:
        print("❌ Could not find small-news container (expected 3rd .row).")
        return

    small_news_container = rows[2]
    # Remove existing small-news blocks
    existing_blocks = small_news_container.find_all("div", class_="col-lg-6")
    for block in existing_blocks:
        block.decompose()

    # Add new 10 small news
    for item in news_items[4:14]:
        new_block = BeautifulSoup(f"""
        <div class="col-lg-6">
            <div class="d-flex mb-3">
                <img src="/ScreamLine/img/movies-tv/{item['img']}" style="width:100px; height:100px; object-fit:cover;"/>
                <div class="w-100 d-flex flex-column justify-content-center bg-light px-3" style="height:100px;">
                    <div class="mb-1" style="font-size:13px;">
                        <a class="text-danger" href="">Movies & TV</a>
                        <span class="px-1">/</span>
                        <span>{item['date']}</span>
                    </div>
                    <a class="h6 m-0" href="/ScreamLine/movies-tv/{item['file']}">{limit_title(item['title'])}</a>
                </div>
            </div>
        </div>
        """, "html.parser")
        small_news_container.append(new_block)

    # Save updates
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    print("✅ movies-tv 2.html updated successfully with 4 big + 10 small news (from 15th onward)!")

if __name__ == "__main__":
    update_movies_tv_page()
