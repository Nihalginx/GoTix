/**
 * frontend/js/ticket.js - Ticket Confirmation & Printable Boarding Pass Controller
 * Formats all fares in Indian Rupees (₹).
 */

document.addEventListener("DOMContentLoaded", async () => {
  API.setupHeaderAuth();

  const urlParams = new URLSearchParams(window.location.search);
  const bookingId = urlParams.get("booking_id");

  if (!bookingId) {
    window.location.href = "/my-bookings.html";
    return;
  }

  await loadTicket(bookingId);

  document.getElementById("printBtn")?.addEventListener("click", () => {
    window.print();
  });
});

async function loadTicket(bookingId) {
  const container = document.getElementById("ticketContent");

  try {
    const data = await API.getBooking(bookingId);
    const b = data.booking;
    const t = b.trip || {};

    const formattedId = `BK-${String(b.id).padStart(5, '0')}`;
    const statusClass = b.status === "confirmed" ? "badge-success" : "badge-failed";

    container.innerHTML = `
      <div class="ticket-header">
        <div>
          <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.8;">OFFICIAL TRAVEL TICKET & BOARDING PASS</div>
          <div style="font-size: 18px; font-weight: 700; margin-top: 2px;">${escapeHtml(t.operator || "Transport Operator")}</div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 11px; opacity: 0.8;">BOOKING REFERENCE</div>
          <div style="font-size: 16px; font-weight: 700; letter-spacing: 1px;">#${formattedId}</div>
        </div>
      </div>

      <div class="ticket-body">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 14px;">
          <div>
            <span class="badge badge-type" style="margin-right: 6px;">${escapeHtml(t.transport_type || "Transport")}</span>
            <span class="badge ${statusClass}">${escapeHtml(b.status)}</span>
          </div>
          <div style="font-size: 12px; color: var(--text-muted);">
            Booked on: <strong>${b.booked_at || ""}</strong>
          </div>
        </div>

        <div class="ticket-grid">
          <div>
            <div class="ticket-field-label">Origin Station / Airport</div>
            <div class="ticket-field-val">${escapeHtml(t.origin || "Origin")}</div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">Departure: ${t.departure_time || ""}</div>
          </div>

          <div>
            <div class="ticket-field-label">Destination Station / Airport</div>
            <div class="ticket-field-val">${escapeHtml(t.destination || "Destination")}</div>
            <div style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">Arrival: ${t.arrival_time || ""}</div>
          </div>

          <div>
            <div class="ticket-field-label">Passenger Name(s)</div>
            <div class="ticket-field-val">${escapeHtml(b.passenger_names)}</div>
          </div>

          <div>
            <div class="ticket-field-label">Seats / Capacity Booked</div>
            <div class="ticket-field-val">${b.seats_booked} Ticket(s)</div>
          </div>

          <div>
            <div class="ticket-field-label">Primary Account</div>
            <div class="ticket-field-val" style="font-weight: normal; font-size: 13px;">${escapeHtml(b.user_name || "")} (${escapeHtml(b.user_email || "")})</div>
          </div>

          <div>
            <div class="ticket-field-label">Total Amount Paid</div>
            <div class="ticket-field-val" style="font-size: 18px; color: var(--accent);">${API.formatCurrency(b.total_price)}</div>
          </div>
        </div>
      </div>

      <div class="ticket-stub">
        <div>
          <div style="font-size: 11px; text-transform: uppercase;">Security Verification</div>
          <div class="ticket-barcode-mock">||| | |||| || ||| ||||| | ||</div>
        </div>
        <div style="text-align: right;">
          <div>SQLite Record: <code>bookings.id = ${b.id}</code></div>
          <div style="font-size: 11px;">Validated via FastAPI Engine</div>
        </div>
      </div>
    `;

  } catch (err) {
    container.innerHTML = `
      <div style="text-align: center; color: var(--failed-text); padding: 30px;">
        Error retrieving ticket: ${escapeHtml(err.message)}
      </div>
    `;
  }
}
