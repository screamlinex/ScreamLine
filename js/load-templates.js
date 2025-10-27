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

        // --- Initialize search ---
        const input = document.getElementById("search-input");
        const button = document.getElementById("search-button");

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

        // --- Initialize clock ---
        const dateEl = document.getElementById("current-date");
        if (dateEl) {
          function updateClock() {
            const now = new Date();
            const date = now.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
            const time = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
            dateEl.textContent = `${date} ${time}`;
          }

          // Initial load
          updateClock();

          // Update exactly when the minute changes
          const msToNextMinute = (60 - new Date().getSeconds()) * 1000 + 50;
          setTimeout(function tick() {
            updateClock();
            setTimeout(tick, 60000);
          }, msToNextMinute);
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
