/**
 * frontend/js/api.js - Unified Client API Helper
 * Formats all fares in Indian Rupees (₹).
 */

const API = {
  baseUrl: "/api",

  getToken() {
    return localStorage.getItem("transitport_token");
  },

  getUser() {
    const raw = localStorage.getItem("transitport_user");
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  setAuth(token, user) {
    if (token) localStorage.setItem("transitport_token", token);
    if (user) localStorage.setItem("transitport_user", JSON.stringify(user));
  },

  clearAuth() {
    localStorage.removeItem("transitport_token");
    localStorage.removeItem("transitport_user");
  },

  async request(endpoint, options = {}) {
    const url = endpoint.startsWith("http") ? endpoint : `${this.baseUrl}${endpoint}`;
    const headers = options.headers || {};

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    if (options.body && !(options.body instanceof FormData)) {
      headers["Content-Type"] = "application/json";
      options.body = typeof options.body === "string" ? options.body : JSON.stringify(options.body);
    }

    options.headers = headers;

    try {
      const res = await fetch(url, options);
      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        const errorMsg = data.detail || data.message || `Request failed with status ${res.status}`;
        throw new Error(errorMsg);
      }
      return data;
    } catch (err) {
      console.error(`API Error [${options.method || 'GET'} ${endpoint}]:`, err.message);
      throw err;
    }
  },

  // Auth endpoints
  async register(name, email, password) {
    const data = await this.request("/register", {
      method: "POST",
      body: { name, email, password }
    });
    this.setAuth(data.token, data.user);
    return data;
  },

  async login(email, password) {
    const data = await this.request("/login", {
      method: "POST",
      body: { email, password }
    });
    this.setAuth(data.token, data.user);
    return data;
  },

  async logout() {
    try {
      await this.request("/logout", { method: "POST" });
    } catch (e) {
      // Ignore network errors on logout
    }
    this.clearAuth();
    window.location.href = "/login.html";
  },

  async getCurrentUser() {
    return this.request("/me");
  },

  // Trips endpoints
  async getTrips(params = {}) {
    const searchParams = new URLSearchParams();
    if (params.type && params.type !== "all" && params.type !== "allmodes") {
      searchParams.set("type", params.type);
    }
    if (params.origin) searchParams.set("origin", params.origin);
    if (params.destination) searchParams.set("destination", params.destination);
    if (params.date) searchParams.set("date", params.date);
    if (params.max_price) searchParams.set("max_price", params.max_price);

    const qs = searchParams.toString();
    return this.request(`/trips${qs ? '?' + qs : ''}`);
  },

  async getTrip(id) {
    return this.request(`/trips/${id}`);
  },

  async getPopularRoutes() {
    return this.request("/popular-routes");
  },

  // Bookings endpoints
  async createBooking(tripId, passengerNames, seatsBooked) {
    return this.request("/bookings", {
      method: "POST",
      body: {
        trip_id: parseInt(tripId, 10),
        passenger_names: passengerNames,
        seats_booked: parseInt(seatsBooked, 10)
      }
    });
  },

  async getMyBookings() {
    return this.request("/my-bookings");
  },

  async getBooking(id) {
    return this.request(`/bookings/${id}`);
  },

  async cancelBooking(id) {
    return this.request(`/bookings/${id}/cancel`, {
      method: "POST"
    });
  },

  // Admin endpoints
  async getAdminStats() {
    return this.request("/admin/stats");
  },

  async getAdminUsers(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.request(`/admin/users${qs ? '?' + qs : ''}`);
  },

  async getAdminLoginLogs(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.request(`/admin/login-logs${qs ? '?' + qs : ''}`);
  },

  async getAdminTrips(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.request(`/admin/trips${qs ? '?' + qs : ''}`);
  },

  async getAdminBookings(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.request(`/admin/bookings${qs ? '?' + qs : ''}`);
  },

  async getAdminActivity(limit = 20) {
    return this.request(`/admin/activity?limit=${limit}`);
  },

  async syncTrips() {
    return this.request("/admin/sync-trips", { method: "POST" });
  },

  // Customer header setup helper
  setupHeaderAuth() {
    const navAuth = document.getElementById("navAuth");
    if (!navAuth) return;

    const user = this.getUser();
    if (user) {
      let adminLink = "";
      if (user.role === "admin") {
        adminLink = `<a href="/admin/dashboard.html" class="btn btn-secondary btn-sm" style="margin-right:8px;">Admin Monitor</a>`;
      }
      navAuth.innerHTML = `
        ${adminLink}
        <span class="user-badge">${escapeHtml(user.name)}</span>
        <button id="logoutBtn" class="btn btn-secondary btn-sm">Log out</button>
      `;
      document.getElementById("logoutBtn")?.addEventListener("click", () => this.logout());
    } else {
      navAuth.innerHTML = `
        <a href="/login.html" class="btn btn-secondary btn-sm">Log in</a>
        <a href="/login.html?tab=register" class="btn btn-primary btn-sm">Sign up</a>
      `;
    }
  },

  formatCurrency(amount) {
    const num = Number(amount || 0);
    return "₹" + num.toLocaleString("en-IN", { maximumFractionDigits: 2 });
  }
};

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
