/**
 * frontend/js/booking.js - Trip Booking, Seat Map & Quantity Selector Controller
 * Formats all fares in Indian Rupees (₹) and supports Indian passenger names.
 */

let currentTrip = null;
let selectedSeats = [];
let quantity = 1;

document.addEventListener("DOMContentLoaded", async () => {
  API.setupHeaderAuth();

  const urlParams = new URLSearchParams(window.location.search);
  const tripId = urlParams.get("trip_id");

  if (!tripId) {
    window.location.href = "/search.html";
    return;
  }

  await loadTripDetails(tripId);

  document.getElementById("confirmBookingBtn")?.addEventListener("click", handleBookingSubmit);
});

async function loadTripDetails(tripId) {
  const summaryContainer = document.getElementById("tripSummaryCard");
  try {
    const data = await API.getTrip(tripId);
    currentTrip = data.trip;

    renderTripSummary(currentTrip);
    renderSelectionControls(currentTrip);
    updatePriceSummary();

  } catch (err) {
    summaryContainer.innerHTML = `
      <div style="color: var(--failed-text); padding: 20px; text-align: center;">
        Failed to load trip #${tripId}: ${escapeHtml(err.message)}
      </div>
    `;
  }
}

function renderTripSummary(trip) {
  const container = document.getElementById("tripSummaryCard");
  const depTime = trip.departure_time || "--:--";
  const arrTime = trip.arrival_time || "--:--";

  container.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
      <div>
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
          <span class="badge badge-type">${escapeHtml(trip.transport_type)}</span>
          <span style="font-size: 15px; font-weight: 700;">${escapeHtml(trip.operator)}</span>
          <span style="font-size: 11px; color: var(--text-muted);">Trip ID #${trip.id}</span>
        </div>
        <div style="font-size: 14px; font-weight: 600; color: #0f172a;">
          ${escapeHtml(trip.origin)} &rarr; ${escapeHtml(trip.destination)}
        </div>
        <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">
          Departure: ${depTime} | Arrival: ${arrTime}
        </div>
      </div>

      <div style="text-align: right;">
        <div style="font-size: 11px; color: var(--text-muted);">Available Capacity</div>
        <div style="font-size: 18px; font-weight: 700; color: ${trip.seats_available <= 5 ? 'var(--failed-text)' : 'var(--success-text)'};">
          ${trip.seats_available} / ${trip.seats_total} left
        </div>
        <div style="font-size: 13px; font-weight: 600; color: var(--text-main); margin-top: 2px;">
          ${API.formatCurrency(trip.price)} per ticket
        </div>
      </div>
    </div>
  `;
}

function renderSelectionControls(trip) {
  const type = trip.transport_type.toLowerCase();
  const title = document.getElementById("selectionTitle");
  const subtitle = document.getElementById("selectionSubtitle");
  const container = document.getElementById("selectionContainer");

  if (["flight", "bus", "train"].includes(type)) {
    title.textContent = `Select Seat(s) on ${type.toUpperCase()}`;
    subtitle.textContent = "Click available seat(s) to select";

    const seatRows = 6;
    const seatCols = ["A", "B", "C", "D"];
    const totalSimulatedSeats = seatRows * seatCols.length;

    const occupiedCount = Math.max(0, Math.min(totalSimulatedSeats - 1, totalSimulatedSeats - Math.min(trip.seats_available, totalSimulatedSeats)));

    let occupiedSeatsSet = new Set();
    for (let i = 0; i < occupiedCount; i++) {
      const row = ((trip.id * 7 + i * 3) % seatRows) + 1;
      const col = seatCols[(trip.id + i * 2) % 4];
      occupiedSeatsSet.add(`${row}${col}`);
    }

    selectedSeats = [];
    for (let r = 1; r <= seatRows; r++) {
      for (const c of seatCols) {
        const seatName = `${r}${c}`;
        if (!occupiedSeatsSet.has(seatName)) {
          selectedSeats.push(seatName);
          break;
        }
      }
      if (selectedSeats.length > 0) break;
    }

    let gridHtml = `
      <div class="seat-grid-container">
        <div class="seat-legend">
          <div class="seat-legend-item">
            <span class="seat-box-sample" style="background:#ffffff; border:1px solid var(--border-dark);"></span> Available
          </div>
          <div class="seat-legend-item">
            <span class="seat-box-sample" style="background:var(--accent);"></span> Selected
          </div>
          <div class="seat-legend-item">
            <span class="seat-box-sample" style="background:#e2e8f0; border:1px solid #cbd5e1;"></span> Occupied
          </div>
        </div>

        <div class="seat-grid" id="seatGrid">
    `;

    for (let r = 1; r <= seatRows; r++) {
      for (const c of seatCols) {
        const seatName = `${r}${c}`;
        const isOccupied = occupiedSeatsSet.has(seatName);
        const isSelected = selectedSeats.includes(seatName);

        gridHtml += `
          <div class="seat-cell ${isOccupied ? 'occupied' : ''} ${isSelected ? 'selected' : ''}"
               data-seat="${seatName}">
            ${seatName}
          </div>
        `;
      }
    }

    gridHtml += `
        </div>
      </div>
    `;

    container.innerHTML = gridHtml;

    container.querySelectorAll(".seat-cell:not(.occupied)").forEach(cell => {
      cell.addEventListener("click", () => {
        const seat = cell.dataset.seat;
        if (selectedSeats.includes(seat)) {
          if (selectedSeats.length > 1) {
            selectedSeats = selectedSeats.filter(s => s !== seat);
            cell.classList.remove("selected");
          }
        } else {
          if (selectedSeats.length < Math.min(4, trip.seats_available)) {
            selectedSeats.push(seat);
            cell.classList.add("selected");
          } else {
            alert(`Maximum 4 seats can be selected per booking.`);
          }
        }
        quantity = selectedSeats.length;
        renderPassengerInputs();
        updatePriceSummary();
      });
    });

  } else {
    // Cab or Bike
    title.textContent = `Select ${type === 'cab' ? 'Vehicle Seats / Cab Capacity' : 'Number of Bikes'}`;
    subtitle.textContent = "Choose quantity to reserve";

    const maxSelectable = Math.max(1, Math.min(4, trip.seats_available));
    selectedSeats = [];
    quantity = 1;

    let options = "";
    for (let i = 1; i <= maxSelectable; i++) {
      options += `<option value="${i}">${i} ${type === 'cab' ? 'Passenger(s) / Full Cab' : 'Bike(s)'}</option>`;
    }

    container.innerHTML = `
      <div style="padding: 16px; background-color: #f8fafc; border: 1px solid var(--border); border-radius: 4px;">
        <label for="quantitySelect" style="margin-bottom: 6px;">Reservation Quantity</label>
        <select id="quantitySelect" style="max-width: 280px;">
          ${options}
        </select>
        <p style="font-size: 12px; color: var(--text-muted); margin-top: 8px;">
          ${type === 'cab' ? 'Private AC sedan or EV transfer with luggage support.' : 'Urban smart electric mobility with GPS unlock.'}
        </p>
      </div>
    `;

    document.getElementById("quantitySelect")?.addEventListener("change", (e) => {
      quantity = parseInt(e.target.value, 10);
      renderPassengerInputs();
      updatePriceSummary();
    });
  }

  renderPassengerInputs();
}

function renderPassengerInputs() {
  const container = document.getElementById("passengerInputsContainer");
  if (!container) return;

  const user = API.getUser();
  const count = selectedSeats.length > 0 ? selectedSeats.length : quantity;

  let html = "";
  for (let i = 0; i < count; i++) {
    const defaultName = (i === 0 && user) ? user.name : "";
    const seatLabel = selectedSeats[i] ? ` (Seat ${selectedSeats[i]})` : ` (Passenger ${i + 1})`;

    html += `
      <div class="passenger-row">
        <div style="flex: 1;">
          <label for="pName_${i}">Passenger ${i + 1} Name${seatLabel}</label>
          <input type="text" id="pName_${i}" class="p-name-input" required
                 value="${escapeHtml(defaultName)}"
                 placeholder="Enter full legal name (as on Govt ID)">
        </div>
      </div>
    `;
  }

  container.innerHTML = html;
}

function updatePriceSummary() {
  if (!currentTrip) return;

  const count = selectedSeats.length > 0 ? selectedSeats.length : quantity;
  const total = currentTrip.price * count;

  document.getElementById("summaryBasePrice").textContent = API.formatCurrency(currentTrip.price);
  document.getElementById("summaryQuantity").textContent = count;
  document.getElementById("summarySeatList").textContent = selectedSeats.length > 0 ? selectedSeats.join(", ") : `${count} Unit(s)`;
  document.getElementById("summaryTotalPrice").textContent = API.formatCurrency(total);
}

async function handleBookingSubmit() {
  const alertBox = document.getElementById("bookingAlert");
  alertBox.style.display = "none";

  // Check login
  const token = API.getToken();
  if (!token) {
    const returnUrl = encodeURIComponent(window.location.href);
    window.location.href = `/login.html?returnUrl=${returnUrl}`;
    return;
  }

  // Collect passenger names
  const nameInputs = document.querySelectorAll(".p-name-input");
  const names = [];
  for (const input of nameInputs) {
    const val = input.value.trim();
    if (!val) {
      alertBox.textContent = "Please provide the full name for all passengers.";
      alertBox.className = "form-msg error";
      alertBox.style.display = "block";
      input.focus();
      return;
    }
    names.push(val);
  }

  const count = selectedSeats.length > 0 ? selectedSeats.length : quantity;
  const namesJoined = names.join(", ");

  const confirmBtn = document.getElementById("confirmBookingBtn");
  confirmBtn.disabled = true;
  confirmBtn.textContent = "Processing Booking in Database...";

  try {
    const res = await API.createBooking(currentTrip.id, namesJoined, count);
    const booking = res.booking;

    // Successful booking redirect to ticket confirmation
    window.location.href = `/ticket.html?booking_id=${booking.id}`;

  } catch (err) {
    confirmBtn.disabled = false;
    confirmBtn.textContent = "Confirm & Book Ticket";
    alertBox.textContent = err.message || "Failed to create booking. Please check seat availability.";
    alertBox.className = "form-msg error";
    alertBox.style.display = "block";
  }
}
