from bs4 import BeautifulSoup
import os
from datetime import datetime
import re

# Paths
BASE_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine"
PARANORMAL_HTML = os.path.join(BASE_DIR, "global 2.html")
PARANORMAL_FOLDER = os.path.join(BASE_DIR, "global")

# --- Function to extract title, date, image, and description from a news file ---
def extract_news_info(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        # Extract title
        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else os.path.basename(filepath).replace("_", " ")

        # --- Detect date ---
        date_tag = soup.find("span", class_="date")
        if date_tag:
            date = date_tag.get_text(strip=True)
        else:
            # Search for any span with a month/day/year pattern
            date = "Unknown Date"
            for span in soup.find_all("span"):
                if re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}", span.get_text()):
                    date = span.get_text(strip=True)
                    break

        # Extract image
        img_tag = soup.find("img")
        img_src = img_tag["src"] if img_tag else "/ScreamLine/img/default.jpg"

        # Extract short description
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

# --- Step 1: Load all news files ---
news_files = sorted(
    [os.path.join(PARANORMAL_FOLDER, f) for f in os.listdir(PARANORMAL_FOLDER) if f.endswith(".html")],
    key=os.path.getmtime,
    reverse=True
)

# ✅ Skip the first 14 (i.e. take from 15th onwards)
news_files = news_files[14:]

latest_news = [extract_news_info(f) for f in news_files[:14]]
latest_news = [n for n in latest_news if n]  # remove None

# --- Step 2: Load paranormal.html ---
with open(PARANORMAL_HTML, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# --- Step 3: Update 4 big news ---
big_news_divs = soup.select(".col-lg-6 .position-relative.mb-3")[:4]
for div, news in zip(big_news_divs, latest_news[:4]):
    img_tag = div.find("img")
    if img_tag:
        img_tag["src"] = "/ScreamLine/img/global/" + os.path.basename(news["image"])

    link_tag = div.find("a", class_="h4")
    if link_tag:
        # Limit title to 6 words
        words = news["title"].split()
        link_tag.string = " ".join(words[:6]) + ("..." if len(words) > 6 else "")
        link_tag["href"] = f"/ScreamLine/global/{news['file']}"

    date_span = div.find_all("span")[-1]
    if date_span:
        date_span.string = news["date"]

    p_tag = div.find("p")
    if p_tag:
        p_tag.string = news["desc"][:120] + "..."

# --- Step 4: Update 10 small news ---
small_news_divs = soup.select("#paranormal-small-news .d-flex.mb-3")[:10]
for div, news in zip(small_news_divs, latest_news[4:14]):
    img_tag = div.find("img")
    if img_tag:
        img_tag["src"] = "/ScreamLine/img/global/" + os.path.basename(news["image"])

    link_tag = div.find("a", class_="h6")
    if link_tag:
        # Limit title to 6 words
        words = news["title"].split()
        link_tag.string = " ".join(words[:6]) + ("..." if len(words) > 6 else "")
        link_tag["href"] = f"/ScreamLine/global/{news['file']}"

    date_span = div.find_all("span")[-1]
    if date_span:
        date_span.string = news["date"]

# --- Step 5: Save back ---
with open(PARANORMAL_HTML, "w", encoding="utf-8") as f:
    f.write(str(soup.prettify()))

print("✅ Global news updated successfully! (Now detects date automatically)")