(() => {
  const mapDate = document.getElementById("map-date");
  const riskState = document.getElementById("risk-state");
  const mapFrame = document.getElementById("malaysia-map");
  const mapLegends = document.querySelectorAll(".map-legend[data-map]");
  const riskLayers = document.getElementById("risk-layers");
  const weatherCard = document.getElementById("weather-card");
  const agricultureRisk = document.getElementById("agriculture-risk");
  const simulationContent = document.getElementById("simulation-content");
  const simulationCard = document.querySelector(".simulation-card");
  const simulationWeeks = document.querySelectorAll(".simulation-weeks button");
  const motionButton = document.getElementById("simulation-motion");
  const appStatus = document.getElementById("app-status");
  const mapWrapper = mapFrame.parentElement;
  let requestNumber = 0;

  function prepareSimulation() {
    const body = simulationContent.querySelector(".simulation-body");
    if (!body) return;
    const image = body.querySelector("img");
    const ready = () => body.classList.add("is-ready");
    if (image.complete) ready();
    else image.addEventListener("load", ready, { once: true });
  }

  async function loadFragment(target, endpoint, extra = {}) {
    const request = String(++requestNumber);
    target.dataset.request = request;
    if (!mapDate.value || !mapDate.reportValidity()) {
      target.removeAttribute("aria-busy");
      target.textContent = "Choose a valid date.";
      return;
    }
    const url = new URL(endpoint, window.location.origin);
    url.search = new URLSearchParams({ date: mapDate.value, state: riskState.value, ...extra });
    const label = target.getAttribute("aria-label");
    target.classList.remove("is-updated");
    target.setAttribute("aria-busy", "true");
    appStatus.textContent = `Updating ${label.toLowerCase()}…`;
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error("Request failed");
      const html = await response.text();
      if (target.dataset.request !== request) return;
      target.innerHTML = html;
      if (target === simulationContent) prepareSimulation();
      target.classList.add("is-updated");
      appStatus.textContent = `${label} updated.`;
    } catch (error) {
      if (target.dataset.request !== request) return;
      target.innerHTML = '<p class="data-message" role="status">Unable to update this section. Try another date or state.</p>';
      appStatus.textContent = `Unable to update ${label.toLowerCase()}.`;
    } finally {
      if (target.dataset.request === request) target.removeAttribute("aria-busy");
    }
  }

  function updateMap() {
    if (!mapDate.value || !mapDate.reportValidity()) return;
    const selected = document.querySelector('input[name="map"]:checked');
    const url = new URL(selected.value, window.location.origin);
    url.searchParams.set("date", mapDate.value);
    mapWrapper.setAttribute("aria-busy", "true");
    mapFrame.src = url.href;
    mapFrame.title = `Malaysia · ${selected.nextElementSibling.textContent} · ${mapDate.value}`;
    mapLegends.forEach((legend) => { legend.hidden = legend.dataset.map !== selected.id; });
  }

  mapFrame.addEventListener("load", () => mapWrapper.removeAttribute("aria-busy"));

  function updateSimulation() {
    const week = document.querySelector('.simulation-weeks [aria-pressed="true"]').dataset.weeks;
    return loadFragment(simulationContent, "/simulation", { weeks: week });
  }

  function updatePanels() {
    loadFragment(agricultureRisk, "/agriculture-risk");
    loadFragment(riskLayers, "/risk-layers");
    loadFragment(weatherCard, "/weather");
    updateSimulation();
  }

  function setMotion(paused) {
    simulationCard.classList.toggle("motion-paused", paused);
    motionButton.setAttribute("aria-pressed", String(!paused));
    motionButton.textContent = paused ? "Play motion" : "Pause motion";
  }

  motionButton.addEventListener("click", () => {
    const paused = motionButton.getAttribute("aria-pressed") === "true";
    simulationCard.classList.toggle("motion-enabled", !paused);
    setMotion(paused);
  });
  setMotion(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  prepareSimulation();

  simulationWeeks.forEach((button, index) => {
    button.addEventListener("click", () => {
      simulationWeeks.forEach((week) => week.setAttribute("aria-pressed", String(week === button)));
      button.parentElement.style.setProperty("--selected", index);
      updateSimulation();
    });
  });
  mapDate.addEventListener("change", () => { updateMap(); updatePanels(); });
  riskState.addEventListener("change", updatePanels);
  document.querySelectorAll('input[name="map"]').forEach((radio) => radio.addEventListener("change", updateMap));
})();
