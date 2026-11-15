(() => {
  const periods = document.querySelector(".analysis-periods");
  const periodLinks = Array.from(periods.querySelectorAll("a"));
  const initialPeriod = periodLinks.findIndex((link) => link.hasAttribute("aria-current"));
  function selectPeriod(index) {
    periods.style.setProperty("--selected", index);
    periodLinks.forEach((item, position) => {
      if (position === index) item.setAttribute("aria-current", "true");
      else item.removeAttribute("aria-current");
    });
  }
  periodLinks.forEach((link, index) => link.addEventListener("click", (event) => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    selectPeriod(index);
  }));
  window.addEventListener("pageshow", () => selectPeriod(initialPeriod));
  const coarsePointer = window.matchMedia("(pointer: coarse)").matches;
  document.querySelectorAll("[data-analysis-card]").forEach((card) => {
    card.querySelector("[data-open-data]").addEventListener("click", () => card.querySelector("dialog").showModal());
    const spec = card.querySelector(".analysis-spec");
    if (!spec) return;
    const views = JSON.parse(spec.textContent);
    const graph = card.querySelector(".analysis-graph");
    const buttons = card.querySelectorAll("[data-view]");
    let selectedView = 0;

    function render(index) {
      selectedView = index;
      buttons.forEach((button) => button.setAttribute("aria-pressed", String(Number(button.dataset.view) === index)));
      card.querySelectorAll("[data-legend]").forEach((legend) => { legend.hidden = Number(legend.dataset.legend) !== index; });
      const figure = structuredClone(views[index].figure);
      graph.classList.remove("is-updated");
      graph.setAttribute("aria-busy", "true");
      // Touch users can scroll the page normally and tap for values.
      if (coarsePointer) figure.layout.dragmode = false;
      if (typeof Plotly === "undefined") {
        graph.removeAttribute("aria-busy");
        graph.textContent = "Chart unavailable. Select View daily data below.";
        return;
      }
      Plotly.react(graph, figure.data, figure.layout, {
        responsive: true, displayModeBar: false, showTips: false, scrollZoom: false, doubleClick: "reset",
      }).then(() => {
        graph.removeAttribute("aria-busy");
        graph.classList.add("is-updated");
      }).catch(() => {
        graph.removeAttribute("aria-busy");
        graph.textContent = "Chart unavailable. Select View daily data below.";
      });
    }

    buttons.forEach((button) => button.addEventListener("click", () => render(Number(button.dataset.view))));
    card.querySelector("[data-reset]").addEventListener("click", () => render(selectedView));
    render(0);
  });

  document.querySelectorAll('a[href="#analysis-data-notes"]').forEach((link) => {
    link.addEventListener("click", () => { document.getElementById("analysis-data-notes").open = true; });
  });
})();
