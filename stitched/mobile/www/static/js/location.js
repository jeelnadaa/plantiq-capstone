// Dual Location Manager (Auto GPS & Manual Entry & GMaps Guide)
const LocationManager = {
  coords: {
    lat: 13.3161,
    lng: 75.7720,
    mode: "gps", // 'gps' or 'manual'
    allowed: true
  },

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
    }
  },

  save() {
    localStorage.setItem("plantiq_coords", JSON.stringify(this.coords));
    this.updateUI();
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
    }
  },

  bindUI() {
    const btnGps = document.getElementById("btn-mode-gps");
    const btnManual = document.getElementById("btn-mode-manual");
    const manualInputs = document.getElementById("manual-lat-lng-container");
    const latInput = document.getElementById("input-manual-lat");
    const lngInput = document.getElementById("input-manual-lng");

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
          if (latInput) latInput.value = this.coords.lat.toFixed(4);
          if (lngInput) lngInput.value = this.coords.lng.toFixed(4);
        }
        this.save();
      };
    }

    if (latInput) {
      latInput.oninput = () => {
        const val = parseFloat(latInput.value);
        if (!isNaN(val)) {
          this.coords.lat = val;
          this.coords.mode = "manual";
          this.save();
        }
      };
    }

    if (lngInput) {
      lngInput.oninput = () => {
        const val = parseFloat(lngInput.value);
        if (!isNaN(val)) {
          this.coords.lng = val;
          this.coords.mode = "manual";
          this.save();
        }
      };
    }

    // Google Maps Guide Modal Triggers
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
    const coordStr = `${this.coords.lat.toFixed(4)}, ${this.coords.lng.toFixed(4)}`;
    const modeLabel = this.coords.mode === "manual"
      ? (currentLang === "kn" ? "(ಹಸ್ತಚಾಲಿತ)" : "(Manual)")
      : (currentLang === "kn" ? "(ಸ್ವಯಂಚಾಲಿತ ಜಿಪಿಎಸ್)" : "(Auto GPS)");

    const statusEl = document.getElementById("loc-status-text");
    if (statusEl) statusEl.textContent = `${coordStr} ${modeLabel}`;

    const chatLocEl = document.getElementById("chat-loc-badge");
    if (chatLocEl) chatLocEl.textContent = `${currentLang === "kn" ? "ಸ್ಥಳ" : "Location"}: ${coordStr} ${modeLabel}`;
  }
};

window.LocationManager = LocationManager;
document.addEventListener("DOMContentLoaded", () => LocationManager.init());
