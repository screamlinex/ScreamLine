from bs4 import BeautifulSoup
import os

# --- Paths ---
BASE_DIR = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine"
TRENDING_DIR = os.path.join(BASE_DIR, "trending")
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates", "bottom-news.html")

# --- Allowed categories ---
ALLOWED_CATEGORIES = {"Music", "Movies & TV Shows"}


# --- Extract news info from HTML ---
def extract_news_info(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Title
    title_tag = soup.find("h3")
    title = title_tag.get_text(strip=True) if title_tag else "Untitled"

    # Truncate title if too long
    words = title.split()
    if len(words) > 8:
        title = " ".join(words[:8]) + "..."

    # Category
    category_tag = soup.select_one(".overlay .mb-3 a.text-danger, .overlay .mb-2 a.text-danger")
    category = category_tag.get_text(strip=True) if category_tag else "Unknown"

    # Date
    mb_div = soup.select_one(".overlay .mb-3, .overlay .mb-2")
    date = "Unknown"
    if mb_div:
        spans = mb_div.find_all("span")
        if spans:
            date = spans[-1].get_text(strip=True)

    # Image
    img_tag = soup.select_one(".position-relative.mb-3 img, .position-relative img")
    img = img_tag["src"] if img_tag else "/ScreamLine/img/news-placeholder.jpg"

    # Link
    link = f"/ScreamLine/trending/{os.path.basename(file_path)}"

    return {"title": title, "category": category, "date": date, "img": img, "link": link}


# --- Build updated HTML ---
def update_bottom_news():
    # Collect all .html news files in trending folder
    news_files = [f for f in os.listdir(TRENDING_DIR) if f.endswith(".html")]
    if not news_files:
        print("No news found in trending folder.")
        return

    # Sort by oldest → newest
    news_files.sort(key=lambda x: os.path.getmtime(os.path.join(TRENDING_DIR, x)))

    filtered_news = []
    for nf in news_files:
        file_path = os.path.join(TRENDING_DIR, nf)
        news = extract_news_info(file_path)
        if news["category"] in ALLOWED_CATEGORIES:
            filtered_news.append(news)
        if len(filtered_news) >= 4:
            break  # stop after 4

    if not filtered_news:
        print("No 'Music' or 'Movies & TV Shows' news found.")
        return

    # --- Build new HTML structure ---
    soup = BeautifulSoup("", "html.parser")

    # Add the ad image DIV at the top (you asked for this)
    ad_div = soup.new_tag("div", **{"class": "mb-3"})
    ad_a = soup.new_tag("a", href="")
    ad_img = soup.new_tag("img", **{"class": "img-fluid w-100", "src": "/ScreamLine/img/ads-700x70.jpg", "alt": ""})
    ad_a.append(ad_img)
    ad_div.append(ad_a)
    soup.append(ad_div)

    # Row wrapper for the 4 items
    wrapper = soup.new_tag("div", **{"class": "row"})
    soup.append(wrapper)

    for news in filtered_news:
        col = soup.new_tag("div", **{"class": "col-lg-6"})
        d_flex = soup.new_tag("div", **{"class": "d-flex mb-3"})

        img_tag = soup.new_tag("img", src=news["img"])
        img_tag["style"] = "width: 100px; height: 100px; object-fit: cover;"

        content_div = soup.new_tag(
            "div",
            **{
                "class": "w-100 d-flex flex-column justify-content-center bg-light px-3",
                "style": "height: 100px;",
            },
        )

        mb_div = soup.new_tag("div", **{"class": "mb-1", "style": "font-size: 13px;"})
        cat_a = soup.new_tag("a", href="", **{"class": "text-danger"})
        cat_a.string = news["category"]

        slash = soup.new_tag("span", **{"class": "px-1"})
        slash.string = "/"

        date_span = soup.new_tag("span")
        date_span.string = news["date"]

        mb_div.append(cat_a)
        mb_div.append(slash)
        mb_div.append(date_span)

        title_a = soup.new_tag("a", href=news["link"], **{"class": "h6 m-0"})
        title_a.string = news["title"]

        content_div.append(mb_div)
        content_div.append(title_a)

        d_flex.append(img_tag)
        d_flex.append(content_div)
        col.append(d_flex)
        wrapper.append(col)

    # --- Write to bottom-news.html ---
    with open(TEMPLATE_FILE, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print("✅ bottom-news.html updated with ad + 4 oldest 'Music' or 'Movies & TV Shows' news!")


# --- Run the update ---
if __name__ == "__main__":
    update_bottom_news()
