import os
import re
from pathlib import Path
from bs4 import BeautifulSoup

# --- Paths ---
TRENDING_DIR = Path(r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\trending")
HEADER_FILE = Path(r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\templates\header.html")

# --- Step 1: Get the 3 newest news files ---
all_files = sorted(
    [f for f in TRENDING_DIR.glob("*.html") if f.is_file()],
    key=lambda f: f.stat().st_mtime,
    reverse=True
)[:3]

if not all_files:
    print("⚠️ No news files found in trending folder.")
    exit()

# --- Step 2: Extract title + category + relative link ---
news_items = []
for file in all_files:
    try:
        with open(file, "r", encoding="utf-8") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")

        # Extract title
        title_tag = soup.find("h3", class_="mb-3")
        title = title_tag.get_text(strip=True) if title_tag else file.stem

        # Extract category from breadcrumb link
        breadcrumb = soup.find("a", href=re.compile(r"/ScreamLine/(music|movies-tv|scifi|global)\.html"))
        category = breadcrumb["href"].split("/")[-1].replace(".html", "") if breadcrumb else "unknown"

        # Build link (consistent with your HTML structure)
        relative_path = f"/ScreamLine/{category}/{file.name}"

        news_items.append({"title": title, "link": relative_path})
        print(f"✅ Found: {title}  ({category})")

    except Exception as e:
        print(f"⚠️ Error reading {file}: {e}")

# --- Step 3: Update header.html ---
with open(HEADER_FILE, "r", encoding="utf-8") as f:
    header_html = f.read()

# Replace the ticker content
pattern = r'(<div class="ticker-content">)(.*?)(</div>)'
new_ticker_html = "\n".join(
    [f'                    <span><a href="{item["link"]}" class="text-white">{item["title"]}</a></span>' for item in news_items]
)
new_header = re.sub(pattern, r"\1\n" + new_ticker_html + r"\n                \3", header_html, flags=re.S)

# Write back
with open(HEADER_FILE, "w", encoding="utf-8") as f:
    f.write(new_header)

print("🎯 header.html successfully updated with the latest 3 news articles.")
