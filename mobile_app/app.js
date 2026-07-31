// PlantIQ Mobile Frontend Application Logic
// Automatically resolves to whatever IP/hostname/domain you used in your browser
const API_BASE = (typeof window !== "undefined" && window.location && window.location.protocol.startsWith("http"))
  ? window.location.origin
  : `http://${(typeof window !== "undefined" && window.location && window.location.hostname) || "localhost"}:8000`;

let currentLang = "en";
let currentSessionId = null;
let selectedScanFile = null;
let selectedChatFile = null;
let attachedScanContext = null; // Holds selected scanner or history scan object
let currentDiagnosisData = null;
let activePreviewItem = null;
let undoTimer = null;
let userCoords = { lat: 13.3161, lng: 75.7720, allowed: true }; // Default to Chikmagalur region

// Complete i18n Translation Dictionary
const I18N = {
  en: {
    taglineText: "Coffee Crop AI & Marketplace",
    scanTitle: "Coffee Leaf Disease Diagnostic",
    scanSub: "Upload or capture a leaf photo to diagnose diseases and receive tailored treatment advisories.",
    uploadBold: "Tap to Take Photo",
    uploadOr: " or Upload Image",
    fileHint: "Supports JPEG, PNG coffee leaf photos",
    locTitle: "Location Factors",
    lblQuestion: "Specific Question (Optional)",
    scanQuestionPlaceholder: "e.g., Which fungicide is safe near a stream?",
    btnAnalyze: "Analyze Leaf",
    cacheHit: "Instant Hash Cache Match (Pipeline Skipped)",
    healthyBadge: "Diagnostic Output",
    confLbl: "Confidence",
    blendedTitle: "Blended Advisory (Low Certainty Caution)",
    distTitle: "Class Probabilities",
    envTitle: "Environmental Conditions at Site",
    advisoryTitle: "Recommended Agronomic Solution",
    sourcesTitle: "Knowledge Sources:",
    btnHandoff: "Ask Follow-Up in Chat",
    btnClearScan: "Clear Results & New Scan",
    chatTitle: "Agri Chatbot Assistant",
    chatSub: "Chat freely in English or Kannada. Speak via voice mic or attach photos for review.",
    chatWelcome: "Hello! I am your PlantIQ agronomy assistant. Ask me questions about coffee diseases, fertilizers, or pest management in English or Kannada!",
    noImageSelected: "No image selected for next question",
    attachedImage: "Attached: ",
    detachLbl: "Remove",
    btnSelectImg: "Select Image",
    pickerModalTitle: "Select Image for Chat Context",
    optNewTitle: "Upload / Capture New Image",
    optNewSub: "Take a photo or choose from device gallery",
    pickerHistoryHead: "Past Scanned Images (History)",
    optClearLbl: "Clear Selection (No Image)",
    previewModalTitle: "Leaf Image Preview",
    detailsModalTitle: "Complete Diagnostic Report",
    btnMoreDetails: "More Details",
    btnClosePreview: "Close",
    btnClearHistory: "Clear All",
    confirmTitle: "Clear All Scan History?",
    confirmMsg: "Are you sure you want to permanently delete all saved leaf scan history? This action cannot be undone.",
    confirmCancel: "Cancel",
    confirmOk: "Delete All",
    toastSingleDeleted: "Scan deleted & backend cache cleared",
    toastAllCleared: "All scan history & cache cleared",
    btnUndo: "Undo",
    chatPlaceholder: "Type a message or use mic...",
    marketTitle: "Coffee Crop Marketplace",
    marketSub: "Browse listings from local coffee farmers with 1-tap Google Maps navigation.",
    btnSell: "Sell Crop",
    marketSearchPlaceholder: "Search Arabica, Robusta, Location...",
    viewGmaps: "View on Google Maps",
    historyTitle: "Deduplicated Scans History",
    historySub: "Quickly review past coffee leaf disease scans saved in your local image cache.",
    historyEmpty: "No recent scan history found.",
    navScanner: "Scanner",
    navChat: "Chatbot",
    navMarket: "Market",
    navHistory: "History",
    modalTitle: "List Coffee Crop for Sale",
    cropTitle: "Crop Title",
    variety: "Variety",
    quantity: "Quantity (Kg)",
    price: "Price per Kg (₹)",
    farmer: "Farmer Name",
    phone: "Phone / WhatsApp",
    address: "Address / Estate Location",
    latitude: "Latitude (Optional)",
    longitude: "Longitude (Optional)",
    btnFetchGps: "Use Current GPS Location",
    guideTitle: "How to get location coordinates:",
    guideBody: '1. Tap <strong>"Use Current GPS Location"</strong> above, OR<br>2. Open Google Maps, press & hold your estate pin, and copy the numbers.<br><em>(If left blank, address/pincode will auto-convert automatically)</em>',
    btnPublish: "Publish Listing"
  },
  kn: {
    taglineText: "ಕಾಫಿ ಬೆಳೆ ಎಐ ಮತ್ತು ಮಾರುಕಟ್ಟೆ",
    scanTitle: "ಕಾಫಿ ಎಲೆ ರೋಗ ನಿರ್ಣಯ",
    scanSub: "ಕಾಫಿ ಎಲೆ ರೋಗಗಳನ್ನು ಪತ್ತೆಹಚ್ಚಲು ಮತ್ತು ಸೂಕ್ತ ಚಿಕಿತ್ಸಾ ಸಲಹೆಗಳನ್ನು ಪಡೆಯಲು ಎಲೆಯ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಸೆರೆಹಿಡಿಯಿರಿ.",
    uploadBold: "ಫೋಟೋ ತೆಗೆಯಲು ಟ್ಯಾಪ್ ಮಾಡಿ",
    uploadOr: " ಅಥವಾ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
    fileHint: "JPEG, PNG ಕಾಫಿ ಎಲೆ ಫೋಟೋಗಳನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ",
    locTitle: "ಸ್ಥಳೀಯ ವಾತಾವರಣ ವಿವರಗಳು",
    lblQuestion: "ನಿರ್ದಿಷ್ಟ ಪ್ರಶ್ನೆ (ಐಚ್ಛಿಕ)",
    scanQuestionPlaceholder: "ಉದಾ: ಹಳ್ಳದ ಬಳಿ ಯಾವ ಶಿಲೀಂಧ್ರನಾಶಕ ಸುರಕ್ಷಿತ?",
    btnAnalyze: "ಎಲೆ ವಿಶ್ಲೇಷಿಸಿ",
    cacheHit: "ತತ್ಕ್ಷಣದ ಕ್ಯಾಶ್ ಪಂದ್ಯ (ಪುನರಾವರ್ತಿತ ವಿಶ್ಲೇಷಣೆ ತಡೆಗಟ್ಟಲಾಗಿದೆ)",
    healthyBadge: "ರೋಗ ನಿರ್ಣಯ ಫಲಿತಾಂಶ",
    confLbl: "ನಂಬಿಕೆಯ ಶೇಕಡಾ",
    blendedTitle: "ಸಂಯೋಜಿತ ಸಲಹೆ (ಎಚ್ಚರಿಕೆಯ ಸೂಚನೆ)",
    distTitle: "ರೋಗ ಸಂಭಾವ್ಯತೆಗಳು",
    envTitle: "ಸ್ಥಳದ ವಾತಾವರಣದ ಸ್ಥಿತಿ",
    advisoryTitle: "ಶಿಫಾರಸು ಮಾಡಿದ ಕೃಷಿ ಪರಿಹಾರ",
    sourcesTitle: "ಜ್ಞಾನದ ಆಕರಗಳು:",
    btnHandoff: "ಚಾಟ್‌ನಲ್ಲಿ ಮತ್ತಷ್ಟು ವಿಚಾರಿಸಿ",
    btnClearScan: "ಫಲಿತಾಂಶ ಅಳಿಸಿ & ಹೊಸ ಸ್ಕ್ಯಾನ್",
    chatTitle: "ಕೃಷಿ ಚಾಟ್‌ಬಾಟ್ ಸಹಾಯಕ",
    chatSub: "ಇಂಗ್ಲಿಷ್ ಅಥವಾ ಕನ್ನಡದಲ್ಲಿ ಮುಕ್ತವಾಗಿ ಚಾಟ್ ಮಾಡಿ. ಮೈಕ್ ಮೂಲಕ ಮಾತನಾಡಿ ಅಥವಾ ಫೋಟೋ ಲಗತ್ತಿಸಿ.",
    chatWelcome: "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ PlantIQ ಕೃಷಿ ಸಹಾಯಕ. ಕಾಫಿ ರೋಗಗಳು, ಗೊಬ್ಬರಗಳು ಅಥವಾ ಕೀಟ ನಿರ್ವಹಣೆಯ ಬಗ್ಗೆ ಕನ್ನಡ ಅಥವಾ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ಉಚಿತವಾಗಿ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಿ!",
    noImageSelected: "ಮುಂದಿನ ಪ್ರಶ್ನೆಗೆ ಯಾವುದೇ ಚಿತ್ರ ಆಯ್ಕೆಯಾಗಿಲ್ಲ",
    attachedImage: "ಲಗತ್ತಿಸಲಾಗಿದೆ: ",
    detachLbl: "ತೆಗೆದುಹಾಕಿ",
    btnSelectImg: "ಚಿತ್ರ ಆಯ್ಕೆಮಾಡಿ",
    pickerModalTitle: "ಚಾಟ್‌ಗಾಗಿ ಚಿತ್ರ ಆಯ್ಕೆಮಾಡಿ",
    optNewTitle: "ಹೊಸ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
    optNewSub: "ಕ್ಯಾಮೆರಾ ಅಥವಾ ಗ್ಯಾಲರಿಯಿಂದ ಫೋಟೋ ಆಯ್ಕೆಮಾಡಿ",
    pickerHistoryHead: "ಹಿಂದಿನ ಪರಿಶೋಧನೆಗಳ ಚಿತ್ರಗಳು",
    optClearLbl: "ಆಯ್ಕೆ ರದ್ದುಗೊಳಿಸಿ (ಚಿತ್ರವಿಲ್ಲ)",
    previewModalTitle: "ಎಲೆಯ ಫೋಟೋ ಪೂರ್ವವೀಕ್ಷಣೆ",
    detailsModalTitle: "ಸಂಪೂರ್ಣ ರೋಗ ನಿರ್ಣಯ ವರದಿ",
    btnMoreDetails: "ಹೆಚ್ಚಿನ ವಿವರಗಳು",
    btnClosePreview: "ಮುಚ್ಚಿ",
    btnClearHistory: "ಎಲ್ಲಾ ಅಳಿಸಿ",
    confirmTitle: "ಎಲ್ಲಾ ರೋಗ ಪರಿಶೋಧನೆಗಳನ್ನು ಅಳಿಸಬೇಕೇ?",
    confirmMsg: "ನಿಮ್ಮ ಎಲ್ಲಾ ಉಳಿಸಲಾದ ಇತಿಹಾಸವನ್ನು ಶಾಶ್ವತವಾಗಿ ಅಳಿಸಲು ನೀವು ಖಚಿತವಾಗಿದ್ದೀರಾ? ಇದನ್ನು ಹಿಂತಿರುಗಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ.",
    confirmCancel: "ರದ್ದುಗೊಳಿಸಿ",
    confirmOk: "ಎಲ್ಲಾ ಅಳಿಸಿ",
    toastSingleDeleted: "ರೋಗ ಪರಿಶೋಧನೆ & ಕ್ಯಾಶ್ ಅಳಿಸಲಾಗಿದೆ",
    toastAllCleared: "ಎಲ್ಲಾ ಇತಿಹಾಸ & ಕ್ಯಾಶ್ ಅಳಿಸಲಾಗಿದೆ",
    btnUndo: "ಹಿಂಪಡೆಯಿರಿ",
    chatPlaceholder: "ಸಂದೇಶ ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ಮೈಕ್ ಬಳಸಿ...",
    marketTitle: "ಕಾಫಿ ಬೆಳೆ ಮಾರುಕಟ್ಟೆ",
    marketSub: "ಸ್ಥಳೀಯ ಕಾಫಿ ಬೆಳೆಗಾರರ ಮಾರಾಟ ವಿವರಗಳನ್ನು ನೋಡಿ ಮತ್ತು ಗೂಗಲ್ ಮ್ಯಾಪ್ಸ್ ಮೂಲಕ ಸಂಪರ್ಕಿಸಿ.",
    btnSell: "ಬೆಳೆ ಮಾರಾಟ ಮಾಡಿ",
    marketSearchPlaceholder: "ಅರಾಬಿಕಾ, ರೊಬಸ್ಟಾ, ಸ್ಥಳ ಹುಡುಕಿ...",
    viewGmaps: "ಗೂಗಲ್ ಮ್ಯಾಪ್ಸ್‌ನಲ್ಲಿ ನೋಡಿ",
    historyTitle: "ಹಿಂದಿನ ಪರಿಶೋಧನೆಗಳ ಇತಿಹಾಸ",
    historySub: "ನಿಮ್ಮ ಕ್ಯಾಶ್‌ನಲ್ಲಿ ಉಳಿಸಲಾದ ಇತ್ತೀಚಿನ ಎಲೆ ರೋಗ ಪರಿಶೋಧನೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
    historyEmpty: "ಯಾವುದೇ ಇತ್ತೀಚಿನ ರೋಗ ನಿರ್ಣಯಗಳು ಕಂಡುಬಂದಿಲ್ಲ.",
    navScanner: "ಸ್ಕಾನರ್",
    navChat: "ಚಾಟ್‌ಬಾಟ್",
    navMarket: "ಮಾರುಕಟ್ಟೆ",
    navHistory: "ಇತಿಹಾಸ",
    modalTitle: "ಮಾರಾಟಕ್ಕಾಗಿ ಕಾಫಿ ಬೆಳೆ ನೋಂದಾಯಿಸಿ",
    cropTitle: "ಬೆಳೆಯ ಶೀರ್ಷಿಕೆ",
    variety: "ತಳಿ",
    quantity: "ಪ್ರಮಾಣ (ಕೆಜಿ)",
    price: "ದರ ಪ್ರತಿ ಕೆಜಿಗೆ (₹)",
    farmer: "ರೈತರ ಹೆಸರು",
    phone: "ಫೋನ್ / ವಾಟ್ಸಾಪ್",
    address: "ವಿಳಾಸ / ಎಸ್ಟೇಟ್ ಸ್ಥಳ",
    latitude: "ಅಕ್ಷಾಂಶ (ಐಚ್ಛಿಕ)",
    longitude: "ರೇಖಾಂಶ (ಐಚ್ಛಿಕ)",
    btnFetchGps: "ಸ್ಥಳೀಯ ಜಿಪಿಎಸ್ ಬಳಸಿ",
    guideTitle: "ಅಕ್ಷಾಂಶ ಮತ್ತು ರೇಖಾಂಶ ಪಡೆಯುವುದು ಹೇಗೆ:",
    guideBody: '1. ಮೇಲಿರುವ <strong>"ಸ್ಥಳೀಯ ಜಿಪಿಎಸ್ ಬಳಸಿ"</strong> ಬಟನ್ ಟ್ಯಾಪ್ ಮಾಡಿ, ಅಥವಾ<br>2. ಮೊಬೈಲ್‌ನ ಗೂಗಲ್ ಮ್ಯಾಪ್ಸ್ ತೆರೆದು ಎಸ್ಟೇಟ್ ಜಾಗವನ್ನು ಒತ್ತಿ ಹಿಡಿದು ಸಂಖ್ಯೆಗಳನ್ನು ಕಾಪಿ ಮಾಡಿ.<br><em>(ಖಾಲಿ ಬಿಟ್ಟರೆ ನಿಮ್ಮ ವಿಳಾಸದಿಂದ ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಜಿಪಿಎಸ್ ಪಡೆಯಲಾಗುತ್ತದೆ)</em>',
    btnPublish: "ಪ್ರಕಟಿಸಿ"
  }
};

const DISEASE_NAMES_MAP = {
  "Coffee Leaf Rust": { en: "Coffee Leaf Rust", kn: "ಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗ (Coffee Leaf Rust)" },
  "Rust": { en: "Coffee Leaf Rust", kn: "ಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗ (Coffee Leaf Rust)" },
  "Coffee Leaf Miner": { en: "Coffee Leaf Miner", kn: "ಕಾಫಿ ಎಲೆ ಸುರಂಗ ಹುಳು ರೋಗ (Coffee Leaf Miner)" },
  "Miner": { en: "Coffee Leaf Miner", kn: "ಕಾಫಿ ಎಲೆ ಸುರಂಗ ಹುಳು ರೋಗ (Coffee Leaf Miner)" },
  "Phoma": { en: "Phoma Blight", kn: "ಫೋಮಾ ಚುಕ್ಕೆ ರೋಗ (Phoma)" },
  "Cerscospora": { en: "Cercospora Leaf Spot", kn: "ಸರ್ಕೋಸ್ಪೊರಾ ಕಪ್ಪು ಚುಕ್ಕೆ ರೋಗ (Cercospora)" },
  "Healthy": { en: "Healthy Leaf", kn: "ಆರೋಗ್ಯಕರ ಎಲೆ (Healthy)" }
};

// DOM Elements
document.addEventListener("DOMContentLoaded", () => {
  lucide.createIcons();
  initNavigation();
  initLocation();
  initScanner();
  initChatbot();
  initImagePickerModal();
  initModalsAndPreviews();
  initHistorySection();
  initMarketplace();
  initLanguageToggle();
  initSpeech();
  updateLanguageUI();
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
      locStatusText.textContent = currentLang === "kn" ? "ಜಿಪಿಎಸ್ ನಿಷ್ಕ್ರಿಯವಾಗಿದೆ (ಸಾಮಾನ್ಯ ವಿವರ)" : "GPS Disallowed (Default Context)";
      return;
    }

    if ("geolocation" in navigator) {
      locStatusText.textContent = currentLang === "kn" ? "ಜಿಪಿಎಸ್ ಪಡೆಯಲಾಗುತ್ತಿದೆ..." : "Acquiring GPS location...";
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          userCoords.lat = pos.coords.latitude;
          userCoords.lng = pos.coords.longitude;
          userCoords.allowed = true;
          locStatusText.textContent = `${userCoords.lat.toFixed(4)}, ${userCoords.lng.toFixed(4)}`;
          const formLat = document.getElementById("form-lat");
          const formLng = document.getElementById("form-lng");
          if (formLat && !formLat.value) formLat.value = userCoords.lat.toFixed(4);
          if (formLng && !formLng.value) formLng.value = userCoords.lng.toFixed(4);
        },
        (err) => {
          console.warn("GPS Access Error:", err.message);
          userCoords.allowed = false;
          locStatusText.textContent = currentLang === "kn" ? "ನಿಷ್ಕ್ರಿಯವಾಗಿದೆ (ಸಾಮಾನ್ಯ ವಿವರ)" : "Disallowed / Unavailable (Using Defaults)";
        },
        { timeout: 8000 }
      );
    } else {
      userCoords.allowed = false;
      locStatusText.textContent = currentLang === "kn" ? "ಜಿಪಿಎಸ್ ಬೆಂಬಲಿತವಾಗಿಲ್ಲ" : "GPS Not Supported";
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
  const clearScanBtn = document.getElementById("clear-scan-btn");

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
  if (clearScanBtn) {
    clearScanBtn.addEventListener("click", clearScannerResults);
  }
}

function clearScannerResults() {
  const resultsSection = document.getElementById("results-section");
  const placeholder = document.getElementById("upload-placeholder");
  const previewContainer = document.getElementById("preview-container");
  const fileInput = document.getElementById("leaf-image-input");
  const questionInput = document.getElementById("scan-question-input");

  // 1. Hide results
  if (resultsSection) resultsSection.classList.add("hidden");

  // 2. Reset upload inputs & file state
  selectedScanFile = null;
  currentDiagnosisData = null;
  if (fileInput) fileInput.value = "";
  if (questionInput) questionInput.value = "";

  // 3. Reset image preview
  if (previewContainer) previewContainer.classList.add("hidden");
  if (placeholder) placeholder.classList.remove("hidden");

  // 4. Scroll smoothly to top of scanner screen
  const scannerScreen = document.getElementById("screen-scanner");
  if (scannerScreen) scannerScreen.scrollIntoView({ behavior: "smooth" });
}

async function runLeafAnalysis() {
  if (!selectedScanFile) {
    alert(currentLang === "kn" ? "ದಯವಿಟ್ಟು ಮೊದಲಿಗೆ ಕಾಫಿ ಎಲೆಯ ಫೋಟೋ ಆಯ್ಕೆಮಾಡಿ ಅಥವಾ ಸೆರೆಹಿಡಿಯಿರಿ." : "Please select or capture a coffee leaf image first.");
    return;
  }

  const analyzeBtn = document.getElementById("analyze-btn");
  const questionInput = document.getElementById("scan-question-input").value;

  analyzeBtn.disabled = true;
  analyzeBtn.innerHTML = `<i data-lucide="loader" class="spin"></i> ${currentLang === "kn" ? "ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ..." : "Analyzing..."}`;

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

    // Save with image Data URL & timestamp
    const now = new Date();
    const formattedTime = now.toLocaleString(currentLang === "kn" ? "kn-IN" : "en-US", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });

    if (selectedScanFile) {
      const reader = new FileReader();
      reader.onload = (evt) => {
        data.image_data_url = evt.target.result;
        data.timestamp = formattedTime;
        saveToHistoryLocal(data);
      };
      reader.readAsDataURL(selectedScanFile);
    } else {
      data.timestamp = formattedTime;
      saveToHistoryLocal(data);
    }

  } catch (err) {
    alert("Analysis Error: " + err.message);
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = `<i data-lucide="search"></i> <span id="txt-btn-analyze">${I18N[currentLang].btnAnalyze}</span>`;
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

  // Class & Confidence (Translate class if Kannada)
  const mappedDisease = DISEASE_NAMES_MAP[data.disease] ? DISEASE_NAMES_MAP[data.disease][currentLang] : data.disease;
  document.getElementById("diag-class-name").textContent = mappedDisease;
  document.getElementById("diag-conf-value").textContent = `${data.confidence.toFixed(0)}%`;

  // Low Confidence / Blended Warning
  const blendedBox = document.getElementById("blended-warning");
  if (data.is_blended) {
    blendedBox.classList.remove("hidden");
    const reasons = data.reasons && data.reasons.length ? data.reasons.join(". ") : "Confidence below threshold.";
    document.getElementById("blended-reason-text").textContent = currentLang === "kn"
      ? `${reasons} ಜ್ಞಾನ ಭಂಡಾರ ಮತ್ತು ಜನರಲ್ ಎಐ ಸಂಯೋಜಿತ ಸಲಹೆ.`
      : `${reasons} Combined RAG vector knowledge with pre-trained LLM expertise.`;
  } else {
    blendedBox.classList.add("hidden");
  }

  // Distribution Bars
  const distList = document.getElementById("dist-bars-list");
  distList.innerHTML = "";
  if (data.distribution) {
    Object.entries(data.distribution).forEach(([cls, p]) => {
      const clsName = DISEASE_NAMES_MAP[cls] ? DISEASE_NAMES_MAP[cls][currentLang] : cls;
      distList.innerHTML += `
        <div class="dist-bar-item">
          <div class="dist-bar-label">
            <span>${clsName}</span>
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

    // Set attached scan context
    attachedScanContext = currentDiagnosisData;
    updateAttachedImageBarUI();

    // Switch to Chat Screen
    document.querySelector('[data-target="screen-chat"]').click();
    renderChatMessages(session.messages);
  } catch (e) {
    console.error("Handoff Error:", e);
  }
}

/* -------------------------------------------------------------
 * 4. Chatbot Module & Image Picker Modal
 * ------------------------------------------------------------- */
function initChatbot() {
  const sendBtn = document.getElementById("chat-send-btn");
  const textInput = document.getElementById("chat-text-input");
  const attachBtn = document.getElementById("chat-attach-btn");
  const fileInput = document.getElementById("chat-file-input");
  const detachBtn = document.getElementById("detach-image-btn");

  attachBtn.addEventListener("click", () => document.getElementById("open-picker-btn").click());

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      selectedChatFile = e.target.files[0];
      attachedScanContext = null;
      updateAttachedImageBarUI();
    }
  });

  detachBtn.addEventListener("click", () => {
    selectedChatFile = null;
    attachedScanContext = null;
    fileInput.value = "";
    updateAttachedImageBarUI();
  });

  sendBtn.addEventListener("click", sendChatMessage);
  textInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendChatMessage();
  });
}

function initImagePickerModal() {
  const openPickerBtn = document.getElementById("open-picker-btn");
  const closePickerBtn = document.getElementById("close-picker-modal-btn");
  const pickerModal = document.getElementById("image-picker-modal");
  const optUploadNewBtn = document.getElementById("opt-upload-new-btn");
  const optClearImgBtn = document.getElementById("opt-clear-img-btn");

  openPickerBtn.addEventListener("click", () => {
    renderPickerOptions();
    pickerModal.classList.remove("hidden");
  });

  closePickerBtn.addEventListener("click", () => pickerModal.classList.add("hidden"));

  optUploadNewBtn.addEventListener("click", () => {
    pickerModal.classList.add("hidden");
    document.getElementById("chat-file-input").click();
  });

  optClearImgBtn.addEventListener("click", () => {
    selectedChatFile = null;
    attachedScanContext = null;
    document.getElementById("chat-file-input").value = "";
    updateAttachedImageBarUI();
    pickerModal.classList.add("hidden");
  });
}

function renderPickerOptions() {
  const historyContainer = document.getElementById("opt-history-container");
  const pickerModal = document.getElementById("image-picker-modal");

  historyContainer.innerHTML = "";
  let history = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  if (!history || !history.length) {
    historyContainer.innerHTML = `<p style="font-size: 0.75rem; color: #94a3b8;">${I18N[currentLang].historyEmpty}</p>`;
  } else {
    history.forEach((item, idx) => {
      const diseaseName = DISEASE_NAMES_MAP[item.disease] ? DISEASE_NAMES_MAP[item.disease][currentLang] : item.disease;
      const thumbHtml = item.image_data_url 
        ? `<img src="${item.image_data_url}" style="width:40px; height:40px; border-radius:6px; object-fit:cover;">`
        : `<i data-lucide="clock" class="opt-icon"></i>`;
      const timeStr = item.timestamp || `Scan #${idx+1}`;

      const historyOptDiv = document.createElement("div");
      historyOptDiv.className = "picker-option-btn";
      historyOptDiv.style.justifyContent = "space-between";
      historyOptDiv.innerHTML = `
        <div style="display:flex; align-items:center; gap:10px;">
          ${thumbHtml}
          <div>
            <strong>${diseaseName} (${item.confidence.toFixed(0)}%)</strong>
            <span>📅 ${timeStr}</span>
          </div>
        </div>
        <div style="display:flex; gap:6px;">
          <button class="btn btn-sm btn-secondary view-opt-btn">${currentLang === "kn" ? "ನೋಡಿ" : "View"}</button>
          <button class="btn btn-sm btn-primary select-opt-btn">${currentLang === "kn" ? "ಆಯ್ಕೆ" : "Select"}</button>
        </div>
      `;

      // View button in Chat Picker
      historyOptDiv.querySelector(".view-opt-btn").onclick = (evt) => {
        evt.stopPropagation();
        openImagePreviewModal(item);
      };

      // Select button in Chat Picker
      historyOptDiv.querySelector(".select-opt-btn").onclick = () => {
        attachedScanContext = item;
        selectedChatFile = null;
        updateAttachedImageBarUI();
        pickerModal.classList.add("hidden");
      };

      historyContainer.appendChild(historyOptDiv);
    });
  }
  lucide.createIcons();
}

function updateAttachedImageBarUI() {
  const labelText = document.getElementById("attach-label-text");
  const detachBtn = document.getElementById("detach-image-btn");

  if (selectedChatFile) {
    labelText.textContent = `${I18N[currentLang].attachedImage} New Upload (${selectedChatFile.name})`;
    detachBtn.classList.remove("hidden");
  } else if (attachedScanContext) {
    const diseaseName = DISEASE_NAMES_MAP[attachedScanContext.disease] ? DISEASE_NAMES_MAP[attachedScanContext.disease][currentLang] : attachedScanContext.disease;
    labelText.textContent = `${I18N[currentLang].attachedImage} ${diseaseName} (${attachedScanContext.confidence.toFixed(0)}%)`;
    detachBtn.classList.remove("hidden");
  } else {
    labelText.textContent = I18N[currentLang].noImageSelected;
    detachBtn.classList.add("hidden");
  }
}

async function sendChatMessage() {
  const textInput = document.getElementById("chat-text-input");
  const message = textInput.value.trim();
  if (!message && !selectedChatFile && !attachedScanContext) return;

  let displayMsg = message;
  if (!displayMsg) {
    if (selectedChatFile) displayMsg = currentLang === "kn" ? "[ವಿಶ್ಲೇಷಣೆಗಾಗಿ ಫೋಟೋ ಲಗತ್ತಿಸಲಾಗಿದೆ]" : "[Image attached for analysis]";
    else if (attachedScanContext) displayMsg = `${currentLang === "kn" ? "[ರೋಗ ಪರಿಶೋಧನೆ ಲಗತ್ತಿಸಲಾಗಿದೆ: " : "[Scan context attached: "}${attachedScanContext.disease}]`;
  }

  // Render user message bubble
  appendMessageBubble("user", displayMsg);
  textInput.value = "";

  const formData = new FormData();
  if (currentSessionId) formData.append("session_id", currentSessionId);
  formData.append("user_message", message || "Please review this attached coffee leaf image context.");
  formData.append("language", currentLang);
  if (userCoords.allowed) {
    formData.append("latitude", userCoords.lat);
    formData.append("longitude", userCoords.lng);
  }

  if (selectedChatFile) {
    formData.append("image", selectedChatFile);
  } else if (attachedScanContext) {
    formData.append("user_message", `[Context: ${attachedScanContext.disease} (${attachedScanContext.confidence}% confidence)] ` + (message || "Please provide treatment details."));
  }

  // Clear chat image selection after sending
  selectedChatFile = null;
  attachedScanContext = null;
  updateAttachedImageBarUI();

  try {
    const res = await fetch(`${API_BASE}/api/chat/message`, {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    currentSessionId = data.session_id;

    appendMessageBubble("assistant", data.reply, data.sources);
  } catch (err) {
    appendMessageBubble("assistant", currentLang === "kn" ? "ಕ್ಷಮಿಸಿ, ಸಹಾಯಕನಿಗೆ ಸಂಪರ್ಕಿಸಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ." : "Sorry, I had trouble connecting to the backend assistant.");
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
    html += `<div class="sources-box"><span class="sources-title">${I18N[currentLang].sourcesTitle}</span> ${sources.join(", ")}</div>`;
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
 * 5. Modals & Image Preview Popups
 * ------------------------------------------------------------- */
function initModalsAndPreviews() {
  const previewModal = document.getElementById("scan-preview-modal");
  const detailsModal = document.getElementById("scan-details-modal");
  const closePreviewBtn = document.getElementById("close-preview-modal-btn");
  const closePreviewBtn2 = document.getElementById("close-preview-modal-btn-2");
  const closeDetailsBtn = document.getElementById("close-details-modal-btn");
  const btnMoreDetails = document.getElementById("btn-preview-more-details");

  if (closePreviewBtn) closePreviewBtn.addEventListener("click", () => previewModal.classList.add("hidden"));
  if (closePreviewBtn2) closePreviewBtn2.addEventListener("click", () => previewModal.classList.add("hidden"));
  if (closeDetailsBtn) closeDetailsBtn.addEventListener("click", () => detailsModal.classList.add("hidden"));

  if (btnMoreDetails) {
    btnMoreDetails.addEventListener("click", () => {
      previewModal.classList.add("hidden");
      if (activePreviewItem) {
        openFullDetailsModal(activePreviewItem);
      }
    });
  }
}

function openImagePreviewModal(item) {
  activePreviewItem = item;
  const previewModal = document.getElementById("scan-preview-modal");
  const imgElem = document.getElementById("preview-modal-img");
  const diseaseTitle = document.getElementById("preview-modal-disease");
  const dateElem = document.getElementById("preview-modal-date");

  const mappedDisease = DISEASE_NAMES_MAP[item.disease] ? DISEASE_NAMES_MAP[item.disease][currentLang] : item.disease;
  imgElem.src = item.image_data_url || "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400";
  diseaseTitle.textContent = `${mappedDisease} (${item.confidence.toFixed(0)}%)`;
  dateElem.textContent = item.timestamp ? `📅 ${item.timestamp}` : (item.sha256_hash ? `SHA-256: ${item.sha256_hash.substring(0, 12)}` : "");

  previewModal.classList.remove("hidden");
  lucide.createIcons();
}

function openFullDetailsModal(item) {
  const detailsModal = document.getElementById("scan-details-modal");
  const container = document.getElementById("details-modal-content");

  const mappedDisease = DISEASE_NAMES_MAP[item.disease] ? DISEASE_NAMES_MAP[item.disease][currentLang] : item.disease;
  
  let distHtml = "";
  if (item.distribution) {
    Object.entries(item.distribution).forEach(([cls, p]) => {
      const clsName = DISEASE_NAMES_MAP[cls] ? DISEASE_NAMES_MAP[cls][currentLang] : cls;
      distHtml += `
        <div class="dist-bar-item" style="margin-bottom: 6px;">
          <div class="dist-bar-label" style="display:flex; justify-content:space-between; font-size:0.78rem;">
            <span>${clsName}</span>
            <span>${p.toFixed(1)}%</span>
          </div>
          <div class="dist-progress-bg">
            <div class="dist-progress-fill" style="width: ${p}%"></div>
          </div>
        </div>
      `;
    });
  }

  let envHtml = "";
  if (item.env_data) {
    Object.entries(item.env_data).forEach(([k, v]) => {
      envHtml += `
        <div class="env-item" style="padding: 6px 10px; background: #f8fafc; border-radius: 6px;">
          <span class="env-label" style="font-size:0.72rem; color:#64748b;">${k}</span>
          <span class="env-val" style="font-size:0.82rem; font-weight:700;">${v}</span>
        </div>
      `;
    });
  }

  let sourcesHtml = "";
  if (item.sources && item.sources.length) {
    item.sources.forEach(src => {
      sourcesHtml += `<li>${src}</li>`;
    });
  }

  container.innerHTML = `
    <div style="text-align: center; margin-bottom: 12px;">
      ${item.image_data_url ? `<img src="${item.image_data_url}" style="max-width:100%; max-height:180px; border-radius:8px; object-fit:contain; border:1px solid #e2e8f0; margin-bottom:8px;">` : ''}
      <h3 style="font-size: 1.1rem; font-weight: 700; color: #0f172a;">${mappedDisease}</h3>
      <span style="display:inline-block; padding: 2px 10px; background:#dcfce7; color:#166534; font-size:0.78rem; font-weight:700; border-radius:12px;">Confidence: ${item.confidence.toFixed(0)}%</span>
    </div>

    ${item.is_blended ? `
      <div style="background:#fff7ed; border:1px solid #ffedd5; padding:10px; border-radius:8px; margin-bottom:12px; font-size:0.78rem; color:#c2410c;">
        <strong>⚠️ ${I18N[currentLang].blendedTitle}:</strong> ${item.reasons && item.reasons.length ? item.reasons.join(". ") : "Low certainty caution."}
      </div>
    ` : ''}

    <div style="margin-bottom: 12px;">
      <h4 style="font-size: 0.84rem; font-weight: 700; margin-bottom: 6px; color:#475569;">${I18N[currentLang].distTitle}</h4>
      ${distHtml}
    </div>

    ${envHtml ? `
      <div style="margin-bottom: 12px;">
        <h4 style="font-size: 0.84rem; font-weight: 700; margin-bottom: 6px; color:#475569;">${I18N[currentLang].envTitle}</h4>
        <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap:6px;">${envHtml}</div>
      </div>
    ` : ''}

    <div style="margin-bottom: 12px; background: #f0fdf4; border: 1px solid #bbf7d0; padding: 12px; border-radius: 8px;">
      <h4 style="font-size: 0.88rem; font-weight: 700; color: #166534; margin-bottom: 6px;">🛡️ ${I18N[currentLang].advisoryTitle}</h4>
      <p style="font-size: 0.82rem; color: #15803d; white-space: pre-line;">${item.advisory || 'No advisory text available.'}</p>
    </div>

    ${sourcesHtml ? `
      <div style="font-size: 0.76rem; color: #64748b;">
        <strong>${I18N[currentLang].sourcesTitle}</strong>
        <ul style="padding-left: 16px; margin-top: 4px;">${sourcesHtml}</ul>
      </div>
    ` : ''}
  `;

  detailsModal.classList.remove("hidden");
  lucide.createIcons();
}

/* -------------------------------------------------------------
 * 6. Marketplace Discovery (Crop listings & Google Maps)
 * ------------------------------------------------------------- */
function initMarketplace() {
  const modalBtn = document.getElementById("add-listing-modal-btn");
  const closeModalBtn = document.getElementById("close-modal-btn");
  const modal = document.getElementById("listing-modal");
  const form = document.getElementById("create-listing-form");
  const fetchGpsBtn = document.getElementById("use-gps-location-btn");

  modalBtn.addEventListener("click", () => modal.classList.remove("hidden"));
  closeModalBtn.addEventListener("click", () => modal.classList.add("hidden"));

  if (fetchGpsBtn) {
    fetchGpsBtn.addEventListener("click", () => {
      if (userCoords.allowed && userCoords.lat && userCoords.lng) {
        document.getElementById("form-lat").value = userCoords.lat.toFixed(4);
        document.getElementById("form-lng").value = userCoords.lng.toFixed(4);
      } else {
        alert(currentLang === "kn" ? "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಮೊಬೈಲ್ ಜಿಪಿಎಸ್ ಸಕ್ರಿಯಗೊಳಿಸಿ." : "Please enable device GPS access first.");
      }
    });
  }

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
  feed.innerHTML = `<p class='empty-state'>${currentLang === "kn" ? "ಬೆಳೆ ವಿವರಗಳನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ..." : "Loading listings..."}</p>`;

  try {
    const res = await fetch(`${API_BASE}/api/marketplace/listings`);
    const listings = await res.json();

    feed.innerHTML = "";
    if (!listings || !listings.length) {
      feed.innerHTML = `<p class='empty-state'>${currentLang === "kn" ? "ಯಾವುದೇ ಬೆಳೆ ಮಾರಾಟ ವಿವರಗಳು ಪ್ರಸ್ತುತ ಲಭ್ಯವಿಲ್ಲ." : "No crop listings currently available."}</p>`;
      return;
    }

    listings.forEach(item => {
      const card = document.createElement("div");
      card.className = "market-card";
      card.innerHTML = `
        <div class="market-card-body">
          <div class="market-title-row">
            <h3 class="market-title">${item.crop_name}</h3>
            <span class="market-price">₹${item.price_per_kg}/${currentLang === "kn" ? "ಕೆಜಿ" : "kg"}</span>
          </div>
          <p class="market-meta">${currentLang === "kn" ? "ತಳಿ" : "Variety"}: <strong>${item.variety}</strong> | ${currentLang === "kn" ? "ಪ್ರಮಾಣ" : "Quantity"}: <strong>${item.quantity_kg} kg</strong></p>
          <div class="market-location">
            <i data-lucide="map-pin" class="pin-icon"></i>
            <span>${item.address} (${item.farmer_name} • ${item.contact_phone})</span>
          </div>
          ${item.description ? `<p class="market-meta">${item.description}</p>` : ''}
          <div style="margin-top: 10px;">
            <a href="${item.google_maps_url}" target="_blank" rel="noopener" class="btn-gmaps">
              <i data-lucide="navigation"></i> ${I18N[currentLang].viewGmaps}
            </a>
          </div>
        </div>
      `;
      feed.appendChild(card);
    });
    lucide.createIcons();
  } catch (err) {
    feed.innerHTML = `<p class='empty-state'>${currentLang === "kn" ? "ಮಾರುಕಟ್ಟೆ ವಿವರಗಳನ್ನು ಪಡೆಯುವಲ್ಲಿ ದೋಷವಾಗಿದೆ." : "Error loading marketplace listings."}</p>`;
  }
}

/* -------------------------------------------------------------
 * 7. History Local Cache View & Backend Cache Invalidation
 * ------------------------------------------------------------- */
function initHistorySection() {
  const clearBtn = document.getElementById("clear-history-btn");
  const confirmModal = document.getElementById("confirm-dialog-modal");
  const confirmCancelBtn = document.getElementById("confirm-cancel-btn");
  const confirmOkBtn = document.getElementById("confirm-ok-btn");

  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      confirmModal.classList.remove("hidden");
    });
  }

  if (confirmCancelBtn) {
    confirmCancelBtn.addEventListener("click", () => {
      confirmModal.classList.add("hidden");
    });
  }

  if (confirmOkBtn) {
    confirmOkBtn.addEventListener("click", () => {
      clearAllHistory();
      confirmModal.classList.add("hidden");
    });
  }
}

function showUndoToast(messageText, onUndoCallback) {
  const toast = document.getElementById("undo-toast");
  const msgSpan = document.getElementById("txt-toast-message");
  const undoBtn = document.getElementById("undo-action-btn");

  if (undoTimer) clearTimeout(undoTimer);

  msgSpan.textContent = messageText;
  toast.classList.remove("hidden");

  undoBtn.onclick = () => {
    if (onUndoCallback) onUndoCallback();
    toast.classList.add("hidden");
    if (undoTimer) clearTimeout(undoTimer);
  };

  undoTimer = setTimeout(() => {
    toast.classList.add("hidden");
  }, 3000);
}

async function deleteHistoryItem(index) {
  let history = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  if (index >= 0 && index < history.length) {
    const deletedItem = history.splice(index, 1)[0];
    localStorage.setItem("plantiq_history", JSON.stringify(history));
    renderHistoryFeed();

    // Invalidate from backend SQLite database cache as well
    if (deletedItem.sha256_hash) {
      try {
        await fetch(`${API_BASE}/api/cache/item/${deletedItem.sha256_hash}`, { method: "DELETE" });
      } catch (err) {
        console.warn("Backend cache delete request failed:", err);
      }
    }

    showUndoToast(I18N[currentLang].toastSingleDeleted, async () => {
      // Re-insert into local history
      let currentHistory = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
      currentHistory.splice(index, 0, deletedItem);
      localStorage.setItem("plantiq_history", JSON.stringify(currentHistory));
      renderHistoryFeed();
    });
  }
}

async function clearAllHistory() {
  let history = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  if (!history.length) return;

  const previousHistory = [...history];
  localStorage.removeItem("plantiq_history");
  renderHistoryFeed();

  // Purge all entries from backend SQLite database cache as well
  try {
    await fetch(`${API_BASE}/api/cache/clear`, { method: "DELETE" });
  } catch (err) {
    console.warn("Backend cache clear request failed:", err);
  }

  showUndoToast(I18N[currentLang].toastAllCleared, () => {
    localStorage.setItem("plantiq_history", JSON.stringify(previousHistory));
    renderHistoryFeed();
  });
}

function saveToHistoryLocal(item) {
  let history = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  history.unshift(item);
  if (history.length > 15) history.pop();
  localStorage.setItem("plantiq_history", JSON.stringify(history));
  renderHistoryFeed();
}

function renderHistoryFeed() {
  const feed = document.getElementById("history-feed");
  let history = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  if (!history.length) {
    feed.innerHTML = `<p class='empty-state'>${I18N[currentLang].historyEmpty}</p>`;
    return;
  }

  feed.innerHTML = "";
  history.forEach((item, idx) => {
    const div = document.createElement("div");
    div.className = "history-item";
    const mappedDisease = DISEASE_NAMES_MAP[item.disease] ? DISEASE_NAMES_MAP[item.disease][currentLang] : item.disease;
    const thumbHtml = item.image_data_url 
      ? `<img src="${item.image_data_url}" class="history-thumb" alt="Leaf scan preview">`
      : `<div class="history-thumb-placeholder"><i data-lucide="leaf"></i></div>`;
    const timeStr = item.timestamp || (currentLang === "kn" ? "ಇತ್ತೀಚಿನದು" : "Recent");

    div.innerHTML = `
      <div class="history-item-left">
        ${thumbHtml}
        <div class="history-item-info">
          <h4>${mappedDisease} (${item.confidence.toFixed(0)}%)</h4>
          <div class="history-item-meta">
            <span>📅 ${timeStr}</span>
            <span>SHA-256: ${item.sha256_hash ? item.sha256_hash.substring(0, 10) : 'Cached'}</span>
          </div>
        </div>
      </div>
      <div style="display: flex; gap: 6px; align-items: center;">
        <button class="btn btn-sm btn-secondary view-scan-btn">${currentLang === "kn" ? "ನೋಡಿ" : "View"}</button>
        <button class="btn-icon delete-scan-btn" title="Delete scan" style="color: #ef4444; padding: 6px;"><i data-lucide="trash-2"></i></button>
      </div>
    `;

    // Clicking View opens clean preview modal
    div.querySelector(".view-scan-btn").onclick = () => {
      openImagePreviewModal(item);
    };

    // Clicking Delete removes this scan item
    div.querySelector(".delete-scan-btn").onclick = (e) => {
      e.stopPropagation();
      deleteHistoryItem(idx);
    };

    feed.appendChild(div);
  });
  lucide.createIcons();
}

/* -------------------------------------------------------------
 * 8. Language Toggle (English <-> Kannada) & Voice STT Input
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
  const t = I18N[currentLang];

  // Brand tagline (PlantIQ remains PlantIQ)
  document.getElementById("tagline-text").textContent = t.taglineText;

  // Scanner screen
  document.getElementById("txt-scan-title").textContent = t.scanTitle;
  document.getElementById("txt-scan-sub").textContent = t.scanSub;
  document.getElementById("txt-upload-bold").textContent = t.uploadBold;
  document.getElementById("txt-upload-or").textContent = t.uploadOr;
  document.getElementById("txt-file-hint").textContent = t.fileHint;
  document.getElementById("txt-loc-title").textContent = t.locTitle;
  document.getElementById("txt-lbl-question").textContent = t.lblQuestion;
  document.getElementById("scan-question-input").placeholder = t.scanQuestionPlaceholder;
  document.getElementById("txt-btn-analyze").textContent = t.btnAnalyze;
  document.getElementById("txt-cache-hit").textContent = t.cacheHit;
  document.getElementById("healthy-badge").textContent = t.healthyBadge;
  document.getElementById("conf-lbl").textContent = t.confLbl;
  document.getElementById("txt-blended-title").textContent = t.blendedTitle;
  document.getElementById("txt-dist-title").textContent = t.distTitle;
  document.getElementById("txt-env-title").textContent = t.envTitle;
  document.getElementById("txt-advisory-title").innerHTML = `<i data-lucide="shield-check"></i> ${t.advisoryTitle}`;
  document.getElementById("sources-title").textContent = t.sourcesTitle;
  document.getElementById("txt-btn-handoff").textContent = t.btnHandoff;
  if (document.getElementById("txt-btn-clear-scan")) {
    document.getElementById("txt-btn-clear-scan").textContent = t.btnClearScan;
  }

  // Chatbot screen
  document.getElementById("txt-chat-title").textContent = t.chatTitle;
  document.getElementById("txt-chat-sub").textContent = t.chatSub;
  document.getElementById("txt-chat-welcome").textContent = t.chatWelcome;
  document.getElementById("txt-btn-select-img").textContent = t.btnSelectImg;
  document.getElementById("txt-detach-lbl").textContent = t.detachLbl;
  document.getElementById("chat-text-input").placeholder = t.chatPlaceholder;

  // Picker Modal
  document.getElementById("txt-picker-modal-title").textContent = t.pickerModalTitle;
  document.getElementById("txt-opt-new-title").textContent = t.optNewTitle;
  document.getElementById("txt-opt-new-sub").textContent = t.optNewSub;
  document.getElementById("txt-picker-history-head").textContent = t.pickerHistoryHead;
  document.getElementById("txt-opt-clear-lbl").textContent = t.optClearLbl;

  // Preview & Details Modals
  document.getElementById("txt-preview-modal-title").textContent = t.previewModalTitle;
  document.getElementById("txt-details-modal-title").textContent = t.detailsModalTitle;
  document.getElementById("txt-btn-more-details").textContent = t.btnMoreDetails;
  document.getElementById("txt-btn-close-preview").textContent = t.btnClosePreview;

  // Confirm Modal
  document.getElementById("txt-confirm-title").textContent = t.confirmTitle;
  document.getElementById("txt-confirm-msg").textContent = t.confirmMsg;
  document.getElementById("txt-confirm-cancel").textContent = t.confirmCancel;
  document.getElementById("txt-confirm-ok").textContent = t.confirmOk;

  // Toast
  document.getElementById("txt-btn-undo").textContent = t.btnUndo;

  // Marketplace screen
  document.getElementById("txt-market-title").textContent = t.marketTitle;
  document.getElementById("txt-market-sub").textContent = t.marketSub;
  document.getElementById("txt-btn-sell").textContent = t.btnSell;
  document.getElementById("market-search-input").placeholder = t.marketSearchPlaceholder;

  // History screen
  document.getElementById("txt-history-title").textContent = t.historyTitle;
  document.getElementById("txt-history-sub").textContent = t.historySub;
  if (document.getElementById("txt-btn-clear-history")) {
    document.getElementById("txt-btn-clear-history").textContent = t.btnClearHistory;
  }

  // Bottom Navigation Labels
  document.getElementById("nav-scanner-lbl").textContent = t.navScanner;
  document.getElementById("nav-chat-lbl").textContent = t.navChat;
  document.getElementById("nav-market-lbl").textContent = t.navMarket;
  document.getElementById("nav-history-lbl").textContent = t.navHistory;

  // Listing Modal Labels & Location Guide
  document.getElementById("txt-modal-title").textContent = t.modalTitle;
  document.getElementById("lbl-crop-title").textContent = t.cropTitle;
  document.getElementById("lbl-variety").textContent = t.variety;
  document.getElementById("lbl-quantity").textContent = t.quantity;
  document.getElementById("lbl-price").textContent = t.price;
  document.getElementById("lbl-farmer").textContent = t.farmer;
  document.getElementById("lbl-phone").textContent = t.phone;
  document.getElementById("lbl-address").textContent = t.address;
  document.getElementById("lbl-lat").textContent = t.latitude;
  document.getElementById("lbl-lng").textContent = t.longitude;
  document.getElementById("txt-btn-fetch-gps").textContent = t.btnFetchGps;
  document.getElementById("txt-guide-title").innerHTML = `<i data-lucide="info"></i> ${t.guideTitle}`;
  document.getElementById("txt-guide-body").innerHTML = t.guideBody;
  document.getElementById("txt-btn-publish").textContent = t.btnPublish;

  updateAttachedImageBarUI();
  lucide.createIcons();

  // Re-render diagnosis & marketplace if data exists
  if (currentDiagnosisData) {
    renderDiagnosisResults(currentDiagnosisData);
  }
  fetchMarketplaceListings();
  renderHistoryFeed();
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
