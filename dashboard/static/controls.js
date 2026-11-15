(() => {
  const filters = document.getElementById("dashboard-filters");
  const links = document.querySelectorAll("[data-page-link]");

  function updateNavigation() {
    if (!filters.reportValidity()) return;
    const params = new URLSearchParams(new FormData(filters));
    links.forEach((link) => {
      const url = new URL(link.href);
      url.search = params.toString();
      link.href = url.href;
    });
    if (filters.dataset.page === "overview") {
      window.history.replaceState(null, "", links[0].href);
    }
  }

  // Analysis state and date controls belong to this form from the chart toolbar.
  document.addEventListener("change", (event) => {
    if (event.target.form !== filters) return;
    updateNavigation();
    if (filters.dataset.page === "analysis" && filters.reportValidity()) filters.requestSubmit();
  });
  filters.addEventListener("submit", () => {
    filters.setAttribute("aria-busy", "true");
    document.getElementById("app-status").textContent = "Loading the selected state and date…";
  });
  window.addEventListener("pageshow", () => filters.removeAttribute("aria-busy"));
})();
