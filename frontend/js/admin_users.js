/**
 * frontend/js/admin_users.js - Admin Users Table Controller
 */

let currentPage = 1;
const pageLimit = 10;
let totalPages = 1;

document.addEventListener("DOMContentLoaded", () => {
  AdminCommon.init(refreshUsers);

  const searchInput = document.getElementById("searchInput");
  const sortSelect = document.getElementById("sortSelect");

  let searchTimeout = null;
  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      currentPage = 1;
      refreshUsers();
    }, 300);
  });

  sortSelect.addEventListener("change", () => {
    currentPage = 1;
    refreshUsers();
  });

  document.getElementById("manualRefreshBtn")?.addEventListener("click", () => {
    refreshUsers();
  });

  document.getElementById("prevPageBtn")?.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      refreshUsers();
    }
  });

  document.getElementById("nextPageBtn")?.addEventListener("click", () => {
    if (currentPage < totalPages) {
      currentPage++;
      refreshUsers();
    }
  });
});

async function refreshUsers() {
  const tableBody = document.getElementById("usersTableBody");
  const search = document.getElementById("searchInput")?.value.trim() || "";
  const sort = document.getElementById("sortSelect")?.value || "created_at_desc";

  try {
    const data = await API.getAdminUsers({
      search,
      sort,
      page: currentPage,
      limit: pageLimit
    });

    const users = data.users || [];
    totalPages = data.pages || 1;

    document.getElementById("userStatsText").textContent = `Total Accounts: ${data.total} registered`;
    document.getElementById("pageInfoText").textContent = `Page ${data.page} of ${totalPages} (${data.total} total)`;

    document.getElementById("prevPageBtn").disabled = (currentPage <= 1);
    document.getElementById("nextPageBtn").disabled = (currentPage >= totalPages);

    if (users.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:24px; color:var(--text-muted);">No users found matching query.</td></tr>`;
      return;
    }

    tableBody.innerHTML = users.map(u => {
      const roleBadge = u.role === "admin"
        ? `<span class="badge badge-role-admin">ADMIN</span>`
        : `<span class="badge badge-role-user">USER</span>`;

      return `
        <tr>
          <td><strong>#USR-${u.id}</strong></td>
          <td><strong>${escapeHtml(u.name)}</strong></td>
          <td>${escapeHtml(u.email)}</td>
          <td>${roleBadge}</td>
          <td>${u.bookings_count} booking(s)</td>
          <td style="font-size: 12px; color: var(--text-muted);">${u.created_at || "--"}</td>
        </tr>
      `;
    }).join("");

    AdminCommon.updateTimestamp(data.timestamp);

  } catch (err) {
    console.error("Error loading users table:", err);
  }
}
