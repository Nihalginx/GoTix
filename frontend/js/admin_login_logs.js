/**
 * frontend/js/admin_login_logs.js - Admin Login Audit Trail Controller
 */

let currentPage = 1;
const pageLimit = 10;
let totalPages = 1;

document.addEventListener("DOMContentLoaded", () => {
  AdminCommon.init(refreshLogs);

  const statusFilter = document.getElementById("statusFilter");
  const searchInput = document.getElementById("searchInput");
  const sortSelect = document.getElementById("sortSelect");

  statusFilter.addEventListener("change", () => {
    currentPage = 1;
    refreshLogs();
  });

  let searchTimeout = null;
  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      currentPage = 1;
      refreshLogs();
    }, 300);
  });

  sortSelect.addEventListener("change", () => {
    currentPage = 1;
    refreshLogs();
  });

  document.getElementById("manualRefreshBtn")?.addEventListener("click", () => {
    refreshLogs();
  });

  document.getElementById("prevPageBtn")?.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      refreshLogs();
    }
  });

  document.getElementById("nextPageBtn")?.addEventListener("click", () => {
    if (currentPage < totalPages) {
      currentPage++;
      refreshLogs();
    }
  });
});

async function refreshLogs() {
  const tableBody = document.getElementById("logsTableBody");
  const status = document.getElementById("statusFilter")?.value || "";
  const search = document.getElementById("searchInput")?.value.trim() || "";
  const sort = document.getElementById("sortSelect")?.value || "time_desc";

  try {
    const data = await API.getAdminLoginLogs({
      status,
      search,
      sort,
      page: currentPage,
      limit: pageLimit
    });

    const logs = data.logs || [];
    totalPages = data.pages || 1;

    document.getElementById("logsStatsText").textContent = `Total Attempts: ${data.total} logged`;
    document.getElementById("pageInfoText").textContent = `Page ${data.page} of ${totalPages} (${data.total} total)`;

    document.getElementById("prevPageBtn").disabled = (currentPage <= 1);
    document.getElementById("nextPageBtn").disabled = (currentPage >= totalPages);

    if (logs.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:24px; color:var(--text-muted);">No login records found matching criteria.</td></tr>`;
      return;
    }

    tableBody.innerHTML = logs.map(l => {
      const isSuccess = l.status === "success";
      const statusBadge = isSuccess
        ? `<span class="badge badge-success">SUCCESS</span>`
        : `<span class="badge badge-failed">FAILED</span>`;

      const userDisplay = l.user_name
        ? `<strong>${escapeHtml(l.user_name)}</strong> <span style="font-size:11px; color:var(--text-muted);">(ID #${l.user_id})</span>`
        : `<span style="font-size:12px; color:var(--text-muted); font-style:italic;">Unregistered / Unknown</span>`;

      return `
        <tr>
          <td><strong>#LOG-${l.id}</strong></td>
          <td><code>${escapeHtml(l.email_tried)}</code></td>
          <td>${userDisplay}</td>
          <td><span style="font-family:monospace; font-size:12px;">${escapeHtml(l.ip_address)}</span></td>
          <td>${statusBadge}</td>
          <td style="font-size: 12px; color: var(--text-muted);">${l.login_time || "--"}</td>
        </tr>
      `;
    }).join("");

    AdminCommon.updateTimestamp(data.timestamp);

  } catch (err) {
    console.error("Error loading login logs:", err);
  }
}
