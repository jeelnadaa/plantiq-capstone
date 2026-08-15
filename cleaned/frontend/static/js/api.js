// Centralized API Client, Dynamic Server IP Manager, Auth Guard & Theme Switcher

function getApiBase() {
  const custom = localStorage.getItem("plantiq_server_url");
  if (custom && custom.trim()) {
    let clean = custom.trim().replace(/\/+$/, "");
    if (!clean.startsWith("http://") && !clean.startsWith("https://")) {
      clean = "http://" + clean;
    }
    return clean;
  }
  // In native app environment (file://, capacitor://, or localhost in Capacitor), fallback to stored or default
  if (window.location.protocol === "file:" || window.location.protocol === "capacitor:" || window.location.hostname === "localhost") {
    return localStorage.getItem("plantiq_server_url") || "http://192.168.1.100:8000";
  }
  return "";
}

function setApiBase(url) {
  if (!url || !url.trim()) {
    localStorage.removeItem("plantiq_server_url");
  } else {
    let clean = url.trim().replace(/\/+$/, "");
    if (!clean.startsWith("http://") && !clean.startsWith("https://")) {
      clean = "http://" + clean;
    }
    localStorage.setItem("plantiq_server_url", clean);
  }
  updateServerStatusIndicator();
}

function navigateTo(route) {
  const isStaticApp = window.location.pathname.endsWith(".html") || window.location.protocol === "file:" || window.location.protocol === "capacitor:" || window.location.hostname === "localhost";
  if (isStaticApp) {
    if (route === "/" || route === "" || route === "/scanner") {
      window.location.href = "index.html";
    } else {
      const clean = route.replace(/^\//, "").replace(/\.html$/, "");
      window.location.href = `${clean}.html`;
    }
  } else {
    window.location.href = route;
  }
}
window.navigateTo = navigateTo;

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
  const base = getApiBase();
  const url = `${base}${endpoint}`;
  const headers = { ...getAuthHeaders(), ...(options.headers || {}) };
  const config = { ...options, headers };

  try {
    const res = await fetch(url, config);
    if (res.status === 401) {
      console.warn(`[401 Unauthorized] on ${endpoint}. Redirecting to auth.`);
      clearAuthToken();
      if (!window.location.pathname.includes("auth")) {
        navigateTo("/auth");
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
  const isAuthPage = window.location.pathname.includes("auth");
  const token = getAuthToken();

  if (!token) {
    if (!isAuthPage) {
      navigateTo("/auth");
    }
    return;
  }

  // Token exists -> verify valid session with backend
  try {
    const base = getApiBase();
    const res = await fetch(`${base}/api/auth/me`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    if (!res.ok) {
      clearAuthToken();
      if (!isAuthPage) {
        navigateTo("/auth");
      }
    } else if (isAuthPage) {
      navigateTo("/");
    }
  } catch(e){
    // If offline/server not set yet, stay on page to allow user to configure IP
    console.warn("Could not verify session with backend (check server connection)");
  }
}

// Server Backend Configuration Modal & Connectivity
function initServerSettings() {
  const btnOpen = document.querySelectorAll(".btn-open-server-settings");
  const modal = document.getElementById("server-settings-modal");
  const btnClose = document.getElementById("btn-close-server-settings");
  const inputUrl = document.getElementById("server-ip-input");
  const btnTest = document.getElementById("btn-test-server-connection");
  const btnSave = document.getElementById("btn-save-server-settings");
  const btnReset = document.getElementById("btn-reset-server-settings");
  const testResult = document.getElementById("server-test-result");

  btnOpen.forEach(btn => {
    btn.onclick = () => {
      if (inputUrl) {
        inputUrl.value = localStorage.getItem("plantiq_server_url") || getApiBase();
      }
      if (testResult) testResult.innerHTML = "";
      if (modal) modal.classList.remove("hidden");
    };
  });

  if (btnClose && modal) {
    btnClose.onclick = () => modal.classList.add("hidden");
  }

  if (btnTest) {
    btnTest.onclick = async () => {
      const val = (inputUrl?.value || "").trim();
      if (!val) {
        testResult.innerHTML = `<span style="color:var(--danger);">Please enter a server IP (e.g. 192.168.1.15:8000).</span>`;
        return;
      }
      let targetUrl = val.replace(/\/+$/, "");
      if (!targetUrl.startsWith("http://") && !targetUrl.startsWith("https://")) {
        targetUrl = "http://" + targetUrl;
      }
      testResult.innerHTML = `<span style="color:var(--primary);"><i data-lucide="loader-2" class="spin"></i> Pinging ${targetUrl}/health...</span>`;
      if (window.lucide) lucide.createIcons();

      const startTime = Date.now();
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 4000);
        const res = await fetch(`${targetUrl}/health`, { signal: controller.signal });
        clearTimeout(timeout);
        const latency = Date.now() - startTime;
        if (res.ok) {
          testResult.innerHTML = `<span style="color:var(--success); font-weight:700;">🟢 Connected (${latency}ms latency). PlantIQ backend online!</span>`;
        } else {
          testResult.innerHTML = `<span style="color:var(--danger);">⚠️ Server reached but returned HTTP ${res.status}.</span>`;
        }
      } catch (err) {
        testResult.innerHTML = `<span style="color:var(--danger); font-weight:700;">🔴 Cannot reach ${targetUrl}. Ensure laptop is running python run.py and on same Wi-Fi.</span>`;
      }
    };
  }

  if (btnSave) {
    btnSave.onclick = () => {
      const val = (inputUrl?.value || "").trim();
      setApiBase(val);
      if (modal) modal.classList.add("hidden");
      alert(currentLang === "kn" ? "ಸರ್ವರ್ ವಿಳಾಸವನ್ನು ನವೀಕರಿಸಲಾಗಿದೆ!" : "Server URL updated successfully!");
      window.location.reload();
    };
  }

  if (btnReset) {
    btnReset.onclick = () => {
      localStorage.removeItem("plantiq_server_url");
      if (inputUrl) inputUrl.value = "";
      if (modal) modal.classList.add("hidden");
      alert("Reset to default host.");
      window.location.reload();
    };
  }

  updateServerStatusIndicator();
}

async function updateServerStatusIndicator() {
  const dot = document.querySelectorAll(".server-status-dot");
  if (dot.length === 0) return;

  const base = getApiBase();
  try {
    const res = await fetch(`${base}/health`, { signal: AbortSignal.timeout(2500) });
    if (res.ok) {
      dot.forEach(d => {
        d.style.background = "#22c55e";
        d.title = `Server Connected: ${base}`;
      });
    } else {
      dot.forEach(d => {
        d.style.background = "#eab308";
        d.title = `Server Issue (HTTP ${res.status})`;
      });
    }
  } catch(e) {
    dot.forEach(d => {
      d.style.background = "#ef4444";
      d.title = `Server Disconnected (${base || 'local'}). Click to change IP.`;
    });
  }
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
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initServerSettings();
});

// Global External App / Intent Opener (WhatsApp, Maps, Calls)
function openExternalApp(url) {
  if (!url) return;
  try {
    if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Browser && !url.startsWith("tel:") && !url.startsWith("whatsapp:")) {
      window.Capacitor.Plugins.Browser.open({ url: url });
    } else {
      window.open(url, "_system") || (window.location.href = url);
    }
  } catch(e) {
    window.location.href = url;
  }
}
window.openExternalApp = openExternalApp;

// Global Native Back Button & Modal Dismiss Listener
function initNativeBackButton() {
  if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.App) {
    window.Capacitor.Plugins.App.addListener("backButton", (data) => {
      // 1. Dismiss any open modal
      const openModals = document.querySelectorAll(".modal-overlay:not(.hidden)");
      if (openModals.length > 0) {
        openModals.forEach(m => m.classList.add("hidden"));
        return;
      }

      // 2. If on subpage (chat, marketplace, history, profile, auth), return to Scanner Home
      const path = window.location.pathname;
      if (!path.endsWith("index.html") && !path.endsWith("/")) {
        navigateTo("/");
        return;
      }

      // 3. On Home -> exit app
      window.Capacitor.Plugins.App.exitApp();
    });
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initNativeBackButton();
});
