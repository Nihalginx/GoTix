/**
 * frontend/js/home.js - Home & Search Landing Page Controller
 * Handles dynamic mode switching (Flights, Trains, Buses, Cabs, Bikes)
 * with dedicated labels, chips, options, calendar picker, and Indian Rupee fares.
 */

const MODE_CONFIG = {
  flight: {
    badge: "FLIGHTS (DOMESTIC & INTERNATIONAL)",
    heading: "Search Flights from any Indian Airport to Worldwide Destinations",
    subtitle: "Real schedules for Air India, IndiGo, British Airways, Emirates, and Singapore Airlines.",
    fromLabel: "From (Airport / City)",
    fromPlaceholder: "e.g. Delhi (DEL), Mumbai (BOM), Bengaluru (BLR)",
    fromDefault: "Delhi",
    fromChips: ["Delhi (DEL)", "Mumbai (BOM)", "Bengaluru (BLR)", "Chennai (MAA)", "Hyderabad (HYD)", "Kolkata (CCU)"],
    toLabel: "To (Airport / Destination)",
    toPlaceholder: "e.g. London (LHR), Dubai (DXB), Singapore, Goa",
    toDefault: "London",
    toChips: ["London (LHR)", "Dubai (DXB)", "Singapore (SIN)", "New York (JFK)", "Goa (GOI)", "Bangkok (BKK)"],
    dateLabel: "Departure Date",
    optionLabel: "Cabin Class & Travellers",
    options: [
      { val: "1", text: "1 Passenger (Economy)" },
      { val: "2", text: "2 Passengers (Economy)" },
      { val: "3", text: "3 Passengers (Economy)" },
      { val: "1_biz", text: "1 Passenger (Business Class)" }
    ],
    note: "✈️ Non-stop and connecting flight routes available from all Indian airports.",
    btnText: "Search Flights"
  },
  train: {
    badge: "INDIAN RAILWAYS / IRCTC TRAINS",
    heading: "Book Vande Bharat, Rajdhani, Shatabdi & Superfast Trains",
    subtitle: "Confirmed berth availability and IRCTC schedule status across all Indian railway zones.",
    fromLabel: "From (Railway Station)",
    fromPlaceholder: "e.g. New Delhi (NDLS), Mumbai CSMT, Howrah (HWH)",
    fromDefault: "New Delhi",
    fromChips: ["New Delhi (NDLS)", "Mumbai CSMT", "Howrah (HWH)", "Bengaluru (SBC)", "Chennai Central (MAS)"],
    toLabel: "To (Railway Station - Domestic Only)",
    toPlaceholder: "e.g. Varanasi (BSB), Katra (SVDK), Ahmedabad (ADI), Goa (MAO)",
    toDefault: "Varanasi",
    toChips: ["Varanasi (BSB)", "Katra (SVDK)", "Ahmedabad (ADI)", "Goa (MAO)", "Jaipur (JP)", "Amritsar (ASR)"],
    dateLabel: "Journey Date",
    optionLabel: "Train Class & Quota",
    options: [
      { val: "all", text: "All Classes (General Quota)" },
      { val: "cc", text: "AC Chair Car (CC / EC)" },
      { val: "3a", text: "AC 3 Tier (3A)" },
      { val: "2a", text: "AC 2 Tier (2A)" },
      { val: "sl", text: "Sleeper Class (SL)" },
      { val: "tatkal", text: "Tatkal Quota" }
    ],
    note: "🚆 Domestic Indian Railway routes only. Overseas destinations (e.g. London) are not applicable for trains.",
    btnText: "Search Trains"
  },
  bus: {
    badge: "INTERCITY BUSES & VOLVO SLEEPERS",
    heading: "Book Luxury Volvo, AC Sleeper & Electric Intercity Coaches",
    subtitle: "KSRTC Airavat, MSRTC Shivneri, Zingbus, IntrCity SmartBus, and NueGo Electric Coaches.",
    fromLabel: "From (Boarding City)",
    fromPlaceholder: "e.g. Bengaluru, Delhi, Mumbai, Pune, Hyderabad",
    fromDefault: "Bengaluru",
    fromChips: ["Bengaluru", "Delhi", "Mumbai", "Pune", "Hyderabad", "Chennai"],
    toLabel: "To (Drop City)",
    toPlaceholder: "e.g. Hyderabad, Goa, Manali, Jaipur, Pune",
    toDefault: "Hyderabad",
    toChips: ["Hyderabad", "Goa", "Manali", "Jaipur", "Pune", "Chennai"],
    dateLabel: "Journey Date",
    optionLabel: "Coach & Seat Type",
    options: [
      { val: "all", text: "Any Coach Type" },
      { val: "sleeper", text: "AC Sleeper (2+1)" },
      { val: "volvo", text: "Multi-Axle Volvo AC" },
      { val: "electric", text: "NueGo 100% Electric AC" }
    ],
    note: "🚌 Intercity road routes across India with live GPS tracking and charging points.",
    btnText: "Search Buses"
  },
  cab: {
    badge: "CITY, AIRPORT & OUTSTATION CABS",
    heading: "Book Verified Airport Transfers & Intercity Cabs",
    subtitle: "Ola Prime, Uber Premier, BluSmart All-Electric EV, and MakeMyTrip Outstation transfers.",
    fromLabel: "Pickup Location",
    fromPlaceholder: "e.g. Mumbai Airport T2, Delhi IGI T3, Bengaluru Kempegowda",
    fromDefault: "Mumbai Airport",
    fromChips: ["Mumbai Airport T2", "Delhi IGI T3", "Bengaluru Airport T1", "Connaught Place", "Indiranagar"],
    toLabel: "Drop Location",
    toPlaceholder: "e.g. South Mumbai (Colaba), Whitefield, Gurgaon Cyber City",
    toDefault: "South Mumbai",
    toChips: ["South Mumbai", "Whitefield", "Gurgaon Cyber City", "Pune (Outstation)", "Hitec City"],
    dateLabel: "Pickup Date",
    optionLabel: "Cab Category",
    options: [
      { val: "sedan", text: "Prime Sedan (Dzire / Etios)" },
      { val: "electric", text: "BluSmart Electric EV Sedan" },
      { val: "suv", text: "Prime SUV XL (Innova / Ertiga)" },
      { val: "outstation", text: "Outstation One-Way Transfer" }
    ],
    note: "🚖 Fixed transparent pricing with toll fees included. Instant driver dispatch.",
    btnText: "Search Cabs"
  },
  bike: {
    badge: "SMART EV SCOOTERS & TOURIST BIKE RENTALS",
    heading: "Rent Smart EV Scooters & Royal Enfield Cruisers",
    subtitle: "Yulu Miracle EV urban commutes and tourist rentals across Goa, Manali & metro hubs.",
    fromLabel: "Pickup Hub",
    fromPlaceholder: "e.g. Indiranagar (BLR), Connaught Place (DEL), Calangute (Goa)",
    fromDefault: "Indiranagar",
    fromChips: ["Indiranagar (BLR)", "Connaught Place (DEL)", "Marine Drive (BOM)", "Calangute Beach (Goa)", "Old Manali"],
    toLabel: "Drop Hub / Area",
    toPlaceholder: "e.g. Koramangala, India Gate, Anjuna Beach, Solang Valley",
    toDefault: "Koramangala",
    toChips: ["Koramangala", "India Gate", "Colaba Causeway", "Anjuna Beach", "Solang Valley"],
    dateLabel: "Rental Start Date",
    optionLabel: "Rental Duration",
    options: [
      { val: "hourly", text: "Hourly Commute (Yulu / Bounce)" },
      { val: "daily", text: "1-Day Rental (Scooter / Bike)" },
      { val: "3days", text: "3-Day Tourist Rental" },
      { val: "weekly", text: "Weekly Vacation Package" }
    ],
    note: "🛵 Includes DOT-certified helmet and GPS smart unlock via smartphone.",
    btnText: "Search Bikes"
  }
};

let currentMode = "flight";

document.addEventListener("DOMContentLoaded", () => {
  API.setupHeaderAuth();

  // Setup Date Picker
  setupDatePicker();

  // Mode switching tabs
  const tabButtons = document.querySelectorAll("#transportTabs .tab-btn");
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const mode = btn.dataset.type || "flight";
      applyMode(mode);
    });
  });

  // Apply default mode (flight)
  applyMode("flight");

  // Handle Search Form Submit
  const searchForm = document.getElementById("searchForm");
  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const origin = document.getElementById("fromInput").value.trim();
      const destination = document.getElementById("toInput").value.trim();
      const date = document.getElementById("dateInput").value;
      const option = document.getElementById("optionInput").value;

      if (!origin || !destination) {
        alert("Please enter both origin and destination.");
        return;
      }

      // Check for dumb overseas train/bus search
      const overseasTerms = ["london", "dubai", "new york", "singapore", "paris", "bangkok", "toronto", "tokyo"];
      const destLower = destination.toLowerCase();
      if ((currentMode === "train" || currentMode === "bus") && overseasTerms.some(t => destLower.includes(t))) {
        alert(`${currentMode.toUpperCase()}s operate domestically within India.\n\nFor international travel to ${destination}, please switch to the Flights tab.`);
        return;
      }

      const params = new URLSearchParams();
      params.set("type", currentMode);
      params.set("origin", origin);
      params.set("destination", destination);
      if (date) params.set("date", date);
      if (option) params.set("option", option);

      window.location.href = `/search.html?${params.toString()}`;
    });
  }

  // Load Popular Routes table
  loadPopularRoutes();
});

function applyMode(mode) {
  currentMode = mode;
  const cfg = MODE_CONFIG[mode] || MODE_CONFIG.flight;

  // Update text headers
  document.getElementById("modeBadge").textContent = cfg.badge;
  document.getElementById("modeHeading").textContent = cfg.heading;
  document.getElementById("modeSubtitle").textContent = cfg.subtitle;
  document.getElementById("modeFooterNote").textContent = cfg.note;
  document.getElementById("searchSubmitBtn").textContent = cfg.btnText;

  // Update From field
  document.getElementById("fromLabel").textContent = cfg.fromLabel;
  const fromInput = document.getElementById("fromInput");
  fromInput.placeholder = cfg.fromPlaceholder;
  fromInput.value = cfg.fromDefault;

  // Update To field
  document.getElementById("toLabel").textContent = cfg.toLabel;
  const toInput = document.getElementById("toInput");
  toInput.placeholder = cfg.toPlaceholder;
  toInput.value = cfg.toDefault;

  // Update Date label
  document.getElementById("dateLabel").textContent = cfg.dateLabel;

  // Update Option (Class / Category) field
  document.getElementById("optionLabel").textContent = cfg.optionLabel;
  const optionSelect = document.getElementById("optionInput");
  optionSelect.innerHTML = cfg.options.map(opt => `<option value="${opt.val}">${opt.text}</option>`).join("");

  // Render quick chips for From
  const fromChipsContainer = document.getElementById("fromChips");
  fromChipsContainer.innerHTML = cfg.fromChips.map(chipText => {
    const cleanVal = chipText.split(" (")[0];
    return `<span class="city-chip" data-field="from" data-val="${escapeHtml(cleanVal)}">${escapeHtml(chipText)}</span>`;
  }).join("");

  // Render quick chips for To
  const toChipsContainer = document.getElementById("toChips");
  toChipsContainer.innerHTML = cfg.toChips.map(chipText => {
    const cleanVal = chipText.split(" (")[0];
    return `<span class="city-chip" data-field="to" data-val="${escapeHtml(cleanVal)}">${escapeHtml(chipText)}</span>`;
  }).join("");

  // Re-attach chip click handlers
  document.querySelectorAll(".city-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const field = chip.dataset.field;
      const val = chip.dataset.val;
      if (field === "from") {
        fromInput.value = val;
        fromInput.focus();
      } else if (field === "to") {
        toInput.value = val;
        toInput.focus();
      }
    });
  });
}

function setupDatePicker() {
  const dateInput = document.getElementById("dateInput");
  const calendarBtn = document.getElementById("calendarBtn");
  const dateFriendly = document.getElementById("selectedDateFriendly");

  if (!dateInput) return;

  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, "0");
  const dd = String(today.getDate()).padStart(2, "0");
  const todayStr = `${yyyy}-${mm}-${dd}`;

  dateInput.min = todayStr;
  dateInput.value = todayStr;

  function updateFriendlyText(isoStr) {
    if (!isoStr) return;
    try {
      const d = new Date(isoStr + "T00:00:00");
      const options = { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' };
      dateFriendly.textContent = "Selected: " + d.toLocaleDateString("en-IN", options);
    } catch {
      dateFriendly.textContent = "Selected: " + isoStr;
    }
  }

  updateFriendlyText(todayStr);

  dateInput.addEventListener("change", (e) => {
    updateFriendlyText(e.target.value);
  });

  // Clicking anywhere on input or calendar button opens native calendar dialog
  const openCalendar = () => {
    if (typeof dateInput.showPicker === "function") {
      dateInput.showPicker();
    } else {
      dateInput.focus();
    }
  };

  dateInput.addEventListener("click", openCalendar);
  calendarBtn?.addEventListener("click", openCalendar);
}

async function loadPopularRoutes() {
  const tableBody = document.getElementById("popularRoutesTable");
  if (!tableBody) return;

  try {
    const data = await API.getPopularRoutes();
    const routes = data.routes || [];

    if (routes.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:15px; color:var(--text-muted);">No routes available.</td></tr>`;
      return;
    }

    tableBody.innerHTML = routes.map(r => `
      <tr>
        <td>
          <span class="badge badge-type">${escapeHtml(r.type)}</span>
        </td>
        <td>
          <strong>${escapeHtml(r.origin)}</strong> &rarr; <strong>${escapeHtml(r.destination)}</strong>
        </td>
        <td style="font-size: 12px; color: var(--text-muted);">
          ${escapeHtml(r.desc || "")}
        </td>
        <td style="font-size: 12px; color: var(--text-muted);">
          ${escapeHtml(r.duration || "Direct")}
        </td>
        <td>
          From <strong>${API.formatCurrency(r.starting_from)}</strong>
        </td>
        <td style="text-align: right;">
          <a href="/search.html?type=${encodeURIComponent(r.type)}&origin=${encodeURIComponent(r.origin)}&destination=${encodeURIComponent(r.destination)}"
             class="btn btn-secondary btn-sm">
            View Fares &rarr;
          </a>
        </td>
      </tr>
    `).join("");
  } catch (err) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align:center; padding:15px; color:var(--failed-text);">
          Failed to load popular routes.
        </td>
      </tr>
    `;
  }
}
