// Dual Location Manager (Auto GPS & Manual Entry & GMaps Guide)
const LocationManager = {
  coords: {
    lat: 13.3161,
    lng: 75.7720,
    mode: "gps", // 'gps' or 'manual'
    allowed: true
  },

  envData: null,
  isFetchingEnv: false,

  init() {
    const stored = localStorage.getItem("plantiq_coords");
    if (stored) {
      try { this.coords = JSON.parse(stored); } catch(e){}
    }
    this.bindUI();
    if (this.coords.mode === "gps") {
      this.requestGPS();
    } else {
      this.updateUI();
      this.fetchEnvironment();
    }
  },

  save() {
    localStorage.setItem("plantiq_coords", JSON.stringify(this.coords));
    this.updateUI();
    this.fetchEnvironment();
  },

  requestGPS() {
    if ("geolocation" in navigator) {
      const statusEl = document.getElementById("loc-status-text");
      if (statusEl) statusEl.textContent = currentLang === "kn" ? "ಜಿಪಿಎಸ್ ಪಡೆಯಲಾಗುತ್ತಿದೆ..." : "Acquiring GPS...";
      
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          this.coords.lat = pos.coords.latitude;
          this.coords.lng = pos.coords.longitude;
          this.coords.mode = "gps";
          this.coords.allowed = true;
          this.save();
        },
        (err) => {
          console.warn("GPS Access Error:", err.message);
          this.coords.lat = 13.3161;
          this.coords.lng = 75.7720;
          this.coords.mode = "gps";
          this.save();
        },
        { timeout: 8000 }
      );
    } else {
      this.updateUI();
      this.fetchEnvironment();
    }
  },

  debounceTimer: null,

  handleManualCoordChange(source = "main") {
    let latInput = document.getElementById("input-manual-lat");
    let lngInput = document.getElementById("input-manual-lng");
    if (source === "chat") {
      latInput = document.getElementById("input-chat-manual-lat");
      lngInput = document.getElementById("input-chat-manual-lng");
    }
    if (!latInput || !lngInput) return;

    const latRaw = latInput.value.trim();
    const lngRaw = lngInput.value.trim();

    if (latRaw === "" || lngRaw === "") {
      this.coords.lat = null;
      this.coords.lng = null;
      this.coords.mode = "manual";
      this.coords.allowed = false;
      this.envData = { available: false };
      localStorage.setItem("plantiq_coords", JSON.stringify(this.coords));
      this.updateUI();
      this.renderEnvironmentUI();
      return;
    }

    const latVal = parseFloat(latRaw);
    const lngVal = parseFloat(lngRaw);

    if (!isNaN(latVal) && !isNaN(lngVal) && latVal >= -90.0 && latVal <= 90.0 && lngVal >= -180.0 && lngVal <= 180.0) {
      this.coords.lat = latVal;
      this.coords.lng = lngVal;
      this.coords.mode = "manual";
      this.coords.allowed = true;
      this.save();
    }
  },

  async fetchEnvironment() {
    this.isFetchingEnv = true;
    this.renderEnvironmentUI();
    const refreshBtn = document.getElementById("btn-refresh-env");
    if (refreshBtn) refreshBtn.classList.add("loading");

    try {
      const lat = this.coords ? this.coords.lat : null;
      const lng = this.coords ? this.coords.lng : null;
      if (lat == null || lng == null || isNaN(lat) || isNaN(lng)) {
        this.envData = { available: false };
        return;
      }
      const url = `/api/environment/live?latitude=${lat}&longitude=${lng}`;
      const res = await apiRequest(url);
      if (res.ok) {
        this.envData = await res.json();
      } else {
        this.envData = { available: false };
      }
    } catch (e) {
      console.warn("Failed to fetch environmental data:", e);
      this.envData = { available: false };
    } finally {
      this.isFetchingEnv = false;
      if (refreshBtn) refreshBtn.classList.remove("loading");
      this.renderEnvironmentUI();
    }
  },

  renderEnvironmentUI() {
    const tempEl = document.getElementById("env-val-temp");
    const unitTempEl = document.getElementById("env-unit-temp");
    const feelsEl = document.getElementById("env-val-feels");
    const humEl = document.getElementById("env-val-humidity");
    const unitHumEl = document.getElementById("env-unit-humidity");
    const rainEl = document.getElementById("env-val-rain");
    const unitRainEl = document.getElementById("env-unit-rain");
    const elevEl = document.getElementById("env-val-elevation");
    const unitElevEl = document.getElementById("env-unit-elevation");
    const riskTextEl = document.getElementById("env-risk-text");
    const riskBadgeEl = document.getElementById("env-risk-badge");
    const riskBannerEl = document.getElementById("env-risk-banner");

    // 1. Loading State
    if (this.isFetchingEnv) {
      if (riskTextEl) riskTextEl.textContent = currentLang === "kn" ? "ವಾತಾವರಣದ ಲೈವ್ ಮಾಹಿತಿ ಪಡೆಯಲಾಗುತ್ತಿದೆ..." : "Loading live site environmental data...";
      if (riskBadgeEl) {
        riskBadgeEl.textContent = currentLang === "kn" ? "ಲೋಡ್ ಆಗುತ್ತಿದೆ" : "LOADING";
        riskBadgeEl.style.background = "var(--primary-light)";
        riskBadgeEl.style.color = "var(--primary)";
      }
      if (riskBannerEl) riskBannerEl.style.background = "var(--primary-light)";
      return;
    }

    // 2. Strict Zero Mock Data: Not Available State
    if (!this.envData || !this.envData.available || this.envData.temperature == null) {
      const notAvail = currentLang === "kn" ? "ಲಭ್ಯವಿಲ್ಲ" : "Not Available";
      if (tempEl) { tempEl.textContent = notAvail; tempEl.style.fontSize = "0.85rem"; }
      if (unitTempEl) unitTempEl.textContent = "";
      if (feelsEl) feelsEl.textContent = "";

      if (humEl) { humEl.textContent = notAvail; humEl.style.fontSize = "0.85rem"; }
      if (unitHumEl) unitHumEl.textContent = "";

      if (rainEl) { rainEl.textContent = notAvail; rainEl.style.fontSize = "0.85rem"; }
      if (unitRainEl) unitRainEl.textContent = "";

      if (elevEl) { elevEl.textContent = notAvail; elevEl.style.fontSize = "0.85rem"; }
      if (unitElevEl) unitElevEl.textContent = "";

      if (riskBadgeEl) {
        riskBadgeEl.textContent = notAvail;
        riskBadgeEl.style.background = "var(--text-muted, #64748b)";
        riskBadgeEl.style.color = "#ffffff";
      }
      if (riskBannerEl) {
        riskBannerEl.style.background = "var(--bg-card-subtle, rgba(0,0,0,0.04))";
      }
      if (riskTextEl) {
        riskTextEl.textContent = currentLang === "kn" ? "ಲೈವ್ ವಾತಾವರಣದ ಸೆನ್ಸರ್ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ." : "Live microclimate sensor data unavailable.";
      }
      if (window.lucide) lucide.createIcons();
      return;
    }

    // 3. Live Data Available: Digits and Units in standard English/universal, all text localized
    const d = this.envData;
    if (tempEl) {
      tempEl.textContent = Number(d.temperature).toFixed(1);
      tempEl.style.fontSize = "1.1rem";
    }
    if (unitTempEl) unitTempEl.textContent = "°C";
    if (feelsEl) {
      const feelsPrefix = currentLang === "kn" ? "ಅನುಭವ" : "Feels";
      const feelsVal = d.feels_like != null ? Number(d.feels_like).toFixed(1) : Number(d.temperature).toFixed(1);
      feelsEl.textContent = `(${feelsPrefix}: ${feelsVal}°C)`;
    }

    if (humEl) {
      humEl.textContent = Math.round(Number(d.humidity));
      humEl.style.fontSize = "1.1rem";
    }
    if (unitHumEl) unitHumEl.textContent = "%";

    if (rainEl) {
      const r = d.rainfall != null ? Number(d.rainfall).toFixed(1) : "0.0";
      rainEl.textContent = r;
      rainEl.style.fontSize = "1.1rem";
    }
    if (unitRainEl) unitRainEl.textContent = " mm";

    if (elevEl) {
      const el = d.elevation != null ? Math.round(Number(d.elevation)) : "--";
      elevEl.textContent = el;
      elevEl.style.fontSize = "1.1rem";
    }
    if (unitElevEl) unitElevEl.textContent = " m";

    // Incubation risk styling
    const riskLvl = (d.risk_level || "low").toLowerCase();
    if (riskBadgeEl) {
      if (riskLvl === "high") {
        riskBadgeEl.textContent = currentLang === "kn" ? "ಹೆಚ್ಚಿನ ಅಪಾಯ" : "HIGH RISK";
        riskBadgeEl.style.background = "var(--cherry, #ff2a6d)";
        riskBadgeEl.style.color = "#ffffff";
        if (riskBannerEl) riskBannerEl.style.background = "var(--danger-light, #ffe4e6)";
        if (riskTextEl) {
          riskTextEl.textContent = currentLang === "kn"
            ? "ಎಚ್ಚರಿಕೆ: ಹೆಚ್ಚಿನ ಆರ್ದ್ರತೆ - ಎಲೆ ತುಕ್ಕು ಶಿಲೀಂಧ್ರ ಹರಡುವಿಕೆ ಹೆಚ್ಚಾಗಬಹುದು!"
            : "High Infection Risk: Sustained humidity favors Coffee Leaf Rust spore germination!";
        }
      } else if (riskLvl === "moderate") {
        riskBadgeEl.textContent = currentLang === "kn" ? "ಮಧ್ಯಮ ಅಪಾಯ" : "MODERATE";
        riskBadgeEl.style.background = "var(--orange, #ff7700)";
        riskBadgeEl.style.color = "#ffffff";
        if (riskBannerEl) riskBannerEl.style.background = "var(--primary-light)";
        if (riskTextEl) {
          riskTextEl.textContent = currentLang === "kn"
            ? "ಮಧ್ಯಮ ಅಪಾಯ: ಎಲೆಯ ತೇವಾಂಶ ಮತ್ತು ನೆರಳಿನ ಸಾಂದ್ರತೆಯನ್ನು ಗಮನಿಸಿ."
            : "Moderate Risk: Monitor canopy spore activity and wet leaf duration.";
        }
      } else {
        riskBadgeEl.textContent = currentLang === "kn" ? "ಕಡಿಮೆ ಅಪಾಯ" : "LOW RISK";
        riskBadgeEl.style.background = "#10b981";
        riskBadgeEl.style.color = "#ffffff";
        if (riskBannerEl) riskBannerEl.style.background = "#d1fae5";
        if (riskTextEl) {
          riskTextEl.textContent = currentLang === "kn"
            ? "ಅನುಕೂಲಕರ ವಾತಾವರಣ: ಸಿಂಪರಣೆಗೆ ಮತ್ತು ಬೆಳೆ ಪೋಷಣೆಗೆ ಸೂಕ್ತ ಸಮಯ."
            : "Favorable Weather: Ideal window for foliar nourishment and spraying.";
        }
      }
    }
    if (window.lucide) lucide.createIcons();
  },

  bindUI() {
    // 1. Scanner Page Controls
    const btnGps = document.getElementById("btn-mode-gps");
    const btnManual = document.getElementById("btn-mode-manual");
    const manualInputs = document.getElementById("manual-lat-lng-container");
    const latInput = document.getElementById("input-manual-lat");
    const lngInput = document.getElementById("input-manual-lng");
    const btnRefreshEnv = document.getElementById("btn-refresh-env");
    const btnApplyManual = document.getElementById("btn-apply-manual-coords");

    if (btnRefreshEnv) {
      btnRefreshEnv.onclick = (e) => {
        e.preventDefault();
        this.fetchEnvironment();
      };
    }

    if (btnGps && btnManual) {
      btnGps.onclick = () => {
        this.coords.mode = "gps";
        btnGps.className = "btn btn-sm btn-primary";
        btnManual.className = "btn btn-sm btn-secondary";
        if (manualInputs) manualInputs.classList.add("hidden");
        this.requestGPS();
      };

      btnManual.onclick = () => {
        this.coords.mode = "manual";
        btnGps.className = "btn btn-sm btn-secondary";
        btnManual.className = "btn btn-sm btn-primary";
        if (manualInputs) {
          manualInputs.classList.remove("hidden");
          if (latInput && this.coords.lat != null) latInput.value = this.coords.lat.toFixed(4);
          if (lngInput && this.coords.lng != null) lngInput.value = this.coords.lng.toFixed(4);
        }
        this.save();
      };
    }

    const triggerDebounced = (src = "main") => {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => {
        this.handleManualCoordChange(src);
      }, 500);
    };

    if (latInput) {
      latInput.oninput = () => triggerDebounced("main");
      latInput.onchange = () => this.handleManualCoordChange("main");
      latInput.onkeydown = (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          this.handleManualCoordChange("main");
        }
      };
    }

    if (lngInput) {
      lngInput.oninput = () => triggerDebounced("main");
      lngInput.onchange = () => this.handleManualCoordChange("main");
      lngInput.onkeydown = (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          this.handleManualCoordChange("main");
        }
      };
    }

    if (btnApplyManual) {
      btnApplyManual.onclick = (e) => {
        e.preventDefault();
        this.handleManualCoordChange("main");
      };
    }

    // 2. Chat Page Controls
    const btnToggleChatLoc = document.getElementById("btn-toggle-chat-loc");
    const chatManualContainer = document.getElementById("chat-manual-coords-container");
    const btnChatGps = document.getElementById("btn-chat-mode-gps");
    const btnChatManual = document.getElementById("btn-chat-mode-manual");
    const chatManualInputs = document.getElementById("chat-manual-inputs");
    const chatLatInput = document.getElementById("input-chat-manual-lat");
    const chatLngInput = document.getElementById("input-chat-manual-lng");
    const btnApplyChatManual = document.getElementById("btn-apply-chat-manual");

    if (btnToggleChatLoc && chatManualContainer) {
      btnToggleChatLoc.onclick = (e) => {
        e.preventDefault();
        chatManualContainer.classList.toggle("hidden");
        if (window.lucide) lucide.createIcons();
      };
    }

    if (btnChatGps && btnChatManual) {
      btnChatGps.onclick = () => {
        this.coords.mode = "gps";
        btnChatGps.className = "btn btn-sm btn-primary";
        btnChatManual.className = "btn btn-sm btn-secondary";
        if (chatManualInputs) chatManualInputs.classList.add("hidden");
        this.requestGPS();
      };

      btnChatManual.onclick = () => {
        this.coords.mode = "manual";
        btnChatGps.className = "btn btn-sm btn-secondary";
        btnChatManual.className = "btn btn-sm btn-primary";
        if (chatManualInputs) {
          chatManualInputs.classList.remove("hidden");
          if (chatLatInput && this.coords.lat != null) chatLatInput.value = this.coords.lat.toFixed(4);
          if (chatLngInput && this.coords.lng != null) chatLngInput.value = this.coords.lng.toFixed(4);
        }
        this.save();
      };
    }

    if (chatLatInput) {
      chatLatInput.oninput = () => triggerDebounced("chat");
      chatLatInput.onchange = () => this.handleManualCoordChange("chat");
      chatLatInput.onkeydown = (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          this.handleManualCoordChange("chat");
        }
      };
    }

    if (chatLngInput) {
      chatLngInput.oninput = () => triggerDebounced("chat");
      chatLngInput.onchange = () => this.handleManualCoordChange("chat");
      chatLngInput.onkeydown = (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          this.handleManualCoordChange("chat");
        }
      };
    }

    if (btnApplyChatManual) {
      btnApplyChatManual.onclick = (e) => {
        e.preventDefault();
        this.handleManualCoordChange("chat");
      };
    }

    // 3. Google Maps Guide Modal Triggers
    const gmapsModal = document.getElementById("gmaps-guide-modal");
    document.querySelectorAll(".btn-open-gmaps-guide").forEach(btn => {
      btn.onclick = (e) => {
        e.preventDefault();
        if (gmapsModal) gmapsModal.classList.remove("hidden");
      };
    });

    const closeGuideBtn = document.getElementById("btn-close-gmaps-guide");
    if (closeGuideBtn && gmapsModal) {
      closeGuideBtn.onclick = () => gmapsModal.classList.add("hidden");
    }
  },

  updateUI() {
    const lat = this.coords ? this.coords.lat : null;
    const lng = this.coords ? this.coords.lng : null;
    const hasValidCoords = lat != null && lng != null && !isNaN(lat) && !isNaN(lng);
    const coordStr = hasValidCoords ? `${lat.toFixed(4)}, ${lng.toFixed(4)}` : (currentLang === "kn" ? "ಲಭ್ಯವಿಲ್ಲ" : "Not Set");
    const modeLabel = this.coords.mode === "manual"
      ? (currentLang === "kn" ? "(ಹಸ್ತಚಾಲಿತ)" : "(Manual)")
      : (currentLang === "kn" ? "(ಸ್ವಯಂಚಾಲಿತ ಜಿಪಿಎಸ್)" : "(Auto GPS)");

    // 1. Scanner Page Location Card
    const statusEl = document.getElementById("loc-status-text");
    if (statusEl) statusEl.textContent = `${coordStr} ${modeLabel}`;

    const btnGps = document.getElementById("btn-mode-gps");
    const btnManual = document.getElementById("btn-mode-manual");
    const manualInputs = document.getElementById("manual-lat-lng-container");
    const latInput = document.getElementById("input-manual-lat");
    const lngInput = document.getElementById("input-manual-lng");

    if (btnGps && btnManual) {
      if (this.coords.mode === "manual") {
        btnGps.className = "btn btn-sm btn-secondary";
        btnManual.className = "btn btn-sm btn-primary";
        if (manualInputs) manualInputs.classList.remove("hidden");
        if (latInput && document.activeElement !== latInput) {
          latInput.value = hasValidCoords ? lat.toFixed(4) : "";
        }
        if (lngInput && document.activeElement !== lngInput) {
          lngInput.value = hasValidCoords ? lng.toFixed(4) : "";
        }
      } else {
        btnGps.className = "btn btn-sm btn-primary";
        btnManual.className = "btn btn-sm btn-secondary";
        if (manualInputs) manualInputs.classList.add("hidden");
      }
    }

    // 2. Chat Page Location Card
    const chatLocEl = document.getElementById("chat-loc-badge");
    if (chatLocEl) chatLocEl.textContent = `${currentLang === "kn" ? "ಸ್ಥಳ" : "Location"}: ${coordStr} ${modeLabel}`;

    const btnChatGps = document.getElementById("btn-chat-mode-gps");
    const btnChatManual = document.getElementById("btn-chat-mode-manual");
    const chatManualInputs = document.getElementById("chat-manual-inputs");
    const chatLatInput = document.getElementById("input-chat-manual-lat");
    const chatLngInput = document.getElementById("input-chat-manual-lng");

    if (btnChatGps && btnChatManual) {
      if (this.coords.mode === "manual") {
        btnChatGps.className = "btn btn-sm btn-secondary";
        btnChatManual.className = "btn btn-sm btn-primary";
        if (chatManualInputs) chatManualInputs.classList.remove("hidden");
        if (chatLatInput && document.activeElement !== chatLatInput) {
          chatLatInput.value = hasValidCoords ? lat.toFixed(4) : "";
        }
        if (chatLngInput && document.activeElement !== chatLngInput) {
          chatLngInput.value = hasValidCoords ? lng.toFixed(4) : "";
        }
      } else {
        btnChatGps.className = "btn btn-sm btn-primary";
        btnChatManual.className = "btn btn-sm btn-secondary";
        if (chatManualInputs) chatManualInputs.classList.add("hidden");
      }
    }

    this.renderEnvironmentUI();
  }
};

window.LocationManager = LocationManager;
document.addEventListener("DOMContentLoaded", () => LocationManager.init());
