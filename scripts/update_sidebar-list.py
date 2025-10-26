import os
from bs4 import BeautifulSoup
from datetime import datetime

TRENDING_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\trending"
SIDEBAR_FILE = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\templates\sidebar.html"

def get_latest_trending_files(folder, count=5):
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".html")]
    files.sort(key=os.path.getmtime, reverse=True)
    return files[:count]

def extract_info_from_html(filepath):
    """Extract title, category, date, and image from your news file."""
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Title: <h3 class="mb-3">...</h3>
    title_tag = soup.find("h3", class_="mb-3")
    title = title_tag.get_text(strip=True) if title_tag else os.path.basename(filepath).replace("_", " ").replace(".html", "")
    title_words = title.split()
    if len(title_words) > 7:
        title = " ".join(title_words[:7]) + "..."

    # Category: <div class="mb-3"><a class="text-danger">Category</a> ...
    cat_tag = soup.select_one("div.mb-3 a.text-danger")
    category = cat_tag.get_text(strip=True) if cat_tag else "News"

    # Date: look inside the same parent div.mb-3 and take the last <span>
    date = None
    if cat_tag:
        parent_div = cat_tag.parent
        if parent_div:
            spans = parent_div.find_all("span")
            # Prefer the last span if exists and looks like a date
            if spans:
                date_candidate = spans[-1].get_text(strip=True)
                if date_candidate:
                    date = date_candidate

    # Fallback to file modification time if date not found
    if not date:
        date = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%B %d, %Y")

    # Image: first main image with class img-fluid (or any img if none)
    img_tag = soup.find("img", class_="img-fluid")
    if not img_tag:
        img_tag = soup.find("img")
    image = img_tag["src"] if img_tag and img_tag.get("src") else "/img/default.jpg"

    return {
        "title": title,
        "category": category,
        "date": date,
        "image": image,
        "link": f"/ScreamLine/trending/{os.path.basename(filepath)}"
    }

def build_trending_html(items):
    blocks = []
    for item in items:
        block = f"""
  <div class="d-flex mb-3">
   <img src="{item['image']}" style="width: 100px; height: 100px; object-fit: cover;"/>
   <div class="w-100 d-flex flex-column justify-content-center bg-dark px-3" style="height: 100px;">
    <div class="mb-1" style="font-size: 13px;">
     <a class="text-danger" href="">{item['category']}</a>
     <span class="px-1">/</span>
     <span>{item['date']}</span>
    </div>
    <a class="h6 m-0" href="{item['link']}">{item['title']}</a>
   </div>
  </div>"""
        blocks.append(block)
    return "\n".join(blocks)

def update_sidebar():
    print("Updating sidebar with latest trending news...")
    trending_files = get_latest_trending_files(TRENDING_DIR)
    news_items = [extract_info_from_html(f) for f in trending_files]

    with open(SIDEBAR_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    start_tag = "<!-- Popular News Start -->"
    end_tag = "<!-- Popular News End -->"
    start_idx = html.find(start_tag)
    end_idx = html.find(end_tag)

    if start_idx == -1 or end_idx == -1:
        print("❌ Could not find trending section in sidebar.html")
        return

    before = html[:start_idx + len(start_tag)]
    after = html[end_idx:]

    new_trending = f"""\n <div class="pb-3">
  <div class="bg-red py-2 px-4 mb-3">
   <h3 class="m-0">Trending</h3>
  </div>
{build_trending_html(news_items)}
 </div>\n"""

    updated_html = before + new_trending + after

    with open(SIDEBAR_FILE, "w", encoding="utf-8") as f:
        f.write(updated_html)

    print(f"✅ Sidebar updated with {len(news_items)} trending items!")

if __name__ == "__main__":
    update_sidebar()