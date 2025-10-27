document.addEventListener("DOMContentLoaded", function () {
  // ===== 1️⃣ Load Header =====
  const headerContainer = document.getElementById("header");
  if (headerContainer) {
    fetch("/ScreamLine/templates/header.html")
      .then(res => {
        if (!res.ok) throw new Error("Header not found");
        return res.text();
      })
      .then(data => {
        headerContainer.innerHTML = data;

        // Enable search + live clock once header loads
        const input = document.getElementById("search-input");
        const button = document.getElementById("search-button");
        const dateEl = document.getElementById("current-date");

        function searchNow() {
          const query = input?.value.trim();
          if (query) {
            window.location.href = `/ScreamLine/search.html?q=${encodeURIComponent(query)}`;
          }
        }

        if (button && input) {
          button.addEventListener("click", searchNow);
          input.addEventListener("keypress", e => {
            if (e.key === "Enter") searchNow();
          });
        }

        if (dateEl) {
          setInterval(() => {
            const now = new Date();
            dateEl.textContent = now.toLocaleString();
          }, 1000);
        }
      })
      .catch(err => console.error("Header load error:", err));
  }

  // ===== 2️⃣ Load Footer =====
  const footerContainer = document.getElementById("footer");
  if (footerContainer) {
    fetch("/ScreamLine/templates/footer.html")
      .then(res => {
        if (!res.ok) throw new Error("Footer not found");
        return res.text();
      })
      .then(data => {
        footerContainer.innerHTML = data;
      })
      .catch(err => console.error("Footer load error:", err));
  }

  // ===== 3️⃣ Build Dynamic News Index =====
  const folders = [
    "/ScreamLine/music/",
    "/ScreamLine/movies-tv/",
    "/ScreamLine/scifi/",
    "/ScreamLine/global/"
  ];

  async function fetchAllNews() {
    const allArticles = [];

    for (const folder of folders) {
      try {
        const response = await fetch(folder);
        const text = await response.text();
        const matches = text.match(/href="([^"]+\.html)"/g);
        if (!matches) continue;

        for (const match of matches) {
          const file = match.replace('href="', "").replace('"', "");
          const fileUrl = folder + file;

          const page = await fetch(fileUrl);
          const html = await page.text();
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, "text/html");

          const title =
            doc.querySelector("h1")?.innerText ||
            doc.querySelector("h3")?.innerText ||
            file.replace(".html", "").replace(/_/g, " ");
          const desc = doc.querySelector("p")?.innerText?.slice(0, 150) || "";
          const img = doc.querySelector("img")?.getAttribute("src") || "/ScreamLine/img/default.jpg";
          const date = doc.querySelector(".date")?.innerText || "";

          allArticles.push({
            title,
            desc,
            img: img.startsWith("/") ? img : folder + img,
            link: fileUrl,
            date,
          });
        }
      } catch (err) {
        console.warn(`Error reading folder: ${folder}`, err);
      }
    }

    // Store full index in localStorage for instant use
    localStorage.setItem("screamline_news_index", JSON.stringify(allArticles));
    console.log(`✅ Indexed ${allArticles.length} news articles.`);
  }

  // Run only if not indexed recently
  const lastIndexed = localStorage.getItem("screamline_index_time");
  const oneDay = 24 * 60 * 60 * 1000;
  if (!lastIndexed || Date.now() - Number(lastIndexed) > oneDay) {
    fetchAllNews().then(() => {
      localStorage.setItem("screamline_index_time", Date.now().toString());
    });
  }
});
