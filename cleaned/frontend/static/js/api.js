// Centralized API Client, Auth Guard, Global Markdown Formatter & Theme Switcher
const API_BASE = "";

function getAuthToken() {
  return localStorage.getItem("plantiq_token");
}

function setAuthToken(token) {
  if (token) localStorage.setItem("plantiq_token", token);
}

function clearAuthToken() {
  localStorage.removeItem("plantiq_token");
  localStorage.removeItem("plantiq_user");
}

function getAuthHeaders() {
  const token = getAuthToken();
  const headers = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = { ...getAuthHeaders(), ...(options.headers || {}) };
  const config = { ...options, headers };

  try {
    const res = await fetch(url, config);
    if (res.status === 401) {
      console.warn(`[401 Unauthorized] on ${endpoint}. Clearing token & redirecting to /auth.`);
      clearAuthToken();
      if (!window.location.pathname.endsWith("/auth")) {
        window.location.replace("/auth");
      }
    }
    return res;
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err);
    throw err;
  }
}

// Global Markdown & Rich Text Formatter
function formatMarkdown(text) {
  if (!text) return "";
  return text
    .replace(/^### (.*$)/gim, '<strong style="display:block; margin:6px 0 2px 0;">$1</strong>')
    .replace(/^## (.*$)/gim, '<h4 style="margin: 8px 0 4px 0; color:var(--primary);">$1</h4>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^\* (.*$)/gim, '• $1<br>')
    .replace(/^\- (.*$)/gim, '• $1<br>')
    .replace(/\n/g, '<br>');
}
window.formatMarkdown = formatMarkdown;

// Global Auth Guard
async function checkAuthGuard() {
  const isAuthPage = window.location.pathname.endsWith("/auth");
  const token = getAuthToken();

  if (!token) {
    if (!isAuthPage) {
      window.location.replace("/auth");
    }
    return;
  }

  // Token exists -> verify valid session with backend
  try {
    const res = await fetch("/api/auth/me", {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!res.ok) {
      clearAuthToken();
      if (!isAuthPage) {
        window.location.replace("/auth");
      }
    } else if (isAuthPage) {
      window.location.replace("/");
    }
  } catch(e){}
}

// Dark Mode Theme Controller
function initTheme() {
  const saved = localStorage.getItem("plantiq_theme") || "light";
  setTheme(saved);

  document.querySelectorAll(".btn-theme-toggle").forEach(btn => {
    btn.onclick = () => {
      const current = document.documentElement.getAttribute("data-theme") || "light";
      const next = current === "dark" ? "light" : "dark";
      setTheme(next);
    };
  });
}

function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("plantiq_theme", theme);
  document.querySelectorAll(".btn-theme-toggle i").forEach(icon => {
    icon.setAttribute("data-lucide", theme === "dark" ? "sun" : "moon");
  });
  if (window.lucide) lucide.createIcons();
}

checkAuthGuard();
document.addEventListener("DOMContentLoaded", () => initTheme());
