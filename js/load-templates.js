document.addEventListener("DOMContentLoaded", function () {
  // ✅ Load Header
  const headerContainer = document.getElementById("header");
  if (headerContainer) {
    fetch("/ScreamLine/templates/header.html")
      .then(res => {
        if (!res.ok) throw new Error("Header not found");
        return res.text();
      })
      .then(data => {
        headerContainer.innerHTML = data;

        // Enable search and live clock once header is loaded
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

  // ✅ Load Footer
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
});
