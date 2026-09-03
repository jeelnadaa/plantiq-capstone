// Bilingual i18n Dictionary & Reactive Localization Engine
const I18N_DICTIONARY = {
  en: {
    brandTagline: "Smart Coffee Agronomy & Marketplace",
    navScanner: "Scanner",
    navChat: "Chatbot",
    navMarket: "Marketplace",
    navHistory: "History",
    navProfile: "Profile",
    navAuth: "Sign In",

    // Scanner
    scanTitle: "Coffee Leaf Disease Diagnostic",
    scanSubtitle: "Capture or upload coffee leaf photos to detect diseases and receive verified CCRI treatment advisories.",
    uploadPrompt: "Tap to Take Photo or Upload Image",
    uploadHint: "Supports JPEG, PNG coffee leaf photos",
    locationTitle: "Location & Microclimate",
    btnAutoGps: "Auto GPS",
    btnManualEntry: "Manual Entry",
    lblLat: "Latitude (°N)",
    lblLng: "Longitude (°E)",
    btnGmapsGuide: "GMaps Guide",
    lblQuestion: "Specific Question (Optional)",
    placeholderQuestion: "e.g., Which fungicide is best near water streams?",
    btnAnalyze: "Analyze Leaf",
    confidenceLabel: "Confidence",
    healthyLabel: "Healthy Leaf",
    diseaseLabel: "Disease Detected",
    blendedCaution: "Blended Advisory (Low Confidence Caution)",
    classProbabilities: "Class Probabilities",
    envConditions: "Site Environmental Conditions",
    recommendedSolution: "Recommended Agronomic Solution",
    btnAskInChat: "Ask Follow-Up in Chat",
    btnClearScan: "Clear & New Scan",

    // Chatbot
    chatTitle: "Agri Chatbot Assistant",
    chatSubtitle: "Chat freely in English or Kannada. Attach leaf photos or use voice mic.",
    newConversation: "+ New Conversation",
    btnNewChat: "New Chat",
    chatWelcome: "Hello! I am your PlantIQ agronomy assistant. Ask questions about coffee rust, fertilizers, shade, or spray timing in English or Kannada!",
    chatPlaceholder: "Type your query or tap mic...",
    btnSend: "Send",
    attachedLeaf: "Attached Leaf: ",
    noImageAttached: "No image attached for next question",
    btnRemoveAttach: "Remove",
    pickerModalTitle: "Select Image for Chat Context",
    optUploadNew: "Upload / Capture New Image",
    optHistoryTitle: "Past Scanned Images (History)",
    btnClearAttach: "Clear Selection (No Image)",

    // Marketplace
    marketTitle: "Coffee Crop Marketplace",
    marketSubtitle: "Browse coffee bean lots from local growers with 1-tap Google Maps estate directions.",
    btnSellCrop: "+ Sell Crop",
    tabAllListings: "All Listings",
    tabMyListings: "Your Listings",
    searchPlaceholder: "Search by crop title, variety, location, farmer...",
    filterPriceRange: "Price Filter (₹/kg)",
    lblMinPrice: "Min Price:",
    lblMaxPrice: "Max Price:",
    btnContactPhone: "Call Farmer",
    btnContactWhatsapp: "WhatsApp",
    btnNavMaps: "Google Maps",
    btnDeleteListing: "Delete Listing",
    sellModalTitle: "List Coffee Crop for Sale",
    lblCropTitle: "Crop Title",
    lblVariety: "Variety",
    lblQuantity: "Quantity (kg)",
    lblPricePerKg: "Price per Kg (₹)",
    lblFarmerName: "Farmer Name",
    lblPhone: "Phone / WhatsApp",
    lblAddress: "Estate Address",
    lblEstateLocation: "Estate GPS / Coordinates",
    btnAddPhotos: "Add Crop Photos",
    photoCaptionPlaceholder: "Photo description (e.g., Sundried parchment / harvest lot)",
    btnPublishListing: "Publish Listing",
    noMyListings: "You have not published any crop listings yet.",

    // History & Profile
    historyTitle: "Scan History",
    historySubtitle: "Saved deduplicated scans stored in your local image cache.",
    noScansFound: "No scan history found on this device.",
    btnClearAllHistory: "Clear All",
    confirmClearTitle: "Clear All Scan History?",
    confirmClearMsg: "Are you sure you want to permanently delete all saved leaf scan history? This action cannot be undone.",
    btnConfirmDelete: "Delete All",
    btnUndo: "Undo",
    toastSingleDeleted: "Scan deleted",
    toastAllCleared: "All scan history cleared",
    detailsModalTitle: "Complete Diagnostic Report",
    btnViewDetails: "View Details",
    btnDeleteScan: "Delete Scan",
    profileTitle: "Farmer Account & Diagnostics",
    statTotalScans: "Total Leaf Scans",
    statActiveListings: "Your Active Listings",
    btnLogout: "Sign Out",

    // Voice Modal
    voiceModalTitle: "Choose Voice Language",
    voiceModalSub: "Select the language you want to speak in",
    btnVoiceKn: "ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡಿ (Kannada)",
    btnVoiceEn: "Speak in English",
    btnCancel: "Cancel"
  },
  kn: {
    brandTagline: "ಕಾಫಿ ಬೆಳೆ ಎಐ ಮತ್ತು ಮಾರುಕಟ್ಟೆ",
    navScanner: "ಸ್ಕಾನರ್",
    navChat: "ಚಾಟ್‌ಬಾಟ್",
    navMarket: "ಮಾರುಕಟ್ಟೆ",
    navHistory: "ಇತಿಹಾಸ",
    navProfile: "ಪ್ರೊಫೈಲ್",
    navAuth: "ಲಾಗಿನ್",

    // Scanner
    scanTitle: "ಕಾಫಿ ಎಲೆ ರೋಗ ನಿರ್ಣಯ",
    scanSubtitle: "ಕಾಫಿ ಎಲೆಯ ರೋಗ ಪತ್ತೆಹಚ್ಚಲು ಮತ್ತು ಸೂಕ್ತ ಕೃಷಿ ಸಲಹೆಗಳನ್ನು ಪಡೆಯಲು ಫೋಟೋ ತೆಗೆಯಿರಿ ಅಥವಾ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.",
    uploadPrompt: "ಫೋಟೋ ತೆಗೆಯಲು ಟ್ಯಾಪ್ ಮಾಡಿ ಅಥವಾ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
    uploadHint: "JPEG, PNG ಕಾಫಿ ಎಲೆ ಫೋಟೋಗಳನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ",
    locationTitle: "ಸ್ಥಳ & ಸೂಕ್ಷ್ಮ ವಾತಾವರಣ",
    btnAutoGps: "ಸ್ವಯಂಚಾಲಿತ ಜಿಪಿಎಸ್",
    btnManualEntry: "ಹಸ್ತಚಾಲಿತ ನಮೂದು",
    lblLat: "ಅಕ್ಷಾಂಶ (°N)",
    lblLng: "ರೇಖಾಂಶ (°E)",
    btnGmapsGuide: "ಮ್ಯಾಪ್ಸ್ ಮಾರ್ಗದರ್ಶಿ",
    lblQuestion: "ನಿರ್ದಿಷ್ಟ ಪ್ರಶ್ನೆ (ಐಚ್ಛಿಕ)",
    placeholderQuestion: "ಉದಾ: ಹಳ್ಳದ ಬಳಿ ಯಾವ ಶಿಲೀಂಧ್ರನಾಶಕ ಸುರಕ್ಷಿತ?",
    btnAnalyze: "ಎಲೆ ವಿಶ್ಲೇಷಿಸಿ",
    confidenceLabel: "ಖಚಿತತೆ",
    healthyLabel: "ಆರೋಗ್ಯಕರ ಎಲೆ",
    diseaseLabel: "ರೋಗ ಪತ್ತೆಯಾಗಿದೆ",
    blendedCaution: "ಸಂಯೋಜಿತ ಸಲಹೆ (ಎಚ್ಚರಿಕೆಯ ಸೂಚನೆ)",
    classProbabilities: "ರೋಗ ಸಂಭಾವ್ಯತೆಗಳು",
    envConditions: "ಸ್ಥಳದ ವಾತಾವರಣದ ಸ್ಥಿತಿ",
    recommendedSolution: "ಶಿಫಾರಸು ಮಾಡಿದ ಕೃಷಿ ಪರಿಹಾರ",
    btnAskInChat: "ಚಾಟ್‌ನಲ್ಲಿ ಮತ್ತಷ್ಟು ವಿಚಾರಿಸಿ",
    btnClearScan: "ಫಲಿತಾಂಶ ಅಳಿಸಿ & ಹೊಸ ಸ್ಕ್ಯಾನ್",

    // Chatbot
    chatTitle: "ಕೃಷಿ ಚಾಟ್‌ಬಾಟ್ ಸಹಾಯಕ",
    chatSubtitle: "ಇಂಗ್ಲಿಷ್ ಅಥವಾ ಕನ್ನಡದಲ್ಲಿ ಮುಕ್ತವಾಗಿ ಚಾಟ್ ಮಾಡಿ. ಮೈಕ್ ಮೂಲಕ ಮಾತನಾಡಿ ಅಥವಾ ಫೋಟೋ ಲಗತ್ತಿಸಿ.",
    newConversation: "+ ಹೊಸ ಸಂಭಾಷಣೆ",
    btnNewChat: "ಹೊಸ ಚಾಟ್",
    chatWelcome: "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ PlantIQ ಕೃಷಿ ಸಹಾಯಕ. ಕಾಫಿ ರೋಗಗಳು, ಗೊಬ್ಬರಗಳು ಅಥವಾ ಕೀಟ ನಿರ್ವಹಣೆಯ ಬಗ್ಗೆ ಕನ್ನಡ ಅಥವಾ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ಉಚಿತವಾಗಿ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಿ!",
    chatPlaceholder: "ಸಂದೇಶ ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ಮೈಕ್ ಬಳಸಿ...",
    btnSend: "ಕಳುಹಿಸಿ",
    attachedLeaf: "ಲಗತ್ತಿಸಲಾದ ಎಲೆ: ",
    noImageAttached: "ಮುಂದಿನ ಪ್ರಶ್ನೆಗೆ ಯಾವುದೇ ಚಿತ್ರ ಲಗತ್ತಿಸಿಲ್ಲ",
    btnRemoveAttach: "ತೆಗೆದುಹಾಕಿ",
    pickerModalTitle: "ಚಾಟ್ ಸಂದರ್ಭಕ್ಕಾಗಿ ಚಿತ್ರ ಆಯ್ಕೆಮಾಡಿ",
    optUploadNew: "ಹೊಸ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ / ಸೆರೆಹಿಡಿಯಿರಿ",
    optHistoryTitle: "ಹಿಂದೆ ಸ್ಕ್ಯಾನ್ ಮಾಡಿದ ಚಿತ್ರಗಳು (ಇತಿಹಾಸ)",
    btnClearAttach: "ಆಯ್ಕೆ ರದ್ದುಮಾಡಿ (ಯಾವುದೇ ಚಿತ್ರವಿಲ್ಲ)",

    // Marketplace
    marketTitle: "ಕಾಫಿ ಬೆಳೆ ಮಾರುಕಟ್ಟೆ",
    marketSubtitle: "ಸ್ಥಳೀಯ ಕಾಫಿ ಬೆಳೆಗಾರರ ಮಾರಾಟ ವಿವರಗಳನ್ನು ನೋಡಿ ಮತ್ತು ಗೂಗಲ್ ಮ್ಯಾಪ್ಸ್ ಮೂಲಕ ಸಂಪರ್ಕಿಸಿ.",
    btnSellCrop: "+ ಬೆಳೆ ಮಾರಾಟ ಮಾಡಿ",
    tabAllListings: "ಎಲ್ಲಾ ಪ್ರಕಟಣೆಗಳು",
    tabMyListings: "ನಿಮ್ಮ ಪ್ರಕಟಣೆಗಳು",
    searchPlaceholder: "ಶೀರ್ಷಿಕೆ, ತಳಿ, ಸ್ಥಳ ಅಥವಾ ರೈತರ ಹೆಸರಿನ ಮೂಲಕ ಹುಡುಕಿ...",
    filterPriceRange: "ಬೆಲೆ ಶ್ರೇಣಿ ಫಿಲ್ಟರ್ (₹/ಕೆಜಿ)",
    lblMinPrice: "ಕನಿಷ್ಠ ದರ:",
    lblMaxPrice: "ಗರಿಷ್ಠ ದರ:",
    btnContactPhone: "ಕರೆ ಮಾಡಿ",
    btnContactWhatsapp: "ವಾಟ್ಸಾಪ್",
    btnNavMaps: "ಗೂಗಲ್ ಮ್ಯಾಪ್ಸ್",
    btnDeleteListing: "ಪ್ರಕಟಣೆ ಅಳಿಸಿ",
    sellModalTitle: "ಮಾರಾಟಕ್ಕಾಗಿ ಕಾಫಿ ಬೆಳೆ ನೋಂದಾಯಿಸಿ",
    lblCropTitle: "ಬೆಳೆಯ ಶೀರ್ಷಿಕೆ",
    lblVariety: "ತಳಿ",
    lblQuantity: "ಪ್ರಮಾಣ (ಕೆಜಿ)",
    lblPricePerKg: "ದರ ಪ್ರತಿ ಕೆಜಿಗೆ (₹)",
    lblFarmerName: "ರೈತರ ಹೆಸರು",
    lblPhone: "ಫೋನ್ / ವಾಟ್ಸಾಪ್",
    lblAddress: "ಎಸ್ಟೇಟ್ ವಿಳಾಸ",
    lblEstateLocation: "ಎಸ್ಟೇಟ್ ಜಿಪಿಎಸ್ / ನಿರ್ದೇಶಾಂಕಗಳು",
    btnAddPhotos: "ಬೆಳೆಯ ಫೋಟೋಗಳನ್ನು ಸೇರಿಸಿ",
    photoCaptionPlaceholder: "ಫೋಟೋ ವಿವರಣೆ (ಉದಾ: ಬಿಸಿಲಿನಲ್ಲಿ ಒಣಗುತ್ತಿರುವ ಕಾಫಿ / ಕೊಯ್ಲು ಲಾಟ್)",
    btnPublishListing: "ಪ್ರಕಟಣೆ ಪ್ರಕಟಿಸಿ",
    noMyListings: "ನೀವು ಇನ್ನೂ ಯಾವುದೇ ಬೆಳೆ ಪ್ರಕಟಣೆಗಳನ್ನು ಪ್ರಕಟಿಸಿಲ್ಲ.",

    // History & Profile
    historyTitle: "ಸ್ಕ್ಯಾನ್ ಇತಿಹಾಸ",
    historySubtitle: "ನಿಮ್ಮ ಸಾಧನದಲ್ಲಿ ಉಳಿಸಲಾದ ರೋಗ ಪರಿಶೋಧನೆಗಳು.",
    noScansFound: "ಈ ಸಾಧನದಲ್ಲಿ ಯಾವುದೇ ಸ್ಕ್ಯಾನ್ ಇತಿಹಾಸ ಕಂಡುಬಂದಿಲ್ಲ.",
    btnClearAllHistory: "ಎಲ್ಲಾ ಅಳಿಸಿ",
    confirmClearTitle: "ಎಲ್ಲಾ ಸ್ಕ್ಯಾನ್ ಇತಿಹಾಸವನ್ನು ಅಳಿಸುವುದೇ?",
    confirmClearMsg: "ಉಳಿಸಲಾದ ಎಲ್ಲಾ ಎಲೆ ರೋಗ ಪರಿಶೋಧನೆಗಳನ್ನು ಶಾಶ್ವತವಾಗಿ ಅಳಿಸಲು ನೀವು ಖಚಿತವಾಗಿ ಬಯಸುವಿರಾ?",
    btnConfirmDelete: "ಎಲ್ಲಾ ಅಳಿಸಿ",
    btnUndo: "ಹಿಂಪಡೆಯಿರಿ",
    toastSingleDeleted: "ರೋಗ ಪರಿಶೋಧನೆ ಅಳಿಸಲಾಗಿದೆ",
    toastAllCleared: "ಎಲ್ಲಾ ಇತಿಹಾಸ ಅಳಿಸಲಾಗಿದೆ",
    detailsModalTitle: "ಸಂಪೂರ್ಣ ರೋಗ ನಿರ್ಣಯ ವರದಿ",
    btnViewDetails: "ವಿವರಗಳನ್ನು ನೋಡಿ",
    btnDeleteScan: "ಸ್ಕ್ಯಾನ್ ಅಳಿಸಿ",
    profileTitle: "ರೈತರ ಪ್ರೊಫೈಲ್ ಮತ್ತು ರೋಗ ನಿರ್ಣಯಗಳು",
    statTotalScans: "ಒಟ್ಟು ರೋಗ ಪರಿಶೋಧನೆಗಳು",
    statActiveListings: "ನಿಮ್ಮ ಪ್ರಕಟಣೆಗಳು",
    btnLogout: "ಖಾತೆಯಿಂದ ನಿರ್ಗಮಿಸಿ",

    // Voice Modal
    voiceModalTitle: "ಧ್ವನಿ ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ",
    voiceModalSub: "ನೀವು ಮಾತನಾಡಲು ಬಯಸುವ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    btnVoiceKn: "ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡಿ (Kannada)",
    btnVoiceEn: "Speak in English",
    btnCancel: "ರದ್ದುಗೊಳಿಸಿ"
  }
};

let currentLang = localStorage.getItem("plantiq_lang") || "en";

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem("plantiq_lang", lang);
  updateDOMTranslations();
}

function t(key) {
  return I18N_DICTIONARY[currentLang]?.[key] || I18N_DICTIONARY["en"]?.[key] || key;
}

function updateDOMTranslations() {
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (key && I18N_DICTIONARY[currentLang]?.[key]) {
      el.textContent = I18N_DICTIONARY[currentLang][key];
    }
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (key && I18N_DICTIONARY[currentLang]?.[key]) {
      el.placeholder = I18N_DICTIONARY[currentLang][key];
    }
  });

  const langLabel = document.getElementById("current-lang-indicator");
  if (langLabel) langLabel.textContent = currentLang.toUpperCase();

  if (window.LocationManager) {
    LocationManager.updateUI();
  }
  if (typeof renderHistoryPage === "function") {
    renderHistoryPage();
  }
  if (typeof filterAndRenderListings === "function") {
    filterAndRenderListings();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const langToggleBtn = document.getElementById("btn-lang-toggle");
  if (langToggleBtn) {
    langToggleBtn.onclick = () => {
      setLanguage(currentLang === "en" ? "kn" : "en");
    };
  }
  updateDOMTranslations();
});
