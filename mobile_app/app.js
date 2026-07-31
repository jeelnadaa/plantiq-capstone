// PlantIQ Mobile Frontend Application Logic
// Automatically resolves to whatever IP/hostname/domain you used in your browser
const API_BASE = (typeof window !== "undefined" && window.location && window.location.protocol.startsWith("http"))
  ? window.location.origin
  : `http://${(typeof window !== "undefined" && window.location && window.location.hostname) || "localhost"}:8000`;

let currentLang = "en";
let currentSessionId = null;
let selectedScanFile = null;
let selectedChatFile = null;
let currentDiagnosisData = null;
let userCoords = { lat: 13.3161, lng: 75.7720, allowed: true }; // Default to Chikmagalur region

// DOM Elements
document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  initNavigation();
  initLocation();
  initScanner();
  initChatbot();
  initMarketplace();
  initLanguageToggle();
  initSpeech();
});

/* -------------------------------------------------------------
 * 1. Navigation & UI Tabs
 * ------------------------------------------------------------- */
function initNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  const screens = document.querySelectorAll(".app-screen");

  navItems.forEach(item => {
    item.addEventListener("click", () => {
      const targetId = item.getAttribute("data-target");

      navItems.forEach(n => n.classList.remove("active"));
      screens.forEach(s => s.classList.remove("active"));

      item.classList.add("active");
      document.getElementById(targetId).classList.add("active");

      if (targetId === "screen-market") {
        fetchMarketplaceListings();
      }
    });
  });
}

/* -------------------------------------------------------------
 * 2. Location Handling (Allowed vs Disallowed)
 * ------------------------------------------------------------- */
function initLocation() {
  const locStatusText = document.getElementById("loc-status-text");
  const gpsToggle = document.getElementById("gps-toggle");

  function requestGPS() {
    if (!gpsToggle.checked) {
      userCoords.allowed = false;
      locStatusText.textContent = "GPS Disallowed (Default Context)";
      return;
    }

    if ("geolocation" in navigator) {
      locStatusText.textContent = "Acquiring GPS location...";
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          userCoords.lat = pos.coords.latitude;
          userCoords.lng = pos.coords.longitude;
          userCoords.allowed = true;
          locStatusText.textContent = `${userCoords.lat.toFixed(4)}, ${userCoords.lng.toFixed(4)}`;
          document.getElementById("form-lat").value = userCoords.lat;
          document.getElementById("form-lng").value = userCoords.lng;
        },
        (err) => {
          console.warn("GPS Access Error:", err.message);
          userCoords.allowed = false;
          locStatusText.textContent = "Disallowed / Unavailable (Using Defaults)";
        },
        { timeout: 8000 }
      );
    } else {
      userCoords.allowed = false;
      locStatusText.textContent = "GPS Not Supported";
    }
  }

  gpsToggle.addEventListener("change", requestGPS);
  requestGPS();
}

/* -------------------------------------------------------------
 * 3. Scanner Module (CNN + RAG Advisory Pipeline)
 * ------------------------------------------------------------- */
function initScanner() {
  const uploadZone = document.getElementById("upload-zone");
  const fileInput = document.getElementById("leaf-image-input");
  const placeholder = document.getElementById("upload-placeholder");
  const previewContainer = document.getElementById("preview-container");
  const imagePreview = document.getElementById("image-preview");
  const removeBtn = document.getElementById("remove-img-btn");
  const analyzeBtn = document.getElementById("analyze-btn");

  uploadZone.addEventListener("click", (e) => {
    if (e.target !== removeBtn && !removeBtn.contains(e.target)) {
      fileInput.click();
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      selectedScanFile = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (evt) => {
        imagePreview.src = evt.target.result;
        placeholder.classList.add("hidden");
        previewContainer.classList.remove("hidden");
      };
      reader.readAsDataURL(selectedScanFile);
    }
  });

  removeBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    selectedScanFile = null;
    fileInput.value = "";
    previewContainer.classList.add("hidden");
    placeholder.classList.remove("hidden");
  });

  analyzeBtn.addEventListener("click", runLeafAnalysis);
}

async function runLeafAnalysis() {
  if (!selectedScanFile) {
    alert("Please select or capture a coffee leaf image first.");
    return;
  }

  const analyzeBtn = document.getElementById("analyze-btn");
  const resultsSection = document.getElementById("results-section");
  const questionInput = document.getElementById("scan-question-input").value;

  analyzeBtn.disabled = true;
  analyzeBtn.innerHTML = `<i data-lucide="loader" class="spin"></i> Analyzing...`;

  const formData = new FormData();
  formData.append("file", selectedScanFile);
  formData.append("language", currentLang);
  if (userCoords.allowed) {
    formData.append("latitude", userCoords.lat);
    formData.append("longitude", userCoords.lng);
  }
  if (questionInput.trim()) {
    formData.append("user_question", questionInput);
  }

  try {
    const res = await fetch(`${API_BASE}/api/predict`, {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Diagnosis request failed.");

    const data = await res.json();
    currentDiagnosisData = data;
    renderDiagnosisResults(data);
    saveToHistoryLocal(data);
  } catch (err) {
    alert("Analysis Error: " + err.message);
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = `<i data-lucide="search"></i> <span id="txt-btn-analyze">Analyze Leaf</span>`;
    lucide.createIcons();
  }
}

function renderDiagnosisResults(data) {
  const resultsSection = document.getElementById("results-section");
  resultsSection.classList.remove("hidden");
  resultsSection.scrollIntoView({ behavior: "smooth" });

  // Cache hit badge
  const cacheBadge = document.getElementById("cache-badge");
  if (data.cache_hit) {
    cacheBadge.classList.remove("hidden");
  } else {
    cacheBadge.classList.add("hidden");
  }

  // Class & Confidence
  document.getElementById("diag-class-name").textContent = data.disease;
  document.getElementById("diag-conf-value").textContent = `${data.confidence.toFixed(0)}%`;

  // Low Confidence / Blended Warning
  const blendedBox = document.getElementById("blended-warning");
  if (data.is_blended) {
    blendedBox.classList.remove("hidden");
    const reasons = data.reasons && data.reasons.length ? data.reasons.join(". ") : "Confidence below threshold.";
    document.getElementById("blended-reason-text").textContent = `${reasons} Combined RAG vector knowledge with pre-trained LLM expertise.`;
  } else {
    blendedBox.classList.add("hidden");
  }

  // Distribution Bars
  const distList = document.getElementById("dist-bars-list");
  distList.innerHTML = "";
  if (data.distribution) {
    Object.entries(data.distribution).forEach(([cls, p]) => {
      distList.innerHTML += `
        <div class="dist-bar-item">
          <div class="dist-bar-label">
            <span>${cls}</span>
            <span>${p.toFixed(1)}%</span>
          </div>
          <div class="dist-progress-bg">
            <div class="dist-progress-fill" style="width: ${p}%"></div>
          </div>
        </div>
      `;
    });
  }

  // Environmental Grid
  const envGrid = document.getElementById("env-grid-display");
  envGrid.innerHTML = "";
  if (data.env_data) {
    Object.entries(data.env_data).forEach(([k, v]) => {
      envGrid.innerHTML += `
        <div class="env-item">
          <span class="env-label">${k}</span>
          <span class="env-val">${v}</span>
        </div>
      `;
    });
  }

  // Advisory markdown
  document.getElementById("advisory-text-content").textContent = data.advisory;

  // Sources
  const sourcesList = document.getElementById("sources-list");
  sourcesList.innerHTML = "";
  if (data.sources && data.sources.length) {
    data.sources.forEach(src => {
      sourcesList.innerHTML += `<li>${src}</li>`;
    });
  }

  // Handoff to Chat button binding
  document.getElementById("handoff-chat-btn").onclick = handoffToChat;
}

async function handoffToChat() {
  if (!currentDiagnosisData) return;

  const formData = new FormData();
  formData.append("disease", currentDiagnosisData.disease);
  formData.append("confidence", currentDiagnosisData.confidence);
  formData.append("advisory", currentDiagnosisData.advisory);
  formData.append("language", currentLang);

  try {
    const res = await fetch(`${API_BASE}/api/chat/start-from-scan`, {
      method: "POST",
      body: formData
    });
    const session = await res.json();
    currentSessionId = session.session_id;

    // Switch to Chat Screen
    document.querySelector('[data-target="screen-chat"]').click();
    renderChatMessages(session.messages);
  } catch (e) {
    console.error("Handoff Error:", e);
  }
}

/* -------------------------------------------------------------
 * 4. Chatbot Module (Bilingual, Image-in-Chat, Voice)
 * ------------------------------------------------------------- */
function initChatbot() {
  const sendBtn = document.getElementById("chat-send-btn");
  const textInput = document.getElementById("chat-text-input");
  const attachBtn = document.getElementById("chat-attach-btn");
  const fileInput = document.getElementById("chat-file-input");
  const detachBtn = document.getElementById("detach-image-btn");

  attachBtn.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      selectedChatFile = e.target.files[0];
      document.getElementById("attach-label-text").textContent = `Attached: ${selectedChatFile.name}`;
      detachBtn.classList.remove("hidden");
    }
  });

  detachBtn.addEventListener("click", () => {
    selectedChatFile = null;
    fileInput.value = "";
    document.getElementById("attach-label-text").textContent = "No image selected for next question";
    detachBtn.classList.add("hidden");
  });

  sendBtn.addEventListener("click", sendChatMessage);
  textInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendChatMessage();
  });
}

async function sendChatMessage() {
  const textInput = document.getElementById("chat-text-input");
  const message = textInput.value.trim();
  if (!message && !selectedChatFile) return;

  const messagesList = document.getElementById("chat-messages-list");

  // Render user message bubble
  appendMessageBubble("user", message || "[Image attached for analysis]");
  textInput.value = "";

  const formData = new FormData();
  if (currentSessionId) formData.append("session_id", currentSessionId);
  formData.append("user_message", message || "Please review this coffee leaf image.");
  formData.append("language", currentLang);
  if (userCoords.allowed) {
    formData.append("latitude", userCoords.lat);
    formData.append("longitude", userCoords.lng);
  }
  if (selectedChatFile) {
    formData.append("image", selectedChatFile);
  }

  // Clear chat file after sending
  selectedChatFile = null;
  document.getElementById("attach-label-text").textContent = "No image selected for next question";
  document.getElementById("detach-image-btn").classList.add("hidden");

  try {
    const res = await fetch(`${API_BASE}/api/chat/message`, {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    currentSessionId = data.session_id;

    appendMessageBubble("assistant", data.reply, data.sources);
    speakText(data.reply);
  } catch (err) {
    appendMessageBubble("assistant", "Sorry, I had trouble connecting to the backend assistant.");
  }
}

function appendMessageBubble(role, text, sources = []) {
  const messagesList = document.getElementById("chat-messages-list");
  const msgDiv = document.createElement("div");
  msgDiv.className = `msg ${role}-msg`;

  const avatarDiv = document.createElement("div");
  avatarDiv.className = "avatar";
  avatarDiv.innerHTML = role === "user" ? `<i data-lucide="user"></i>` : `<i data-lucide="bot"></i>`;

  const bubbleDiv = document.createElement("div");
  bubbleDiv.className = "msg-bubble";

  let html = `<p>${text}</p>`;
  if (sources && sources.length) {
    html += `<div class="sources-box"><span class="sources-title">Sources:</span> ${sources.join(", ")}</div>`;
  }
  bubbleDiv.innerHTML = html;

  msgDiv.appendChild(avatarDiv);
  msgDiv.appendChild(bubbleDiv);
  messagesList.appendChild(msgDiv);

  lucide.createIcons();
  messagesList.scrollTop = messagesList.scrollHeight;
}

function renderChatMessages(messages) {
  const messagesList = document.getElementById("chat-messages-list");
  messagesList.innerHTML = "";
  messages.forEach(m => {
    if (m.role !== "system") {
      appendMessageBubble(m.role, m.content, m.sources);
    }
  });
}

/* -------------------------------------------------------------
 * 5. Marketplace Discovery (Crop listings & Google Maps)
 * ------------------------------------------------------------- */
function initMarketplace() {
  const modalBtn = document.getElementById("add-listing-modal-btn");
  const closeModalBtn = document.getElementById("close-modal-btn");
  const modal = document.getElementById("listing-modal");
  const form = document.getElementById("create-listing-form");

  modalBtn.addEventListener("click", () => modal.classList.remove("hidden"));
  closeModalBtn.addEventListener("click", () => modal.classList.add("hidden"));

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);

    try {
      const res = await fetch(`${API_BASE}/api/marketplace/listings`, {
        method: "POST",
        body: formData
      });
      if (res.ok) {
        modal.classList.add("hidden");
        form.reset();
        fetchMarketplaceListings();
      }
    } catch (err) {
      alert("Failed to publish listing: " + err.message);
    }
  });
}

async function fetchMarketplaceListings() {
  const feed = document.getElementById("marketplace-feed");
  feed.innerHTML = "<p class='empty-state'>Loading listings...</p>";

  try {
    const res = await fetch(`${API_BASE}/api/marketplace/listings`);
    const listings = await res.json();

    feed.innerHTML = "";
    if (!listings || !listings.length) {
      feed.innerHTML = "<p class='empty-state'>No crop listings currently available.</p>";
      return;
    }

    listings.forEach(item => {
      const card = document.createElement("div");
      card.className = "market-card";
      card.innerHTML = `
        <div class="market-card-body">
          <div class="market-title-row">
            <h3 class="market-title">${item.crop_name}</h3>
            <span class="market-price">₹${item.price_per_kg}/kg</span>
          </div>
          <p class="market-meta">Variety: <strong>${item.variety}</strong> | Quantity: <strong>${item.quantity_kg} kg</strong></p>
          <div class="market-location">
            <i data-lucide="map-pin" class="pin-icon"></i>
            <span>${item.address} (${item.farmer_name} • ${item.contact_phone})</span>
          </div>
          ${item.description ? `<p class="market-meta">${item.description}</p>` : ''}
          <div style="margin-top: 10px;">
            <a href="${item.google_maps_url}" target="_blank" rel="noopener" class="btn-gmaps">
              <i data-lucide="navigation"></i> View on Google Maps
            </a>
          </div>
        </div>
      `;
      feed.appendChild(card);
    });
    lucide.createIcons();
  } catch (err) {
    feed.innerHTML = "<p class='empty-state'>Error loading marketplace listings.</p>";
  }
}

/* -------------------------------------------------------------
 * 6. History Local Cache View
 * ------------------------------------------------------------- */
function saveToHistoryLocal(item) {
  let history = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  history.unshift(item);
  if (history.length > 10) history.pop();
  localStorage.setItem("plantiq_history", JSON.stringify(history));
  renderHistoryFeed();
}

function renderHistoryFeed() {
  const feed = document.getElementById("history-feed");
  let history = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  if (!history.length) {
    feed.innerHTML = "<p class='empty-state'>No recent scan history found.</p>";
    return;
  }

  feed.innerHTML = "";
  history.forEach(item => {
    const div = document.createElement("div");
    div.className = "history-item";
    div.innerHTML = `
      <div>
        <h4>${item.disease} (${item.confidence.toFixed(0)}%)</h4>
        <span>SHA-256: ${item.sha256_hash ? item.sha256_hash.substring(0, 12) : 'Cached'}</span>
      </div>
      <button class="btn btn-sm btn-secondary">View</button>
    `;
    div.querySelector("button").onclick = () => renderDiagnosisResults(item);
    feed.appendChild(div);
  });
}

/* -------------------------------------------------------------
 * 7. Language Toggle (English <-> Kannada) & Voice STT/TTS
 * ------------------------------------------------------------- */
function initLanguageToggle() {
  const langBtn = document.getElementById("lang-btn");
  const langLabel = document.getElementById("current-lang-label");

  langBtn.addEventListener("click", () => {
    currentLang = currentLang === "en" ? "kn" : "en";
    langLabel.textContent = currentLang.toUpperCase();
    updateLanguageUI();
  });
}

function updateLanguageUI() {
  if (currentLang === "kn") {
    document.getElementById("tagline-text").textContent = "ಕಾಫಿ ಬೆಳೆ ಎಐ ಮತ್ತು ಮಾರುಕಟ್ಟೆ";
    document.getElementById("txt-scan-title").textContent = "ಕಾಫಿ ಎಲೆ ರೋಗ ನಿರ್ಣಯ";
    document.getElementById("txt-btn-analyze").textContent = "ಎಲೆ ವಿಶ್ಲೇಷಿಸಿ";
    document.getElementById("txt-chat-title").textContent = "ಕೃಷಿ ಎಐ ಸಹಾಯಕ";
    document.getElementById("txt-market-title").textContent = "ಕಾಫಿ ಮಾರುಕಟ್ಟೆ";
  } else {
    document.getElementById("tagline-text").textContent = "Coffee Crop AI & Marketplace";
    document.getElementById("txt-scan-title").textContent = "Coffee Leaf Disease Diagnostic";
    document.getElementById("txt-btn-analyze").textContent = "Analyze Leaf";
    document.getElementById("txt-chat-title").textContent = "Agri Chatbot Assistant";
    document.getElementById("txt-market-title").textContent = "Coffee Crop Marketplace";
  }
}

function initSpeech() {
  const micBtn = document.getElementById("voice-mic-btn");
  const textInput = document.getElementById("chat-text-input");

  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    micBtn.style.display = "none";
    return;
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();

  recognition.continuous = false;
  recognition.interimResults = false;

  micBtn.addEventListener("click", () => {
    recognition.lang = currentLang === "kn" ? "kn-IN" : "en-US";
    micBtn.classList.add("recording");
    recognition.start();
  });

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    textInput.value = transcript;
    micBtn.classList.remove("recording");
  };

  recognition.onerror = () => {
    micBtn.classList.remove("recording");
  };

  recognition.onend = () => {
    micBtn.classList.remove("recording");
  };
}

function speakText(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel(); // Stop current speech
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = currentLang === "kn" ? "kn-IN" : "en-US";
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
  }
}
