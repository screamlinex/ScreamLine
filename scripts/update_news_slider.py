import os
from bs4 import BeautifulSoup, Comment

# --- Paths ---
index_file_path = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\index.html"
trending_folder = r"C:\Users\LOQ\Downloads\ScreamLine\ScreamLine\trending"

# --- Load index.html ---
with open(index_file_path, "r", encoding="utf-8") as f:
    index_soup = BeautifulSoup(f, "html.parser")

# --- Find Top News Slider comments robustly ---
comments = index_soup.find_all(string=lambda text: isinstance(text, Comment))
start_comment = None
end_comment = None

for c in comments:
    text = c.strip().lower()
    if "top news slider start" in text:
        start_comment = c
    elif "top news slider end" in text:
        end_comment = c

if not start_comment or not end_comment:
    raise Exception("Could not find <!-- Top News Slider Start --> or <!-- Top News Slider End --> in index.html")

# --- Remove old slider content ---
current = start_comment.next_sibling
while current and current != end_comment:
    next_elem = current.next_sibling
    current.extract()
    current = next_elem

# --- Collect latest 6 trending articles ---
trending_files = sorted(
    [f for f in os.listdir(trending_folder) if f.endswith(".html")],
    key=lambda x: os.path.getmtime(os.path.join(trending_folder, x)),
    reverse=True
)[:6]

# --- Build slider HTML ---
slider_html = """
<div class="container-fluid py-3">
    <div class="container">
        <div class="owl-carousel owl-carousel-2 carousel-item-3 position-relative">
"""

for file_name in trending_files:
    file_path = os.path.join(trending_folder, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        # grab first img (with class="img-fluid") for slider
        img_tag = soup.find("img", class_="img-fluid")
        img_src = img_tag["src"] if img_tag else "/ScreamLine/img/news-placeholder.jpg"
        # grab the news title exactly as in original article
        title_tag = soup.find("h3", class_="mb-3")
        title = title_tag.get_text(strip=True) if title_tag else file_name.replace("_", " ")
        # --- truncate title if more than 6 words ---
        words = title.split()
        if len(words) > 6:
            title = " ".join(words[:10]) + "..."
        slider_html += f"""
        <div class="d-flex">
            <img src="{img_src}" style="width: 80px; height: 80px; object-fit: cover;">
            <div class="d-flex align-items-center bg-light px-3" style="height: 80px;">
                <a class="text-secondary font-weight-semi-bold" href="/ScreamLine/trending/{file_name}">{title}</a>
            </div>
        </div>
        """

slider_html += """
        </div>
    </div>
</div>
"""

# --- Insert new slider ---
start_comment.insert_after(BeautifulSoup(slider_html, "html.parser"))

# --- Save index.html ---
with open(index_file_path, "w", encoding="utf-8") as f:
    f.write(str(index_soup))

print("Top News Slider updated successfully!")