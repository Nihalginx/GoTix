/**
 * frontend/js/admin_dashboard.js - Database Monitor Dashboard Controller
 * Auto-refreshes metrics, breakdown table, and recent activity stream every 5s.
 * Formats all revenues in Indian Rupees (₹).
 */

document.addEventListener("DOMContentLoaded", () => {
  AdminCommon.init(refreshDashboard);

  document.getElementById("manualRefreshBtn")?.addEventListener("click", () => {
    refreshDashboard();
  });
});

async function refreshDashboard() {
  await Promise.all([
    loadStats(),
    loadActivity()
  ]);
}

async function loadStats() {
  try {
    const data = await API.getAdminStats();

    // Update 4 Summary Stat Cards
    document.getElementById("statUsers").textContent = data.total_users;
    document.getElementById("statBookings").textContent = data.total_bookings;
    document.getElementById("statRevenue").textContent = API.formatCurrency(data.revenue);
    document.getElementById("statFailedLogins").textContent = data.failed_logins_today;

    // Update Bookings per Transport Type table
    const tableBody = document.getElementById("transportBreakdownTable");
    const breakdown = data.bookings_per_transport_type || [];

    if (breakdown.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:15px; color:var(--text-muted);">No data.</td></tr>`;
    } else {
      tableBody.innerHTML = breakdown.map(item => `
        <tr>
          <td>
            <span class="badge badge-type" style="min-width: 60px; text-align: center;">${escapeHtml(item.transport_type)}</span>
          </td>
          <td>${item.active_trips} trips</td>
          <td><strong>${item.bookings_count}</strong></td>
          <td><strong>${API.formatCurrency(item.revenue)}</strong></td>
        </tr>
      `).join("");
    }

    AdminCommon.updateTimestamp(data.timestamp);

  } catch (err) {
    console.error("Dashboard stats error:", err);
  }
}

async function loadActivity() {
  const tableBody = document.getElementById("recentActivityTable");
  try {
    const data = await API.getAdminActivity(20);
    const activities = data.activity || [];

    if (activities.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:15px; color:var(--text-muted);">No recent activity recorded yet.</td></tr>`;
      return;
    }

    tableBody.innerHTML = activities.map(act => {
      const isSuccess = act.status === "success" || act.status === "confirmed";
      const statusBadge = isSuccess
        ? `<span class="badge badge-success">${escapeHtml(act.status)}</span>`
        : `<span class="badge badge-failed">${escapeHtml(act.status)}</span>`;

      const typeBadge = act.type === "login"
        ? `<span class="badge badge-role-user" style="font-size:10px;">AUTH</span>`
        : `<span class="badge badge-type" style="font-size:10px;">BOOKING</span>`;

      return `
        <tr>
          <td>
            ${typeBadge} <strong>${escapeHtml(act.action)}</strong>
          </td>
          <td>${escapeHtml(act.actor)}</td>
          <td style="font-size: 12px; color: var(--text-muted);">${escapeHtml(act.details)}</td>
          <td>${statusBadge}</td>
          <td style="font-size: 12px; color: var(--text-muted);">${act.time || "--"}</td>
        </tr>
      `;
    }).join("");

  } catch (err) {
    console.error("Activity stream error:", err);
  }
}
