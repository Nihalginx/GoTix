/**
 * frontend/js/auth.js - Authentication Page Controller (Login & Registration)
 */

document.addEventListener("DOMContentLoaded", () => {
  API.setupHeaderAuth();

  const tabLoginBtn = document.getElementById("tabLoginBtn");
  const tabRegisterBtn = document.getElementById("tabRegisterBtn");
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const authMessage = document.getElementById("authMessage");

  // Determine return URL
  const urlParams = new URLSearchParams(window.location.search);
  const returnUrl = urlParams.get("returnUrl") || "";
  const initialTab = urlParams.get("tab") || "login";

  function showTab(tab) {
    clearMessage();
    if (tab === "register") {
      tabRegisterBtn.classList.add("active");
      tabLoginBtn.classList.remove("active");
      registerForm.style.display = "block";
      loginForm.style.display = "none";
    } else {
      tabLoginBtn.classList.add("active");
      tabRegisterBtn.classList.remove("active");
      loginForm.style.display = "block";
      registerForm.style.display = "none";
    }
  }

  if (initialTab === "register") {
    showTab("register");
  }

  tabLoginBtn.addEventListener("click", () => showTab("login"));
  tabRegisterBtn.addEventListener("click", () => showTab("register"));

  function showMessage(text, isError = true) {
    authMessage.textContent = text;
    authMessage.className = isError ? "form-msg error" : "form-msg success";
  }

  function clearMessage() {
    authMessage.textContent = "";
    authMessage.className = "form-msg";
    authMessage.style.display = "none";
  }

  // Handle Login Submit
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearMessage();

    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value;

    try {
      const res = await API.login(email, password);
      showMessage("Login successful! Redirecting...", false);

      setTimeout(() => {
        if (returnUrl) {
          window.location.href = returnUrl;
        } else if (res.user && res.user.role === "admin") {
          window.location.href = "/admin/dashboard.html";
        } else {
          window.location.href = "/index.html";
        }
      }, 700);

    } catch (err) {
      showMessage(err.message || "Invalid email or password. Attempt logged to audit trail.");
    }
  });

  // Handle Register Submit
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearMessage();

    const name = document.getElementById("regName").value.trim();
    const email = document.getElementById("regEmail").value.trim();
    const password = document.getElementById("regPassword").value;
    const confirmPassword = document.getElementById("regConfirmPassword").value;

    if (password !== confirmPassword) {
      showMessage("Passwords do not match.");
      return;
    }

    try {
      const res = await API.register(name, email, password);
      showMessage("Account created successfully! Redirecting...", false);

      setTimeout(() => {
        if (returnUrl) {
          window.location.href = returnUrl;
        } else {
          window.location.href = "/index.html";
        }
      }, 700);

    } catch (err) {
      showMessage(err.message || "Registration failed.");
    }
  });
});
