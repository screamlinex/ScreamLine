from bs4 import BeautifulSoup
import os

# Paths
BASE_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine"
INDEX_FILE = os.path.join(BASE_DIR, "index.html")
NEWS_FOLDER = os.path.join(BASE_DIR, "old news")

# Load index.html
with open(INDEX_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Function to extract news data
def extract_news(file_path, summary_words_count=20):
    with open(file_path, "r", encoding="utf-8") as f:
        news_soup = BeautifulSoup(f, "html.parser")

    # Title
    title_tag = news_soup.find("h3")
    title = title_tag.get_text(strip=True) if title_tag else "No Title"

    # --- truncate title if more than 6 words ---
    words = title.split()
    if len(words) > 7:
        title = " ".join(words[:7]) + "..."

    # Category & Date
    category = "Unknown"
    date = "Unknown"
    mb3_div = news_soup.find("div", class_="mb-3")
    if mb3_div:
        cat_tag = mb3_div.find("a", class_="text-danger")
        if cat_tag:
            category = cat_tag.get_text(strip=True)
        span_tags = mb3_div.find_all("span")
        if span_tags:
            date = span_tags[-1].get_text(strip=True)

    # Summary
    summary_tag = news_soup.find("p", class_="important")
    summary = ""
    if summary_tag:
        text = summary_tag.get_text(strip=True).replace("Summary:", "").strip()
        words = text.split()[:summary_words_count]
        summary = " ".join(words) + "..."

    # Image
    img_tag = news_soup.find("img")
    img = img_tag["src"] if img_tag else "/ScreamLine/img/news-placeholder.jpg"

    link = os.path.basename(file_path)
    return {"title": title, "category": category, "date": date, "img": img, "link": link, "summary": summary}

# Locate "Last Week" heading and its two columns
heading = soup.find("h3", string="Last Week")
columns = []
if heading:
    col12_div = heading.find_parent("div", class_="col-12")
    if col12_div:
        sibling = col12_div.find_next_sibling()
        while sibling and len(columns) < 2:
            if "col-lg-6" in sibling.get("class", []):
                columns.append(sibling)
            sibling = sibling.find_next_sibling()

# Proceed if both columns found
if len(columns) == 2:
    # Clear old news in both columns
    for col in columns:
        for div in col.find_all("div", class_=["position-relative mb-3", "d-flex mb-3"]):
            div.decompose()

    # Get latest 6 news files (2 large + 4 small)
    news_files = [f for f in os.listdir(NEWS_FOLDER) if f.endswith(".html")]
    news_files.sort(key=lambda x: os.path.getmtime(os.path.join(NEWS_FOLDER, x)), reverse=True)
    news_files = news_files[:6]

    # Add first 2 as large news (one in each column)
    for i, nf in enumerate(news_files[:2]):
        news = extract_news(os.path.join(NEWS_FOLDER, nf))
        item = soup.new_tag("div", **{"class": "position-relative mb-3"})
        img_tag = soup.new_tag("img", src=news["img"], **{"class": "img-fluid w-100", "style": "object-fit: cover;"})
        overlay = soup.new_tag("div", **{"class": "overlay position-relative bg-light"})

        # Category + date
        mb_div = soup.new_tag("div", **{"class": "mb-2", "style": "font-size: 14px;"})
        cat_a = soup.new_tag("a", href="", **{"class": "text-danger"})
        cat_a.string = news["category"]
        slash_span = soup.new_tag("span", **{"class": "px-1"})
        slash_span.string = "/"
        date_span = soup.new_tag("span")
        date_span.string = news["date"]
        mb_div.extend([cat_a, slash_span, date_span])

        # Title
        title_a = soup.new_tag("a", href=os.path.join("old news", news["link"]), **{"class": "h4"})
        title_a.string = news["title"]

        # Summary
        p_tag = soup.new_tag("p", **{"class": "m-0"})
        p_tag.string = news["summary"]

        overlay.extend([mb_div, title_a, p_tag])
        item.extend([img_tag, overlay])
        columns[i].append(item)

    # Remaining 4 as small news
    for idx, nf in enumerate(news_files[2:]):
        news = extract_news(os.path.join(NEWS_FOLDER, nf))
        col_idx = idx % 2  # alternate between the two columns
        d_flex = soup.new_tag("div", **{"class": "d-flex mb-3"})
        img_tag = soup.new_tag("img", src=news["img"], style="width: 100px; height: 100px; object-fit: cover;")
        content_div = soup.new_tag(
            "div",
            **{"class": "w-100 d-flex flex-column justify-content-center bg-light px-3", "style": "height: 100px;"}
        )

        # Category + date
        mb_div = soup.new_tag("div", **{"class": "mb-1", "style": "font-size: 13px;"})
        cat_a = soup.new_tag("a", href="", **{"class": "text-danger"})
        cat_a.string = news["category"]
        slash_span = soup.new_tag("span", **{"class": "px-1"})
        slash_span.string = "/"
        date_span = soup.new_tag("span")
        date_span.string = news["date"]
        mb_div.extend([cat_a, slash_span, date_span])

        # Title
        title_a = soup.new_tag("a", href=os.path.join("old news", news["link"]), **{"class": "h6 m-0"})
        title_a.string = news["title"]

        content_div.extend([mb_div, title_a])
        d_flex.extend([img_tag, content_div])
        columns[col_idx].append(d_flex)

# Save changes
with open(INDEX_FILE, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("Last Week News block updated successfully!")