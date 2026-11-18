/**
 * frontend/js/admin_common.js - Shared Admin Panel Controller
 * Handles admin authentication guard, 5-second polling timer,
 * "Last updated: HH:MM:SS" status, and active navigation highlighting.
 */

const AdminCommon = {
  pollingIntervalMs: 5000,
  timerId: null,

  init(refreshCallback) {
    this.checkAdminAuth();
    this.highlightActiveNav();

    // Attach admin logout
    document.getElementById("adminLogoutBtn")?.addEventListener("click", (e) => {
      e.preventDefault();
      API.logout();
    });

    // Run first refresh immediately
    if (typeof refreshCallback === "function") {
      refreshCallback();

      // Setup 5-second recurring polling
      this.timerId = setInterval(() => {
        refreshCallback();
      }, this.pollingIntervalMs);
    }
  },

  checkAdminAuth() {
    const user = API.getUser();
    const token = API.getToken();

    if (!token || !user) {
      const returnUrl = encodeURIComponent(window.location.href);
      window.location.href = `/login.html?returnUrl=${returnUrl}`;
      return false;
    }

    if (user.role !== "admin") {
      alert("Access Denied: You must be logged in as an administrator (e.g. admin@transport.com / admin123) to view the Database Monitor.");
      window.location.href = "/index.html";
      return false;
    }

    // Set admin name in sidebar if element exists
    const adminNameEl = document.getElementById("adminUserDisplay");
    if (adminNameEl) {
      adminNameEl.textContent = user.name || user.email;
    }

    return true;
  },

  updateTimestamp(serverTime) {
    const timeEl = document.getElementById("lastUpdatedTime");
    if (!timeEl) return;

    if (serverTime) {
      timeEl.textContent = serverTime;
    } else {
      const now = new Date();
      timeEl.textContent = now.toTimeString().split(" ")[0];
    }
  },

  highlightActiveNav() {
    const currentPath = window.location.pathname.toLowerCase();
    const navLinks = document.querySelectorAll(".admin-nav a");

    navLinks.forEach(link => {
      const href = link.getAttribute("href")?.toLowerCase() || "";
      if (currentPath.includes(href) && href !== "") {
        link.classList.add("active");
      } else {
        link.classList.remove("active");
      }
    });
  }
};
