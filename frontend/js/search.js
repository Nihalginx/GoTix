/**
 * frontend/js/search.js - Search Results Page Controller
 * Mode-tailored trip cards with airline flight codes, IRCTC train numbers,
 * interactive calendar picker, and Indian Rupee (₹) pricing.
 */

document.addEventListener("DOMContentLoaded", () => {
  API.setupHeaderAuth();

  // Read initial query params from URL
  const urlParams = new URLSearchParams(window.location.search);
  const typeParam = urlParams.get("type") || "flight";
  const originParam = urlParams.get("origin") || "";
  const destinationParam = urlParams.get("destination") || "";
  const dateParam = urlParams.get("date") || "";
  const maxPriceParam = urlParams.get("max_price") || "";

  // Set filter UI inputs to match URL
  const filterType = document.getElementById("filterType");
  const quickOrigin = document.getElementById("quickOrigin");
  const quickDestination = document.getElementById("quickDestination");
  const filterMaxPrice = document.getElementById("filterMaxPrice");

  if (filterType && typeParam) filterType.value = typeParam;
  if (quickOrigin && originParam) quickOrigin.value = originParam;
  if (quickDestination && destinationParam) quickDestination.value = destinationParam;
  if (filterMaxPrice && maxPriceParam) filterMaxPrice.value = maxPriceParam;

  setupSearchDatePicker(dateParam);
  updateSearchHeader(typeParam, originParam, destinationParam);

  // Load Trips
  fetchAndRenderTrips();

  // Handle Filter Form Submit
  const filterForm = document.getElementById("filterForm");
  if (filterForm) {
    filterForm.addEventListener("submit", (e) => {
      e.preventDefault();
      fetchAndRenderTrips();
    });
  }

  // Quick Origin / Destination search
  document.getElementById("quickSearchBtn")?.addEventListener("click", () => {
    fetchAndRenderTrips();
  });

  // Transport mode change listener
  filterType?.addEventListener("change", () => {
    updateSearchHeader(filterType.value, quickOrigin?.value, quickDestination?.value);
    fetchAndRenderTrips();
  });

  // Reset Filters
  document.getElementById("resetFiltersBtn")?.addEventListener("click", () => {
    if (filterType) filterType.value = "flight";
    if (quickOrigin) quickOrigin.value = "";
    if (quickDestination) quickDestination.value = "";
    if (filterMaxPrice) filterMaxPrice.value = "";
    document.getElementById("filterTimeOfDay").value = "any";
    document.getElementById("filterSort").value = "departure_asc";
    fetchAndRenderTrips();
  });
});

function setupSearchDatePicker(initialDate) {
  const dateInput = document.getElementById("filterDate");
  const calBtn = document.getElementById("filterCalBtn");
  const friendlyText = document.getElementById("filterDateFriendly");

  if (!dateInput) return;

  const today = new Date();
  const todayStr = today.toISOString().split("T")[0];
  dateInput.min = todayStr;

  if (initialDate) {
    dateInput.value = initialDate;
  } else {
    dateInput.value = todayStr;
  }

  function updateLabel(val) {
    if (!val) {
      friendlyText.textContent = "Any date";
      return;
    }
    try {
      const d = new Date(val + "T00:00:00");
      friendlyText.textContent = d.toLocaleDateString("en-IN", { weekday: 'short', day: 'numeric', month: 'short' });
    } catch {
      friendlyText.textContent = val;
    }
  }

  updateLabel(dateInput.value);

  dateInput.addEventListener("change", (e) => updateLabel(e.target.value));

  const triggerCalendar = () => {
    if (typeof dateInput.showPicker === "function") {
      dateInput.showPicker();
    } else {
      dateInput.focus();
    }
  };

  dateInput.addEventListener("click", triggerCalendar);
  calBtn?.addEventListener("click", triggerCalendar);
}

function updateSearchHeader(type, origin, dest) {
  const headerTitle = document.getElementById("searchHeaderTitle");
  const breadcrumb = document.getElementById("modeBreadcrumb");

  const modeName = {
    flight: "Flights",
    train: "Indian Railways Trains",
    bus: "Intercity Buses",
    cab: "Cabs & Transfers",
    bike: "Bikes & Scooters"
  }[type] || "Transit";

  breadcrumb.textContent = `${modeName.toUpperCase()} SCHEDULES`;

  if (origin && dest) {
    headerTitle.textContent = `${origin} → ${dest} (${modeName})`;
  } else if (origin || dest) {
    headerTitle.textContent = `${origin || "Any Origin"} → ${dest || "Any Destination"}`;
  } else {
    headerTitle.textContent = `Available ${modeName} Options`;
  }
}

async function fetchAndRenderTrips() {
  const container = document.getElementById("tripsList");
  const resultsCount = document.getElementById("resultsCount");
  const alertBanner = document.getElementById("searchAlertBanner");
  if (!container) return;

  alertBanner.style.display = "none";
  container.innerHTML = `<div class="card" style="text-align: center; color: var(--text-muted); padding: 30px;">Checking real-time database schedules...</div>`;

  const type = document.getElementById("filterType")?.value || "flight";
  const origin = document.getElementById("quickOrigin")?.value.trim() || "";
  const destination = document.getElementById("quickDestination")?.value.trim() || "";
  const date = document.getElementById("filterDate")?.value || "";
  const maxPrice = document.getElementById("filterMaxPrice")?.value || "";
  const timeOfDay = document.getElementById("filterTimeOfDay")?.value || "any";
  const sortBy = document.getElementById("filterSort")?.value || "departure_asc";

  updateSearchHeader(type, origin, destination);

  // Overseas check for trains and buses
  const overseasKeywords = ["london", "dubai", "new york", "singapore", "paris", "bangkok", "toronto", "tokyo"];
  const destLower = destination.toLowerCase();
  if ((type === "train" || type === "bus") && overseasKeywords.some(k => destLower.includes(k))) {
    alertBanner.innerHTML = `
      <strong>Route Incompatibility:</strong> ${type.toUpperCase()} services operate domestically within India.<br>
      For international journeys to <strong>${escapeHtml(destination)}</strong>, please select the <strong>Flights</strong> filter.
    `;
    alertBanner.className = "form-msg error";
    alertBanner.style.display = "block";
    container.innerHTML = `<div class="card" style="text-align: center; color: var(--text-muted); padding: 30px;">Please switch to Flights for overseas travel.</div>`;
    resultsCount.textContent = "0 options";
    return;
  }

  try {
    const data = await API.getTrips({
      type,
      origin,
      destination,
      date,
      max_price: maxPrice ? parseFloat(maxPrice) : null
    });

    let trips = data.trips || [];

    // Filter by Time of Day
    if (timeOfDay !== "any") {
      trips = trips.filter(t => {
        if (!t.departure_time) return true;
        const hour = parseInt(t.departure_time.split(" ")[1]?.split(":")[0] || "0", 10);
        if (timeOfDay === "morning") return hour >= 5 && hour < 12;
        if (timeOfDay === "afternoon") return hour >= 12 && hour < 18;
        if (timeOfDay === "evening") return hour >= 18 || hour < 5;
        return true;
      });
    }

    // Sort Trips
    trips.sort((a, b) => {
      if (sortBy === "price_asc") return a.price - b.price;
      if (sortBy === "price_desc") return b.price - a.price;
      if (sortBy === "seats_desc") return b.seats_available - a.seats_available;
      return (a.departure_time || "").localeCompare(b.departure_time || "");
    });

    resultsCount.textContent = `Found ${trips.length} verified ${type} option(s)`;

    if (trips.length === 0) {
      container.innerHTML = `
        <div class="card" style="text-align: center; padding: 40px;">
          <h3 style="font-size: 15px; font-weight: 600; color: var(--text-main);">No ${type} services found for this date</h3>
          <p style="font-size: 13px; color: var(--text-muted); margin-top: 6px;">
            Try clearing price or origin/destination filters.
          </p>
        </div>
      `;
      return;
    }

    container.innerHTML = trips.map(t => {
      const depTime = t.departure_time ? t.departure_time.split(" ")[1] : "--:--";
      const depDate = t.departure_time ? t.departure_time.split(" ")[0] : "";
      const arrTime = t.arrival_time ? t.arrival_time.split(" ")[1] : "--:--";

      const isLowSeats = t.seats_available > 0 && t.seats_available <= 5;
      const isSoldOut = t.seats_available <= 0;

      let seatText = `${t.seats_available} seats remaining`;
      if (t.transport_type === 'bike') seatText = `${t.seats_available} bikes available`;
      if (t.transport_type === 'cab') seatText = `${t.seats_available} vehicle slots`;
      if (isSoldOut) seatText = "Sold Out";

      // Tailored Amenities per Transport Type
      let amenitiesHtml = "";
      if (t.transport_type === "flight") {
        amenitiesHtml = `
          <div class="amenities-bar">
            <span class="amenity-tag">🍱 Free Hot Meals</span>
            <span class="amenity-tag">🧳 23kg Check-in + 7kg Cabin</span>
            <span class="amenity-tag" style="color: var(--success-text); font-weight: 600;">✓ 95% On-Time</span>
            <span class="amenity-tag">Terminal Verified</span>
          </div>
        `;
      } else if (t.transport_type === "train") {
        amenitiesHtml = `
          <div class="amenities-bar">
            <span class="amenity-tag">🚆 IRCTC Confirmed Berths</span>
            <span class="amenity-tag">🍽️ Catering / Pantry Available</span>
            <span class="amenity-tag">⚡ Charging Sockets at Every Berth</span>
          </div>
        `;
      } else if (t.transport_type === "bus") {
        amenitiesHtml = `
          <div class="amenities-bar">
            <span class="amenity-tag">📶 Live GPS Tracking</span>
            <span class="amenity-tag">🔌 Mobile Charging</span>
            <span class="amenity-tag">🛏️ Sanitized Blankets & Pillow</span>
            <span class="amenity-tag">⭐ 4.6 / 5 Rating</span>
          </div>
        `;
      } else if (t.transport_type === "cab") {
        amenitiesHtml = `
          <div class="amenities-bar">
            <span class="amenity-tag">🚘 Sanitized AC Cab</span>
            <span class="amenity-tag">🛣️ Toll & Airport Parking Included</span>
            <span class="amenity-tag">⏱️ 45 min Free Waiting</span>
          </div>
        `;
      } else if (t.transport_type === "bike") {
        amenitiesHtml = `
          <div class="amenities-bar">
            <span class="amenity-tag">🪖 DOT-Certified Helmet Included</span>
            <span class="amenity-tag">🔋 100% Fully Charged</span>
            <span class="amenity-tag">📱 Keyless Smartphone Unlock</span>
          </div>
        `;
      }

      return `
        <div class="trip-card">
          <div class="trip-info-left">
            <div class="trip-operator">
              <span class="badge badge-type">${escapeHtml(t.transport_type)}</span>
              <span>${escapeHtml(t.operator)}</span>
              <span style="font-size: 11px; color: var(--text-muted); font-weight: normal;">#ID-${t.id}</span>
            </div>

            <div class="trip-route">
              <div class="trip-point">
                <span class="trip-time">${depTime}</span>
                <span class="trip-city">${escapeHtml(t.origin)}</span>
                <span style="font-size: 11px; color: var(--text-muted);">${depDate}</span>
              </div>

              <div class="trip-duration-indicator">
                <div class="trip-line"></div>
                <span>direct</span>
              </div>

              <div class="trip-point">
                <span class="trip-time">${arrTime}</span>
                <span class="trip-city">${escapeHtml(t.destination)}</span>
              </div>
            </div>

            ${amenitiesHtml}
          </div>

          <div class="trip-pricing-right">
            <div class="trip-price">${API.formatCurrency(t.price)}</div>
            <span class="seats-pill ${isLowSeats ? 'low' : ''} ${isSoldOut ? 'low' : ''}">
              ${seatText}
            </span>
            ${isSoldOut
              ? `<button class="btn btn-secondary btn-sm" disabled>Sold Out</button>`
              : `<a href="/booking.html?trip_id=${t.id}" class="btn btn-primary btn-sm">Book Ticket &rarr;</a>`
            }
          </div>
        </div>
      `;
    }).join("");

  } catch (err) {
    container.innerHTML = `
      <div class="card" style="text-align: center; color: var(--failed-text); padding: 30px;">
        ${escapeHtml(err.message)}
      </div>
    `;
  }
}
