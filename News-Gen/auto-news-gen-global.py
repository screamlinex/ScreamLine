#!/usr/bin/env python3
"""
auto-news-gen-paranormal.py
- Uses Groq API (Mixtral) to generate structured HTML articles for Paranormal news.
- Downloads a main image (og:image, twitter:image, first <img>) or generates one via AI if scraping fails.
- Saves generated article HTML to OUTPUT_DIR and tracks seen links in seen.json.
"""

import os
import re
import json
import datetime
import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import base64

# Groq client
from groq import Groq

# ---------------- CONFIG ----------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise SystemExit("Set GROQ_API_KEY environment variable (or add to .env).")

client = Groq(api_key=GROQ_API_KEY)

CATEGORY = "global"
FEEDS = [
   "https://feeds.bbci.co.uk/news/world/rss.xml",
"https://rss.cnn.com/rss/edition_world.rss",
"https://www.aljazeera.com/xml/rss/all.xml",
"https://www.france24.com/en/rss",
"https://feeds.npr.org/1004/rss.xml",
"https://feeds.feedburner.com/time/world",
"https://feeds.feedburner.com/ndtvworld",
"https://rssfeeds.usatoday.com/usatoday-NewsTopStories", 
"https://feeds.nbcnews.com/nbcnews/public/news",
"https://feeds.reuters.com/Reuters/worldNews"
]
OUTPUT_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\global"
IMAGE_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\img\global"
SEEN_FILE = os.path.join(OUTPUT_DIR, "seen_global.json")
MAX_PER_RUN = 5

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

CATEGORY_PAGE = "/global.html"

# ---------------- helpers ----------------
def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_seen(seen_set):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(seen_set)), f, ensure_ascii=False, indent=2)

def fetch_news(feed_urls):
    items = []
    now = datetime.datetime.now()
    for url in feed_urls:
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries:
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime.datetime(*entry.published_parsed[:6])
                    age_days = (now - published).days
                    if age_days > 7:
                        continue
                    published_str = published.strftime("%B %d, %Y")
                else:
                    published_str = now.strftime("%B %d, %Y")
                link = getattr(entry, "link", None)
                title = getattr(entry, "title", "").strip()
                summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
                if title and link:
                    items.append({
                        "title": title,
                        "link": link,
                        "summary": summary,
                        "published": published_str
                    })
        except Exception as e:
            print(f"[fetch_news] error parsing {url}: {e}")
    seen_links = set()
    dedup = []
    for it in items:
        if it['link'] not in seen_links:
            dedup.append(it)
            seen_links.add(it['link'])
    return dedup

def safe_filename(text, ext="html", limit=60):
    name = "".join(c if (c.isalnum() or c in " -_") else "_" for c in text).strip()
    name = re.sub(r"\s+", "_", name)
    return (name[:limit].rstrip("_") + f".{ext}")

def download_image_from_url(img_url, folder, title):
    if not img_url:
        return f"/ScreamLine/img/{CATEGORY}/dummy.jpg"
    try:
        resp = requests.get(img_url, timeout=10)
        if resp.status_code == 200 and resp.content:
            ext = "jpg"
            m = re.search(r"\.([a-zA-Z0-9]{2,4})(?:\?|$)", img_url)
            if m:
                ext = m.group(1).lower()
                if ext not in ("jpg", "jpeg", "png", "webp", "gif"):
                    ext = "jpg"
            fn = safe_filename(title, ext=ext)
            path = os.path.join(folder, fn)
            with open(path, "wb") as f:
                f.write(resp.content)
            return f"/ScreamLine/img/{CATEGORY}/{fn}"
    except Exception:
        pass
    return f"/ScreamLine/img/{CATEGORY}/dummy.jpg"

def generate_image_via_groq(prompt, folder, title):
    """Generate an AI image via Groq API and save it locally."""
    try:
        resp = client.images.generate(
            prompt=prompt,
            size="1024x1024",
            n=1
        )
        img_data = base64.b64decode(resp.data[0].b64_json)
        fn = safe_filename(title, ext="png")
        path = os.path.join(folder, fn)
        with open(path, "wb") as f:
            f.write(img_data)
        return f"/ScreamLine/img/{CATEGORY}/{fn}"
    except Exception as e:
        print(f"[generate_image_via_groq] error: {e}")
        return f"/ScreamLine/img/{CATEGORY}/dummy.jpg"

def scrape_best_image(article_url, title="", summary=""):
    try:
        resp = requests.get(article_url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        if resp.status_code != 200:
            raise Exception("Bad status code")
        soup = BeautifulSoup(resp.text, "html.parser")
        meta = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name":"og:image"})
        if meta and meta.get("content"):
            return download_image_from_url(meta["content"], IMAGE_DIR, article_url)
        meta2 = soup.find("meta", attrs={"name":"twitter:image"})
        if meta2 and meta2.get("content"):
            return download_image_from_url(meta2["content"], IMAGE_DIR, article_url)
        img = soup.find("img")
        if img and img.get("src"):
            return download_image_from_url(img["src"], IMAGE_DIR, article_url)
    except Exception:
        pass
    prompt = f"Paranormal news article: {title}. {summary}"
    return generate_image_via_groq(prompt, IMAGE_DIR, title)

def generate_article_via_groq(title, summary):
    system = (
        "You are a professional entertainment reporter. Output ONLY the inner HTML content that "
        "will be inserted inside <div class=\"hero\">. "
        "Start with a single <p class=\"important\"><strong>Summary:</strong> ...</p>. "
        "Then provide 2–5 <section> blocks with <h4> heading and one or more <p> paragraphs."
    )
    prompt = f"Title: {title}\n\nSummary: {summary}\n\nWrite the article content."
    try:
        resp = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            model="openai/gpt-oss-20b",
            temperature=0.7,
            max_completion_tokens=1200
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[generate_article_via_groq] error: {e}")
        safe_summary = summary or ""
        return f'<p class="important"><strong>Summary:</strong> {safe_summary}</p><section><h4>Summary</h4><p>{safe_summary}</p></section>'

def wrap_html(title, date, hero_inner_html, image_path):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>ScreamLine</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="/ScreamLine/img/favicon.png" rel="icon">
    <link rel="stylesheet" href="/ScreamLine/css/style.css">
    <link href="/ScreamLine/lib/owlcarousel/assets/owl.carousel.min.css" rel="stylesheet">
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.0/css/all.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
</head>
</head>
<body>
<div id="header"></div>
<div class="container-fluid">
    <div class="container">
        <nav class="breadcrumb bg-transparent m-0 p-0">
            <a class="breadcrumb-item text-danger" href="/ScreamLine/index.html">Home</a>
            <a class="breadcrumb-item text-danger" href="#">Category</a>
            <a class="breadcrumb-item text-danger" href="/ScreamLine/global.html">Global News</a>
            <span class="breadcrumb-item active"></span>
        </nav>
    </div>
</div>
<div class="container-fluid py-3">
    <div class="container">
        <div class="row">
            <div class="col-lg-8">
                <div class="position-relative mb-3">
                    <img class="img-fluid w-100" src="{image_path}" style="object-fit: cover;">
                    <div class="overlay position-relative bg-light">
                        <div class="mb-3">
                            <a href="" class="text-danger">Global News</a>
                            <span class="px-1">/</span>
                            <span>{date}</span>
                        </div>
                        <div>
                            <h3 class="mb-3">{title}</h3>
                            <div class="hero">
                                {hero_inner_html}
                            </div>
                        </div>
                    </div>
                </div>
                <div id="bottom-news"></div>
            </div>
            <div class="col-lg-4" id="sidebar"></div>
        </div>
    </div>
</div>
<div id="footer"></div>
<a href="#" class="btn btn-dark back-to-top"><i class="fa fa-angle-up"></i></a>
<script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.bundle.min.js"></script>
<script src="/ScreamLine/lib/easing/easing.min.js"></script>
<script src="/ScreamLine/lib/owlcarousel/owl.carousel.min.js"></script>
<script src="/ScreamLine/mail/jqBootstrapValidation.min.js"></script>
<script src="/ScreamLine/mail/contact.js"></script>
<script src="/ScreamLine/js/main.js"></script>
<script src="/ScreamLine/js/load-templates.js"></script>
</body>
</html>"""

# ---------------- main ----------------
def main():
    # ✅ image crop check disabled
    print("⚠️  Image crop check disabled — continuing without verifying imagecrop.py.")
    seen = load_seen()
    all_news = fetch_news(FEEDS)
    new_items = [n for n in all_news if n['link'] not in seen]

    if not new_items:
        print("No more latest news, try again in an hour.")
        return

    to_process = new_items[:MAX_PER_RUN]
    for item in to_process:
        title = item['title']
        link = item['link']
        published = item.get('published', datetime.datetime.now().strftime("%B %d, %Y"))
        summary = item.get('summary', "")

        print("Generating article:", title)
        hero_html = generate_article_via_groq(title, summary)
        image_path = scrape_best_image(link, title=title, summary=summary)
        fname = safe_filename(title, ext="html")
        filepath = os.path.join(OUTPUT_DIR, fname)
        html = wrap_html(title, published, hero_html, image_path)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved:", filepath)
        seen.add(link)

    save_seen(seen)
    print("Done.")

if __name__ == "__main__":
    main()