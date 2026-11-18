/**
 * frontend/js/my_bookings.js - Customer Bookings Management Controller
 * Formats all fares in Indian Rupees (₹).
 */

document.addEventListener("DOMContentLoaded", () => {
  API.setupHeaderAuth();

  const user = API.getUser();
  if (!user) {
    const tableBody = document.getElementById("myBookingsTable");
    tableBody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align: center; padding: 40px;">
          <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 12px;">
            Please log in to view your travel reservations.
          </p>
          <a href="/login.html?returnUrl=/my-bookings.html" class="btn btn-primary btn-sm">Log In to Account</a>
        </td>
      </tr>
    `;
    return;
  }

  loadBookings();
});

async function loadBookings() {
  const tableBody = document.getElementById("myBookingsTable");

  try {
    const data = await API.getMyBookings();
    const bookings = data.bookings || [];

    if (bookings.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="9" style="text-align: center; padding: 40px; color: var(--text-muted);">
            You have not booked any trips yet. <a href="/search.html">Explore transport catalog &rarr;</a>
          </td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = bookings.map(b => {
      const t = b.trip || {};
      const isConfirmed = b.status === "confirmed";
      const statusBadge = isConfirmed
        ? `<span class="badge badge-success">Confirmed</span>`
        : `<span class="badge badge-failed">Cancelled</span>`;

      return `
        <tr>
          <td><strong>#BK-${String(b.id).padStart(5, '0')}</strong></td>
          <td>
            <span class="badge badge-type" style="margin-right: 4px;">${escapeHtml(t.transport_type || "")}</span>
            <span>${escapeHtml(t.operator || "Operator")}</span>
          </td>
          <td>
            <strong>${escapeHtml(t.origin || "")}</strong> &rarr; <strong>${escapeHtml(t.destination || "")}</strong>
          </td>
          <td style="font-size: 12px; color: var(--text-muted);">
            ${t.departure_time || "--"}
          </td>
          <td>${escapeHtml(b.passenger_names)}</td>
          <td><strong>${b.seats_booked}</strong></td>
          <td><strong>${API.formatCurrency(b.total_price)}</strong></td>
          <td>${statusBadge}</td>
          <td style="text-align: right; white-space: nowrap;">
            <a href="/ticket.html?booking_id=${b.id}" class="btn btn-secondary btn-sm" style="margin-right: 4px;">Ticket</a>
            ${isConfirmed
              ? `<button class="btn btn-danger btn-sm cancel-booking-btn" data-id="${b.id}" data-trip="${escapeHtml(t.operator || '')}">Cancel</button>`
              : `<span style="font-size: 11px; color: var(--text-muted);">Cancelled</span>`
            }
          </td>
        </tr>
      `;
    }).join("");

    // Attach cancellation handlers
    document.querySelectorAll(".cancel-booking-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const id = btn.dataset.id;
        handleCancel(id);
      });
    });

  } catch (err) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align: center; padding: 20px; color: var(--failed-text);">
          Failed to load bookings: ${escapeHtml(err.message)}
        </td>
      </tr>
    `;
  }
}

async function handleCancel(bookingId) {
  const alertBox = document.getElementById("bookingActionAlert");
  alertBox.style.display = "none";

  const confirmed = confirm(
    `Are you sure you want to cancel Booking #BK-${String(bookingId).padStart(5, '0')}?\n\nThe booked seats will be immediately returned to the trip's available capacity in the SQLite database.`
  );
  if (!confirmed) return;

  try {
    const res = await API.cancelBooking(bookingId);
    alertBox.textContent = res.message || "Booking successfully cancelled.";
    alertBox.className = "form-msg success";
    alertBox.style.display = "block";

    // Reload table to reflect new status
    loadBookings();

  } catch (err) {
    alertBox.textContent = err.message || "Failed to cancel booking.";
    alertBox.className = "form-msg error";
    alertBox.style.display = "block";
  }
}
