from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

# --- Paths ---
BASE_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine"
SCIFI_HTML = os.path.join(BASE_DIR, "scifi.html")
SCIFI_FOLDER = os.path.join(BASE_DIR, "scifi")

# --- Function: Extract info from each news file ---
def extract_news_info(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # --- Title ---
        title_tag = soup.find("h1") or soup.find("h3")
        title = title_tag.get_text(strip=True) if title_tag else os.path.basename(filepath).replace("_", " ")

        # --- Date Detection ---
        date = "Unknown Date"
        date_tag = soup.find("span", class_="date")
        if date_tag:
            date = date_tag.get_text(strip=True)
        else:
            # Try pattern match (e.g., October 24, 2025)
            for span in soup.find_all("span"):
                text = span.get_text()
                if re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}", text):
                    date = text.strip()
                    break

        # --- Image ---
        img_tag = soup.find("img")
        img_src = img_tag["src"] if img_tag else "/ScreamLine/img/default.jpg"
        if not img_src.startswith("/ScreamLine/"):
            img_src = "/ScreamLine/img/scifi/" + os.path.basename(img_src)

        # --- Description ---
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
        print(f"⚠️ Error parsing {filepath}: {e}")
        return None


# --- Step 1: Load and sort all news files ---
news_files = sorted(
    [os.path.join(SCIFI_FOLDER, f) for f in os.listdir(SCIFI_FOLDER) if f.endswith(".html")],
    key=os.path.getmtime,
    reverse=True
)

# Get 14 most recent for the page
latest_news = [extract_news_info(f) for f in news_files[:14]]
latest_news = [n for n in latest_news if n]

# --- Step 2: Load target HTML file ---
with open(SCIFI_HTML, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# --- Step 3: Update 4 big news ---
big_news_divs = soup.select(".col-lg-6 .position-relative.mb-3")[:4]
for div, news in zip(big_news_divs, latest_news[:4]):
    # Image
    img_tag = div.find("img")
    if img_tag:
        img_tag["src"] = news["image"]

    # Title
    link_tag = div.find("a", class_="h4")
    if link_tag:
        words = news["title"].split()
        link_tag.string = " ".join(words[:7]) + ("..." if len(words) > 7 else "")
        link_tag["href"] = f"/ScreamLine/scifi/{news['file']}"

    # Date
    date_span = div.find_all("span")[-1]
    if date_span and news["date"]:
        date_span.string = news["date"]

    # Description
    p_tag = div.find("p")
    if p_tag:
        p_tag.string = news["desc"][:120] + "..."

# --- Step 4: Update (or create) 10 small news ---
small_news_divs = soup.select("#scifi-small-news .d-flex.mb-3")[:10]

# Create missing ones if needed
if len(small_news_divs) < 10:
    container = soup.select_one("#scifi-small-news")
    if container:
        for _ in range(10 - len(small_news_divs)):
            new_block = BeautifulSoup("""
            <div class="d-flex mb-3">
              <img src="/ScreamLine/img/scifi/default.jpg" style="width:100px;height:100px;object-fit:cover;"/>
              <div class="w-100 d-flex flex-column justify-content-center bg-light px-3" style="height:100px;">
                <div class="mb-1" style="font-size:13px;">
                  <a class="text-danger" href="">Sci-Fi</a>
                  <span class="px-1">/</span>
                  <span>October 24, 2025</span>
                </div>
                <a class="h6 m-0" href="#">Default News Title</a>
              </div>
            </div>
            """, "html.parser")
            container.append(new_block)
    small_news_divs = soup.select("#scifi-small-news .d-flex.mb-3")[:10]

for div, news in zip(small_news_divs, latest_news[4:14]):
    # Image
    img_tag = div.find("img")
    if img_tag:
        img_tag["src"] = news["image"]

    # Title
    link_tag = div.find("a", class_="h6")
    if link_tag:
        words = news["title"].split()
        link_tag.string = " ".join(words[:8]) + ("..." if len(words) > 8 else "")
        link_tag["href"] = f"/ScreamLine/scifi/{news['file']}"

    # Date
    date_span = div.find_all("span")[-1]
    if date_span and news["date"]:
        date_span.string = news["date"]

# --- Step 5: Save ---
with open(SCIFI_HTML, "w", encoding="utf-8") as f:
    f.write(str(soup.prettify()))

print("✅ Sci-Fi news updated successfully! (4 big + 10 small, with auto date/image handling)")
