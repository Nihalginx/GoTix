/**
 * frontend/js/admin_bookings.js - Admin Live Bookings Monitor Controller
 * Automatically detects newly inserted booking rows and highlights them with a fade-out effect.
 * Formats all fares in Indian Rupees (₹).
 */

let currentPage = 1;
const pageLimit = 10;
let totalPages = 1;

// Set of booking IDs seen in previous polling cycles
let knownBookingIds = new Set();
let isFirstLoad = true;

document.addEventListener("DOMContentLoaded", () => {
  AdminCommon.init(refreshBookings);

  const statusFilter = document.getElementById("statusFilter");
  const searchInput = document.getElementById("searchInput");
  const sortSelect = document.getElementById("sortSelect");

  statusFilter.addEventListener("change", () => {
    currentPage = 1;
    refreshBookings();
  });

  let searchTimeout = null;
  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      currentPage = 1;
      refreshBookings();
    }, 300);
  });

  sortSelect.addEventListener("change", () => {
    currentPage = 1;
    refreshBookings();
  });

  document.getElementById("manualRefreshBtn")?.addEventListener("click", () => {
    refreshBookings();
  });

  document.getElementById("prevPageBtn")?.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      refreshBookings();
    }
  });

  document.getElementById("nextPageBtn")?.addEventListener("click", () => {
    if (currentPage < totalPages) {
      currentPage++;
      refreshBookings();
    }
  });
});

async function refreshBookings() {
  const tableBody = document.getElementById("bookingsTableBody");
  const status = document.getElementById("statusFilter")?.value || "";
  const search = document.getElementById("searchInput")?.value.trim() || "";
  const sort = document.getElementById("sortSelect")?.value || "booked_desc";

  try {
    const data = await API.getAdminBookings({
      status,
      search,
      sort,
      page: currentPage,
      limit: pageLimit
    });

    const bookings = data.bookings || [];
    totalPages = data.pages || 1;

    document.getElementById("bookingsStatsText").textContent = `Total Bookings: ${data.total} recorded`;
    document.getElementById("pageInfoText").textContent = `Page ${data.page} of ${totalPages} (${data.total} total)`;

    document.getElementById("prevPageBtn").disabled = (currentPage <= 1);
    document.getElementById("nextPageBtn").disabled = (currentPage >= totalPages);

    if (bookings.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:24px; color:var(--text-muted);">No bookings found matching query.</td></tr>`;
      return;
    }

    // Identify newly added rows that were not in knownBookingIds
    const newRowIds = [];
    if (!isFirstLoad) {
      for (const b of bookings) {
        if (!knownBookingIds.has(b.id)) {
          newRowIds.push(b.id);
        }
      }
    }

    tableBody.innerHTML = bookings.map(b => {
      const isNew = newRowIds.includes(b.id);
      const isConfirmed = b.status === "confirmed";
      const statusBadge = isConfirmed
        ? `<span class="badge badge-success">Confirmed</span>`
        : `<span class="badge badge-failed">Cancelled</span>`;

      const t = b.trip || {};

      return `
        <tr class="${isNew ? 'row-highlight' : ''}" id="bookingRow_${b.id}">
          <td><strong>#BK-${String(b.id).padStart(5, '0')}</strong></td>
          <td>
            <strong>${escapeHtml(b.user_name || "User")}</strong><br>
            <span style="font-size:11px; color:var(--text-muted);">${escapeHtml(b.user_email || "")}</span>
          </td>
          <td>
            <span class="badge badge-type" style="margin-right:4px;">${escapeHtml(t.transport_type || "")}</span>
            <span>${escapeHtml(t.operator || "")}</span><br>
            <span style="font-size:12px; color:var(--text-muted);">${escapeHtml(t.origin || "")} &rarr; ${escapeHtml(t.destination || "")}</span>
          </td>
          <td>${escapeHtml(b.passenger_names)}</td>
          <td><strong>${b.seats_booked}</strong></td>
          <td><strong>${API.formatCurrency(b.total_price)}</strong></td>
          <td>${statusBadge}</td>
          <td style="font-size: 12px; color: var(--text-muted);">${b.booked_at || "--"}</td>
        </tr>
      `;
    }).join("");

    // Fade out highlight after 3.5 seconds
    if (newRowIds.length > 0) {
      setTimeout(() => {
        newRowIds.forEach(id => {
          const rowEl = document.getElementById(`bookingRow_${id}`);
          if (rowEl) {
            rowEl.classList.remove("row-highlight");
          }
        });
      }, 3500);
    }

    for (const b of bookings) {
      knownBookingIds.add(b.id);
    }
    isFirstLoad = false;

    AdminCommon.updateTimestamp(data.timestamp);

  } catch (err) {
    console.error("Error loading bookings table:", err);
  }
}
