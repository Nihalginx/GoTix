/**
 * frontend/js/admin_trips.js - Admin Trips Inventory & External API Sync Controller
 * Formats all fares in Indian Rupees (₹).
 */

let currentPage = 1;
const pageLimit = 10;
let totalPages = 1;

document.addEventListener("DOMContentLoaded", () => {
  AdminCommon.init(refreshTrips);

  const typeFilter = document.getElementById("typeFilter");
  const searchInput = document.getElementById("searchInput");
  const sortSelect = document.getElementById("sortSelect");

  typeFilter.addEventListener("change", () => {
    currentPage = 1;
    refreshTrips();
  });

  let searchTimeout = null;
  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      currentPage = 1;
      refreshTrips();
    }, 300);
  });

  sortSelect.addEventListener("change", () => {
    currentPage = 1;
    refreshTrips();
  });

  document.getElementById("manualRefreshBtn")?.addEventListener("click", () => {
    refreshTrips();
  });

  document.getElementById("syncApiBtn")?.addEventListener("click", handleApiSync);

  document.getElementById("prevPageBtn")?.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      refreshTrips();
    }
  });

  document.getElementById("nextPageBtn")?.addEventListener("click", () => {
    if (currentPage < totalPages) {
      currentPage++;
      refreshTrips();
    }
  });
});

async function refreshTrips() {
  const tableBody = document.getElementById("tripsTableBody");
  const type = document.getElementById("typeFilter")?.value || "";
  const search = document.getElementById("searchInput")?.value.trim() || "";
  const sort = document.getElementById("sortSelect")?.value || "id_asc";

  try {
    const data = await API.getAdminTrips({
      type,
      search,
      sort,
      page: currentPage,
      limit: pageLimit
    });

    const trips = data.trips || [];
    totalPages = data.pages || 1;

    document.getElementById("tripsStatsText").textContent = `Total Trips: ${data.total} recorded`;
    document.getElementById("pageInfoText").textContent = `Page ${data.page} of ${totalPages} (${data.total} total)`;

    document.getElementById("prevPageBtn").disabled = (currentPage <= 1);
    document.getElementById("nextPageBtn").disabled = (currentPage >= totalPages);

    if (trips.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding:24px; color:var(--text-muted);">No trips found matching criteria.</td></tr>`;
      return;
    }

    tableBody.innerHTML = trips.map(t => {
      const occ = t.occupancy_percent || 0;
      let occColor = "var(--text-muted)";
      if (occ >= 80) occColor = "var(--failed-text)";
      else if (occ >= 50) occColor = "var(--accent)";

      return `
        <tr>
          <td><strong>#TRIP-${t.id}</strong></td>
          <td><span class="badge badge-type">${escapeHtml(t.transport_type)}</span></td>
          <td><strong>${escapeHtml(t.operator)}</strong></td>
          <td>${escapeHtml(t.origin)} &rarr; ${escapeHtml(t.destination)}</td>
          <td style="font-size: 12px; color: var(--text-muted);">${t.departure_time || "--"}</td>
          <td style="font-size: 12px; color: var(--text-muted);">${t.arrival_time || "--"}</td>
          <td><strong>${API.formatCurrency(t.price)}</strong></td>
          <td>
            <strong>${t.seats_available}</strong> / ${t.seats_total}
          </td>
          <td>
            <span style="font-weight: 600; color: ${occColor};">${occ}%</span>
          </td>
        </tr>
      `;
    }).join("");

    AdminCommon.updateTimestamp(data.timestamp);

  } catch (err) {
    console.error("Error loading trips table:", err);
  }
}

async function handleApiSync() {
  const syncBtn = document.getElementById("syncApiBtn");
  const banner = document.getElementById("syncResultBanner");

  syncBtn.disabled = true;
  syncBtn.textContent = "Pulling API Telemetry...";
  banner.style.display = "none";

  try {
    const res = await API.syncTrips();
    const conditions = (res.synced_conditions || []).join(" | ");

    banner.innerHTML = `
      <strong>API Synchronization Complete:</strong> ${escapeHtml(res.message)}<br>
      <span style="font-size: 11px;">Telemetry: ${escapeHtml(conditions)}</span><br>
      <span style="font-size: 11px;">Added New Flight Connection: <strong>${escapeHtml(res.new_trip_added?.operator || '')} (${escapeHtml(res.new_trip_added?.origin || '')} &rarr; ${escapeHtml(res.new_trip_added?.destination || '')}) - ${API.formatCurrency(res.new_trip_added?.price)}</strong></span>
    `;
    banner.className = "form-msg success";
    banner.style.display = "block";

    refreshTrips();

  } catch (err) {
    banner.textContent = `Sync Error: ${err.message || 'Failed to sync from external API'}`;
    banner.className = "form-msg error";
    banner.style.display = "block";
  } finally {
    syncBtn.disabled = false;
    syncBtn.textContent = "Sync from API";
  }
}
