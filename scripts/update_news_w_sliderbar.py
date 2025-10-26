from bs4 import BeautifulSoup
import os
import random

# Paths
BASE_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine"
INDEX_FILE = os.path.join(BASE_DIR, "index.html")
TRENDING_FOLDER = os.path.join(BASE_DIR, "trending")

# Load index.html
with open(INDEX_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Function to extract news data
def extract_news(file_path, include_summary=False):
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
    mb_div = news_soup.select_one(".overlay .mb-3, .overlay .mb-2, p")  # look inside overlay first
    if mb_div:
        cat_tag = mb_div.find("a", class_="text-danger")
        if cat_tag:
            category = cat_tag.get_text(strip=True)
        span_tags = mb_div.find_all("span")
        if span_tags:
            date = span_tags[-1].get_text(strip=True)
    
    # Image
    img_tag = news_soup.find("img")
    img = img_tag["src"] if img_tag else "/ScreamLine/img/news-placeholder.jpg"
    
    # Summary paragraph (20 words)
    summary_text = ""
    if include_summary:
        summary_tag = news_soup.select_one('p.important')
        if summary_tag:
            words = summary_tag.get_text(strip=True).split()
            summary_text = " ".join(words[1:21])  # Skip 'Summary:' and take 20 words
    
    link = os.path.basename(file_path)
    return {"title": title, "category": category, "date": date, "img": img, "link": link, "summary": summary_text}

# Pick random trending news
news_files = [f for f in os.listdir(TRENDING_FOLDER) if f.endswith(".html")]
random.shuffle(news_files)

# Find both col-lg-6 columns in Popular
popular_section = soup.find("h3", string="Popular").find_parent("div", class_="row mb-3")
columns = popular_section.find_all("div", class_="col-lg-6")

# Process each column
file_idx = 0
for col in columns:
    # Clear old content
    for child in col.find_all(recursive=False):
        child.decompose()
    
    # First news with summary
    if file_idx >= len(news_files):
        break
    news = extract_news(os.path.join(TRENDING_FOLDER, news_files[file_idx]), include_summary=True)
    file_idx += 1
    
    # Large news block
    div_block = soup.new_tag("div", **{"class": "position-relative mb-3"})
    img_tag = soup.new_tag("img", src=news["img"], **{"class": "img-fluid w-100", "style": "object-fit: cover;"})
    overlay = soup.new_tag("div", **{"class": "overlay position-relative bg-light"})
    
    mb_div = soup.new_tag("div", **{"class": "mb-2", "style": "font-size: 14px;"})
    cat_a = soup.new_tag("a", href=f"trending/{news['link']}", **{"class": "text-danger"})
    cat_a.string = news["category"]
    span_sep = soup.new_tag("span", **{"class": "px-1"})
    span_sep.string = "/"
    span_date = soup.new_tag("span")
    span_date.string = news["date"]
    mb_div.extend([cat_a, span_sep, span_date])
    
    title_a = soup.new_tag("a", href=f"trending/{news['link']}", **{"class": "h4"})
    title_a.string = news["title"]
    
    summary_p = soup.new_tag("p", **{"class": "m-0"})
    summary_p.string = news["summary"] + "..."
    
    overlay.extend([mb_div, title_a, summary_p])
    div_block.extend([img_tag, overlay])
    col.append(div_block)
    
    # Next 3 small news blocks
    for _ in range(3):
        if file_idx >= len(news_files):
            break
        news = extract_news(os.path.join(TRENDING_FOLDER, news_files[file_idx]), include_summary=False)
        file_idx += 1
        
        div_block = soup.new_tag("div", **{"class": "d-flex mb-3"})
        img_tag = soup.new_tag("img", src=news["img"], style="width: 100px; height: 100px; object-fit: cover;")
        info_div = soup.new_tag("div", **{"class": "w-100 d-flex flex-column justify-content-center bg-light px-3", "style": "height: 100px;"})
        
        mb_inner = soup.new_tag("div", **{"class": "mb-1", "style": "font-size: 13px;"})
        cat_a = soup.new_tag("a", href=f"trending/{news['link']}", **{"class": "text-danger"})
        cat_a.string = news["category"]
        span_sep = soup.new_tag("span", **{"class": "px-1"})
        span_sep.string = "/"
        span_date = soup.new_tag("span")
        span_date.string = news["date"]
        mb_inner.extend([cat_a, span_sep, span_date])
        
        title_a = soup.new_tag("a", href=f"/ScreamLine/trending/{news['link']}", **{"class": "h6 m-0"})
        title_a.string = news["title"]
        
        info_div.extend([mb_inner, title_a])
        div_block.extend([img_tag, info_div])
        col.append(div_block)

# Save changes
with open(INDEX_FILE, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("Popular news block updated with trending news successfully!")