(() => {
  const calendar = document.getElementById("date-control");
  const dateInput = document.getElementById("map-date");
  const stateInput = document.getElementById("risk-state");
  const filters = document.getElementById("dashboard-filters");
  const dayGrid = calendar.querySelector(".calendar-days");
  const monthTitle = calendar.querySelector("#calendar-month-title");
  const monthButtons = calendar.querySelectorAll("[data-month]");
  const localDate = (value) => new Date(value + "T00:00:00");
  const dateKey = (value) => `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}-${String(value.getDate()).padStart(2, "0")}`;
  const minMonth = dateInput.min.slice(0, 7);
  const maxMonth = dateInput.max.slice(0, 7);
  let visibleMonth = localDate(dateInput.value);

  function updateLabels() {
    const selected = stateInput.selectedOptions[0];
    const flag = document.querySelector(".state-flag");
    document.querySelector(".state-selected").textContent = selected.textContent;
    flag.src = selected.dataset.flag;
    flag.alt = `Flag of ${selected.value}`;
    if (!dateInput.value || !dateInput.validity.valid) return;
    const date = localDate(dateInput.value);
    calendar.querySelector(".calendar-day").textContent = date.getDate();
    calendar.querySelector(".calendar-date-month").textContent = date.toLocaleDateString("en-GB", { month: "short" });
    calendar.querySelector(".calendar-year").textContent = date.getFullYear();
    calendar.querySelector("summary").setAttribute("aria-label", `Choose observation date. Selected ${date.toLocaleDateString("en-GB")} for ${selected.value}.`);
  }
  stateInput.addEventListener("change", updateLabels);
  dateInput.addEventListener("change", updateLabels);

  function renderCalendar() {
    const year = visibleMonth.getFullYear();
    const month = visibleMonth.getMonth();
    monthTitle.textContent = visibleMonth.toLocaleDateString("en-GB", { month: "long", year: "numeric" });
    const firstWeekday = (new Date(year, month, 1).getDay() + 6) % 7;
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const cells = document.createDocumentFragment();
    for (let index = 0; index < firstWeekday; index++) {
      const blank = document.createElement("span");
      blank.setAttribute("aria-hidden", "true");
      cells.append(blank);
    }
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const value = dateKey(date);
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = day;
      button.disabled = value < dateInput.min || value > dateInput.max;
      button.setAttribute("aria-label", date.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" }));
      button.setAttribute("aria-pressed", String(value === dateInput.value));
      button.addEventListener("click", () => {
        dateInput.value = value;
        calendar.open = false;
        dateInput.dispatchEvent(new Event("change", { bubbles: true }));
      });
      cells.append(button);
    }
    dayGrid.replaceChildren(cells);
    monthButtons.forEach((button) => {
      const next = dateKey(new Date(year, month + Number(button.dataset.month), 1)).slice(0, 7);
      button.disabled = next < minMonth || next > maxMonth;
    });
  }
  monthButtons.forEach((button) => button.addEventListener("click", () => {
    visibleMonth = new Date(visibleMonth.getFullYear(), visibleMonth.getMonth() + Number(button.dataset.month), 1);
    renderCalendar();
  }));
  calendar.addEventListener("toggle", () => {
    if (!calendar.open) return;
    visibleMonth = localDate(dateInput.value);
    renderCalendar();
  });
  document.addEventListener("click", (event) => { if (!calendar.contains(event.target)) calendar.open = false; });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && calendar.open) {
      calendar.open = false;
      calendar.querySelector("summary").focus();
    }
  });
  window.addEventListener("pageshow", () => {
    if (filters.dataset.page === "analysis") {
      dateInput.value = dateInput.defaultValue;
      stateInput.value = stateInput.querySelector("option[selected]").value;
    }
    updateLabels();
    calendar.open = false;
  });
  updateLabels();
  renderCalendar();


})();
