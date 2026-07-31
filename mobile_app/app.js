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
let activeMarketTab = "all"; // 'all' or 'mine'
let undoTimer = null;
let userCoords = { lat: 13.3161, lng: 75.7720, allowed: true }; // Default to Chikmagalur region

// User Auth State
let authToken = localStorage.getItem("plantiq_token") || null;
let currentUser = JSON.parse(localStorage.getItem("plantiq_user") || "null");

// Helper for User-Scoped LocalStorage History Key
function getHistoryStorageKey() {
  if (currentUser && (currentUser.id || currentUser.username)) {
    return `plantiq_history_user_${currentUser.id || currentUser.username}`;
  }
  return "plantiq_history_guest";
}

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
    btnNewChat: "New Chat",
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
    marketTabAll: "All Marketplace Listings",
    marketTabMine: "Your Listings",
    btnSell: "Sell Crop",
    marketSearchPlaceholder: "Search by crop title, variety, location, farmer...",
    lblPriceRangeTitle: "Price Range Filter (₹/kg)",
    lblMinPrice: "Min ₹",
    lblMaxPrice: "Max ₹",
    lblMinSlider: "Min Price:",
    lblMaxSlider: "Max Price:",
    viewGmaps: "View on Google Maps",
    historyTitle: "Deduplicated Scans History",
    historySub: "Quickly review past coffee leaf disease scans saved in your local image cache.",
    historyEmpty: "No recent scan history found.",
    profileTitle: "Farmer Profile",
    profileSub: "Manage your farmer account, scan diagnostics stats, and marketplace listings.",
    statScansLbl: "Total Scans",
    statListingsLbl: "Your Listings",
    lblProfileEmail: "Email Address:",
    lblProfileStatus: "Account Status:",
    profileLogout: "Sign Out of Account",
    navScanner: "Scanner",
    navChat: "Chatbot",
    navMarket: "Market",
    navHistory: "History",
    navProfile: "Profile",
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
    btnPublish: "Publish Listing",
    btnLogin: "Login / Sign Up",
    logout: "Logout",
    authPageTitle: "Welcome to PlantIQ",
    authPageSub: "Sign in to your farmer account to access leaf disease scanning, AI chat, and crop marketplace.",
    authTitleLogin: "Farmer Account Sign In",
    authTitleRegister: "Create Farmer Account",
    tabLogin: "Sign In",
    tabRegister: "Register",
    lblLoginUser: "Email or Username",
    lblLoginPass: "Password",
    btnSubmitLogin: "Sign In to Dashboard",
    lblRegFullname: "Full Name",
    lblRegEmail: "Email Address",
    lblRegUsername: "Username",
    lblRegPass: "Password",
    btnSubmitRegister: "Create Farmer Account",
    loginRequiredMsg: "Please log in or register to access PlantIQ features."
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
    btnNewChat: "ಹೊಸ ಚಾಟ್",
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
    marketTabAll: "ಎಲ್ಲಾ ಮಾರುಕಟ್ಟೆ ಪ್ರಕಟಣೆಗಳು",
    marketTabMine: "ನಿಮ್ಮ ಬೆಳೆ ಪ್ರಕಟಣೆಗಳು",
    btnSell: "ಬೆಳೆ ಮಾರಾಟ ಮಾಡಿ",
    marketSearchPlaceholder: "ಶೀರ್ಷಿಕೆ, ತಳಿ, ಸ್ಥಳ ಅಥವಾ ರೈತರ ಹೆಸರಿನ ಮೂಲಕ ಹುಡುಕಿ...",
    lblPriceRangeTitle: "ಬೆಲೆ ಶ್ರೇಣಿ ಫಿಲ್ಟರ್ (₹/ಕೆಜಿ)",
    lblMinPrice: "ಕನಿಷ್ಠ ₹",
    lblMaxPrice: "ಗರಿಷ್ಠ ₹",
    lblMinSlider: "ಕನಿಷ್ಠ ದರ:",
    lblMaxSlider: "ಗರಿಷ್ಠ ದರ:",
    viewGmaps: "ಗೂಗಲ್ ಮ್ಯಾಪ್ಸ್‌ನಲ್ಲಿ ನೋಡಿ",
    historyTitle: "ಹಿಂದಿನ ಪರಿಶೋಧನೆಗಳ ಇತಿಹಾಸ",
    historySub: "ನಿಮ್ಮ ಕ್ಯಾಶ್‌ನಲ್ಲಿ ಉಳಿಸಲಾದ ಇತ್ತೀಚಿನ ಎಲೆ ರೋಗ ಪರಿಶೋಧನೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
    historyEmpty: "ಯಾವುದೇ ಇತ್ತೀಚಿನ ರೋಗ ನಿರ್ಣಯಗಳು ಕಂಡುಬಂದಿಲ್ಲ.",
    profileTitle: "ರೈತರ ಪ್ರೊಫೈಲ್",
    profileSub: "ನಿಮ್ಮ ಖಾತೆ ವಿವರಗಳು, ರೋಗ ಪರಿಶೋಧನೆಗಳ ವಿವರ ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಪ್ರಕಟಣೆಗಳನ್ನು ನಿರ್ವಹಿಸಿ.",
    statScansLbl: "ಒಟ್ಟು ಪರಿಶೋಧನೆಗಳು",
    statListingsLbl: "ನಿಮ್ಮ ಪ್ರಕಟಣೆಗಳು",
    lblProfileEmail: "ಇಮೇಲ್ ವಿಳಾಸ:",
    lblProfileStatus: "ಖಾತೆ ಸ್ಥಿತಿ:",
    profileLogout: "ಖಾತೆಯಿಂದ ನಿರ್ಗಮಿಸಿ",
    navScanner: "ಸ್ಕಾನರ್",
    navChat: "ಚಾಟ್‌ಬಾಟ್",
    navMarket: "ಮಾರುಕಟ್ಟೆ",
    navHistory: "ಇತಿಹಾಸ",
    navProfile: "ಪ್ರೊಫೈಲ್",
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
    btnPublish: "ಪ್ರಕಟಿಸಿ",
    btnLogin: "ಲಾಗಿನ್ / ಸೈನ್ ಅಪ್",
    logout: "ನಿರ್ಗಮಿಸಿ",
    authPageTitle: "PlantIQ ಗೆ ಸುಸ್ವಾಗತ",
    authPageSub: "ಎಲೆ ರೋಗ ಪತ್ತೆ, ಎಐ ಚಾಟ್ ಮತ್ತು ಮಾರುಕಟ್ಟೆ ಬಳಸಲು ನಿಮ್ಮ ರೈತರ ಖಾತೆಗೆ ಲಾಗಿನ್ ಮಾಡಿ.",
    authTitleLogin: "ರೈತರ ಖಾತೆ ಲಾಗಿನ್",
    authTitleRegister: "ಹೊಸ ರೈತರ ಖಾತೆ ತೆರೆಯಿರಿ",
    tabLogin: "ಲಾಗಿನ್",
    tabRegister: "ನೋಂದಣಿ",
    lblLoginUser: "ಇಮೇಲ್ ಅಥವಾ ಬಳಕೆದಾರ ಹೆಸರು",
    lblLoginPass: "ಪಾಸ್‌ವರ್ಡ್",
    btnSubmitLogin: "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಲಾಗಿನ್ ಮಾಡಿ",
    lblRegFullname: "ಪೂರ್ಣ ಹೆಸರು",
    lblRegEmail: "ಇಮೇಲ್ ವಿಳಾಸ",
    lblRegUsername: "ಬಳಕೆದಾರ ಹೆಸರು",
    lblRegPass: "ಪಾಸ್‌ವರ್ಡ್",
    btnSubmitRegister: "ರೈತರ ಖಾತೆ ತೆರೆಯಿರಿ",
    loginRequiredMsg: "PlantIQ ವೈಶಿಷ್ಟ್ಯಗಳನ್ನು ಬಳಸಲು ದಯವಿಟ್ಟು ಲಾಗಿನ್ ಮಾಡಿ."
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
document.addEventListener("DOMContentLoaded", async () => {
  lucide.createIcons();
  initNavigation();
  initLocation();
  initScanner();
  initChatbot();
  initImagePickerModal();
  initModalsAndPreviews();
  initHistorySection();
  initMarketplace();
  initAuthUI();
  initLanguageToggle();
  initSpeech();
  
  await validateSessionAndInit();
  updateLanguageUI();
});

async function validateSessionAndInit() {
  const bottomNav = document.querySelector(".bottom-nav");
  const screens = document.querySelectorAll(".app-screen");
  const navItems = document.querySelectorAll(".nav-item");

  if (authToken) {
    try {
      const res = await fetch(`${API_BASE}/api/auth/me`, {
        headers: getAuthHeaders()
      });
      if (res.ok) {
        currentUser = await res.json();
        localStorage.setItem("plantiq_user", JSON.stringify(currentUser));
      } else {
        // Token expired/invalid
        authToken = null;
        currentUser = null;
        localStorage.removeItem("plantiq_token");
        localStorage.removeItem("plantiq_user");
      }
    } catch (e) {
      console.warn("Session check offline:", e);
    }
  }

  if (!authToken || !currentUser) {
    screens.forEach(s => s.classList.remove("active"));
    navItems.forEach(n => n.classList.remove("active"));
    const authScreen = document.getElementById("screen-auth");
    if (authScreen) authScreen.classList.add("active");
    if (bottomNav) bottomNav.style.display = "none";
    updateAuthProfileBar();
    renderHistoryFeed();
    return false;
  }

  // User is Logged In! Activate Scanner Screen by default on reload
  screens.forEach(s => s.classList.remove("active"));
  navItems.forEach(n => n.classList.remove("active"));

  document.getElementById("screen-scanner").classList.add("active");
  document.querySelector('[data-target="screen-scanner"]').classList.add("active");
  if (bottomNav) bottomNav.style.display = "flex";

  updateAuthProfileBar();
  renderHistoryFeed();
  fetchChatThreads();
  renderProfileStats();
  return true;
}

function checkAuthOrPrompt() {
  const bottomNav = document.querySelector(".bottom-nav");
  const screens = document.querySelectorAll(".app-screen");
  const navItems = document.querySelectorAll(".nav-item");

  if (!authToken || !currentUser) {
    screens.forEach(s => s.classList.remove("active"));
    navItems.forEach(n => n.classList.remove("active"));
    const authScreen = document.getElementById("screen-auth");
    if (authScreen) authScreen.classList.add("active");
    if (bottomNav) bottomNav.style.display = "none";
    return false;
  }

  if (bottomNav) bottomNav.style.display = "flex";
  return true;
}

// Helper for auth headers
function getAuthHeaders() {
  const headers = {};
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }
  return headers;
}

/* -------------------------------------------------------------
 * 0. User Authentication Module & Login Page
 * ------------------------------------------------------------- */
function initAuthUI() {
  const openAuthBtn = document.getElementById("open-auth-modal-btn");
  const closeAuthBtn = document.getElementById("close-auth-modal-btn");
  const authModal = document.getElementById("auth-modal");
  
  // Modal tabs
  const tabLogin = document.getElementById("tab-auth-login");
  const tabRegister = document.getElementById("tab-auth-register");
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");

  // Page tabs
  const pageTabLogin = document.getElementById("page-tab-login");
  const pageTabRegister = document.getElementById("page-tab-register");
  const pageLoginForm = document.getElementById("page-login-form");
  const pageRegisterForm = document.getElementById("page-register-form");

  if (openAuthBtn) openAuthBtn.addEventListener("click", () => authModal.classList.remove("hidden"));
  if (closeAuthBtn) closeAuthBtn.addEventListener("click", () => authModal.classList.add("hidden"));

  // Page Tab Switcher
  if (pageTabLogin && pageTabRegister) {
    pageTabLogin.addEventListener("click", () => {
      pageTabLogin.classList.add("active");
      pageTabLogin.style.background = "#ffffff";
      pageTabLogin.style.color = "#166534";

      pageTabRegister.classList.remove("active");
      pageTabRegister.style.background = "transparent";
      pageTabRegister.style.color = "#64748b";

      pageLoginForm.classList.remove("hidden");
      pageRegisterForm.classList.add("hidden");
    });

    pageTabRegister.addEventListener("click", () => {
      pageTabRegister.classList.add("active");
      pageTabRegister.style.background = "#ffffff";
      pageTabRegister.style.color = "#166534";

      pageTabLogin.classList.remove("active");
      pageTabLogin.style.background = "transparent";
      pageTabLogin.style.color = "#64748b";

      pageRegisterForm.classList.remove("hidden");
      pageLoginForm.classList.add("hidden");
    });
  }

  // Handle Login (Page Form)
  pageLoginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const userInput = document.getElementById("page-login-user-input").value.trim();
    const passInput = document.getElementById("page-login-pass-input").value.trim();
    await handleLoginSubmit(userInput, passInput, pageLoginForm);
  });

  // Handle Register (Page Form)
  pageRegisterForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fullname = document.getElementById("page-reg-fullname-input").value.trim();
    const email = document.getElementById("page-reg-email-input").value.trim();
    const username = document.getElementById("page-reg-username-input").value.trim();
    const pass = document.getElementById("page-reg-pass-input").value.trim();
    await handleRegisterSubmit(fullname, email, username, pass, pageRegisterForm);
  });

  // Modal Login Form
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const userInput = document.getElementById("login-user-input").value.trim();
      const passInput = document.getElementById("login-pass-input").value.trim();
      await handleLoginSubmit(userInput, passInput, loginForm);
    });
  }

  // Modal Register Form
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fullname = document.getElementById("reg-fullname-input").value.trim();
      const email = document.getElementById("reg-email-input").value.trim();
      const username = document.getElementById("reg-username-input").value.trim();
      const pass = document.getElementById("reg-pass-input").value.trim();
      await handleRegisterSubmit(fullname, email, username, pass, registerForm);
    });
  }
}

async function handleLoginSubmit(usernameOrEmail, password, formElem) {
  try {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email_or_username: usernameOrEmail, password: password })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Login failed.");
    }

    const data = await res.json();
    authToken = data.access_token;
    currentUser = data.user;
    localStorage.setItem("plantiq_token", authToken);
    localStorage.setItem("plantiq_user", JSON.stringify(currentUser));

    document.getElementById("auth-modal").classList.add("hidden");
    if (formElem) formElem.reset();

    // Unlock App Navigation to Scanner Screen
    document.querySelectorAll(".app-screen").forEach(s => s.classList.remove("active"));
    document.getElementById("screen-scanner").classList.add("active");
    document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
    document.querySelector('[data-target="screen-scanner"]').classList.add("active");

    updateAuthProfileBar();
    checkAuthOrPrompt();
    renderHistoryFeed();
    fetchChatThreads();
    renderProfileStats();
  } catch (err) {
    alert("Login Error: " + err.message);
  }
}

async function handleRegisterSubmit(fullname, email, username, password, formElem) {
  try {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: fullname,
        email: email,
        username: username,
        password: password
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Registration failed.");
    }

    const data = await res.json();
    authToken = data.access_token;
    currentUser = data.user;
    localStorage.setItem("plantiq_token", authToken);
    localStorage.setItem("plantiq_user", JSON.stringify(currentUser));

    document.getElementById("auth-modal").classList.add("hidden");
    if (formElem) formElem.reset();

    // Unlock App Navigation to Scanner Screen
    document.querySelectorAll(".app-screen").forEach(s => s.classList.remove("active"));
    document.getElementById("screen-scanner").classList.add("active");
    document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
    document.querySelector('[data-target="screen-scanner"]').classList.add("active");

    updateAuthProfileBar();
    checkAuthOrPrompt();
    renderHistoryFeed();
    fetchChatThreads();
    renderProfileStats();
  } catch (err) {
    alert("Registration Error: " + err.message);
  }
}

function updateAuthProfileBar() {
  const profileBar = document.getElementById("user-profile-bar");
  if (!profileBar) return;

  if (currentUser && authToken) {
    profileBar.innerHTML = `
      <div style="display:flex; align-items:center; gap:6px; background:#f0fdf4; border:1px solid #bbf7d0; padding:4px 10px; border-radius:20px; font-size:0.76rem; color:#166534; font-weight:700;">
        <i data-lucide="user" style="width:14px; height:14px;"></i>
        <span>${currentUser.full_name || currentUser.username}</span>
        <button id="user-logout-btn" style="background:none; border:none; color:#ef4444; margin-left:6px; cursor:pointer;" title="Logout"><i data-lucide="log-out" style="width:14px; height:14px;"></i></button>
      </div>
    `;

    document.getElementById("user-logout-btn").onclick = async () => {
      await performUserLogout();
    };
  } else {
    profileBar.innerHTML = `
      <button id="open-auth-modal-btn" class="btn btn-sm btn-outline" style="border-radius: 20px; font-size: 0.76rem; padding: 4px 10px; border-color: #a7f3d0; color: #15803d;">
        <i data-lucide="user-check"></i> <span id="txt-btn-login">${I18N[currentLang].btnLogin}</span>
      </button>
    `;
    document.getElementById("open-auth-modal-btn").onclick = () => {
      checkAuthOrPrompt();
    };
  }
  lucide.createIcons();
}

async function performUserLogout() {
  try {
    await fetch(`${API_BASE}/api/auth/logout`, {
      method: "POST",
      headers: getAuthHeaders()
    });
  } catch (e) {}
  authToken = null;
  currentUser = null;
  localStorage.removeItem("plantiq_token");
  localStorage.removeItem("plantiq_user");
  updateAuthProfileBar();
  checkAuthOrPrompt();
  renderHistoryFeed();
}

/* -------------------------------------------------------------
 * 1. Navigation & UI Tabs
 * ------------------------------------------------------------- */
function initNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  const screens = document.querySelectorAll(".app-screen");

  navItems.forEach(item => {
    item.addEventListener("click", () => {
      if (!checkAuthOrPrompt()) return;

      const targetId = item.getAttribute("data-target");

      navItems.forEach(n => n.classList.remove("active"));
      screens.forEach(s => s.classList.remove("active"));

      item.classList.add("active");
      document.getElementById(targetId).classList.add("active");

      if (targetId === "screen-market") {
        fetchMarketplaceListings();
      } else if (targetId === "screen-chat") {
        fetchChatThreads();
      } else if (targetId === "screen-history") {
        renderHistoryFeed();
      } else if (targetId === "screen-profile") {
        renderProfileStats();
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
    if (!checkAuthOrPrompt()) return;
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

  if (resultsSection) resultsSection.classList.add("hidden");
  selectedScanFile = null;
  currentDiagnosisData = null;
  if (fileInput) fileInput.value = "";
  if (questionInput) questionInput.value = "";
  if (previewContainer) previewContainer.classList.add("hidden");
  if (placeholder) placeholder.classList.remove("hidden");

  const scannerScreen = document.getElementById("screen-scanner");
  if (scannerScreen) scannerScreen.scrollIntoView({ behavior: "smooth" });
}

async function runLeafAnalysis() {
  if (!checkAuthOrPrompt()) return;

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
      headers: getAuthHeaders(),
      body: formData
    });

    if (res.status === 401) {
      checkAuthOrPrompt();
      throw new Error(I18N[currentLang].loginRequiredMsg);
    }

    if (!res.ok) throw new Error("Diagnosis request failed.");

    const data = await res.json();
    currentDiagnosisData = data;
    renderDiagnosisResults(data);

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

  const cacheBadge = document.getElementById("cache-badge");
  if (data.cache_hit) {
    cacheBadge.classList.remove("hidden");
  } else {
    cacheBadge.classList.add("hidden");
  }

  const mappedDisease = DISEASE_NAMES_MAP[data.disease] ? DISEASE_NAMES_MAP[data.disease][currentLang] : data.disease;
  document.getElementById("diag-class-name").textContent = mappedDisease;
  document.getElementById("diag-conf-value").textContent = `${data.confidence.toFixed(0)}%`;

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

  document.getElementById("advisory-text-content").textContent = data.advisory;

  const sourcesList = document.getElementById("sources-list");
  sourcesList.innerHTML = "";
  if (data.sources && data.sources.length) {
    data.sources.forEach(src => {
      sourcesList.innerHTML += `<li>${src}</li>`;
    });
  }

  document.getElementById("handoff-chat-btn").onclick = handoffToChat;
}

async function handoffToChat() {
  if (!checkAuthOrPrompt()) return;
  if (!currentDiagnosisData) return;

  const formData = new FormData();
  formData.append("disease", currentDiagnosisData.disease);
  formData.append("confidence", currentDiagnosisData.confidence);
  formData.append("advisory", currentDiagnosisData.advisory);
  formData.append("language", currentLang);

  try {
    const res = await fetch(`${API_BASE}/api/chat/start-from-scan`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: formData
    });
    const session = await res.json();
    currentSessionId = session.session_id;

    attachedScanContext = currentDiagnosisData;
    updateAttachedImageBarUI();

    document.querySelector('[data-target="screen-chat"]').click();
    renderChatMessages(session.messages);
    fetchChatThreads();
  } catch (e) {
    console.error("Handoff Error:", e);
  }
}

/* -------------------------------------------------------------
 * 4. Multi-Threaded Chatbot Module & Image Picker Modal
 * ------------------------------------------------------------- */
function initChatbot() {
  const sendBtn = document.getElementById("chat-send-btn");
  const textInput = document.getElementById("chat-text-input");
  const attachBtn = document.getElementById("chat-attach-btn");
  const fileInput = document.getElementById("chat-file-input");
  const detachBtn = document.getElementById("detach-image-btn");
  const newChatBtn = document.getElementById("new-chat-btn");
  const threadSelect = document.getElementById("chat-thread-select");

  attachBtn.addEventListener("click", () => {
    if (!checkAuthOrPrompt()) return;
    document.getElementById("open-picker-btn").click();
  });

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

  if (newChatBtn) {
    newChatBtn.addEventListener("click", () => {
      if (!checkAuthOrPrompt()) return;
      startNewChatThread();
    });
  }

  if (threadSelect) {
    threadSelect.addEventListener("change", (e) => {
      if (!checkAuthOrPrompt()) return;
      const selectedThreadId = e.target.value;
      if (!selectedThreadId) {
        startNewChatThread();
      } else {
        loadChatThreadMessages(selectedThreadId);
      }
    });
  }

  sendBtn.addEventListener("click", sendChatMessage);
  textInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendChatMessage();
  });
}

async function fetchChatThreads() {
  if (!authToken || !currentUser) return;
  const threadSelect = document.getElementById("chat-thread-select");
  if (!threadSelect) return;

  try {
    const res = await fetch(`${API_BASE}/api/chat/threads`, {
      headers: getAuthHeaders()
    });

    if (res.status === 401) {
      checkAuthOrPrompt();
      return;
    }

    const threads = await res.json();

    threadSelect.innerHTML = `<option value="">+ ${I18N[currentLang].btnNewChat}</option>`;
    if (threads && threads.length) {
      threads.forEach(t => {
        const opt = document.createElement("option");
        opt.value = t.thread_id;
        opt.textContent = `💬 ${t.title}`;
        if (t.thread_id === currentSessionId) opt.selected = true;
        threadSelect.appendChild(opt);
      });
    }
  } catch (err) {
    console.warn("Failed to load chat threads:", err);
  }
}

async function startNewChatThread() {
  currentSessionId = null;
  const messagesList = document.getElementById("chat-messages-list");
  messagesList.innerHTML = `
    <div class="msg assistant-msg">
      <div class="avatar"><i data-lucide="bot"></i></div>
      <div class="msg-bubble">
        <p id="txt-chat-welcome">${I18N[currentLang].chatWelcome}</p>
      </div>
    </div>
  `;
  lucide.createIcons();

  const threadSelect = document.getElementById("chat-thread-select");
  if (threadSelect) threadSelect.value = "";
}

async function loadChatThreadMessages(threadId) {
  currentSessionId = threadId;
  const messagesList = document.getElementById("chat-messages-list");
  messagesList.innerHTML = `<p style="text-align:center; font-size:0.8rem; color:#94a3b8; padding:20px;">${currentLang === "kn" ? "ಸಂದೇಶಗಳನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ..." : "Loading chat messages..."}</p>`;

  try {
    const res = await fetch(`${API_BASE}/api/chat/threads/${threadId}/messages`, {
      headers: getAuthHeaders()
    });

    if (res.status === 401) {
      checkAuthOrPrompt();
      return;
    }

    const messages = await res.json();
    renderChatMessages(messages);
  } catch (err) {
    messagesList.innerHTML = `<p style="text-align:center; color:#ef4444; font-size:0.8rem;">Failed to load messages.</p>`;
  }
}

function initImagePickerModal() {
  const openPickerBtn = document.getElementById("open-picker-btn");
  const closePickerBtn = document.getElementById("close-picker-modal-btn");
  const pickerModal = document.getElementById("image-picker-modal");
  const optUploadNewBtn = document.getElementById("opt-upload-new-btn");
  const optClearImgBtn = document.getElementById("opt-clear-img-btn");

  openPickerBtn.addEventListener("click", () => {
    if (!checkAuthOrPrompt()) return;
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
  let history = JSON.parse(localStorage.getItem(getHistoryStorageKey()) || "[]");
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

      historyOptDiv.querySelector(".view-opt-btn").onclick = (evt) => {
        evt.stopPropagation();
        openImagePreviewModal(item);
      };

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
  if (!checkAuthOrPrompt()) return;

  const textInput = document.getElementById("chat-text-input");
  const message = textInput.value.trim();
  if (!message && !selectedChatFile && !attachedScanContext) return;

  let displayMsg = message;
  if (!displayMsg) {
    if (selectedChatFile) displayMsg = currentLang === "kn" ? "[ವಿಶ್ಲೇಷಣೆಗಾಗಿ ಫೋಟೋ ಲಗತ್ತಿಸಲಾಗಿದೆ]" : "[Image attached for analysis]";
    else if (attachedScanContext) displayMsg = `${currentLang === "kn" ? "[ರೋಗ ಪರಿಶೋಧನೆ ಲಗತ್ತಿಸಲಾಗಿದೆ: " : "[Scan context attached: "}${attachedScanContext.disease}]`;
  }

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

  selectedChatFile = null;
  attachedScanContext = null;
  updateAttachedImageBarUI();

  try {
    const res = await fetch(`${API_BASE}/api/chat/message`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: formData
    });

    if (res.status === 401) {
      checkAuthOrPrompt();
      throw new Error(I18N[currentLang].loginRequiredMsg);
    }

    const data = await res.json();
    currentSessionId = data.session_id;

    appendMessageBubble("assistant", data.reply, data.sources);
    fetchChatThreads();
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
  if (!messages || !messages.length) {
    messagesList.innerHTML = `
      <div class="msg assistant-msg">
        <div class="avatar"><i data-lucide="bot"></i></div>
        <div class="msg-bubble">
          <p id="txt-chat-welcome">${I18N[currentLang].chatWelcome}</p>
        </div>
      </div>
    `;
  } else {
    messages.forEach(m => {
      if (m.role !== "system") {
        appendMessageBubble(m.role, m.content, m.sources);
      }
    });
  }
  lucide.createIcons();
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
 * 6. Marketplace Discovery & Universal Search / Dual Price Range
 * ------------------------------------------------------------- */
function initMarketplace() {
  const modalBtn = document.getElementById("add-listing-modal-btn");
  const closeModalBtn = document.getElementById("close-modal-btn");
  const modal = document.getElementById("listing-modal");
  const form = document.getElementById("create-listing-form");
  const fetchGpsBtn = document.getElementById("use-gps-location-btn");

  const tabAll = document.getElementById("market-tab-all");
  const tabMine = document.getElementById("market-tab-mine");
  const searchInput = document.getElementById("market-search-input");
  
  const minSlider = document.getElementById("market-min-slider");
  const maxSlider = document.getElementById("market-max-slider");
  const minInput = document.getElementById("market-min-input");
  const maxInput = document.getElementById("market-max-input");
  const badge = document.getElementById("market-price-range-badge");

  if (tabAll && tabMine) {
    tabAll.addEventListener("click", () => {
      activeMarketTab = "all";
      tabAll.classList.add("active");
      tabAll.style.background = "#ffffff";
      tabAll.style.color = "#166534";

      tabMine.classList.remove("active");
      tabMine.style.background = "transparent";
      tabMine.style.color = "#64748b";

      fetchMarketplaceListings();
    });

    tabMine.addEventListener("click", () => {
      if (!checkAuthOrPrompt()) return;
      activeMarketTab = "mine";
      tabMine.classList.add("active");
      tabMine.style.background = "#ffffff";
      tabMine.style.color = "#166534";

      tabAll.classList.remove("active");
      tabAll.style.background = "transparent";
      tabAll.style.color = "#64748b";

      fetchMarketplaceListings();
    });
  }

  function syncPriceControls(source) {
    let minV = parseFloat(minSlider.value) || 0;
    let maxV = parseFloat(maxSlider.value) || 1000;

    if (source === "minInput") {
      minV = parseFloat(minInput.value) || 0;
      minSlider.value = minV;
    } else if (source === "maxInput") {
      maxV = parseFloat(maxInput.value) || 1000;
      maxSlider.value = maxV;
    } else if (source === "minSlider") {
      minInput.value = minV;
    } else if (source === "maxSlider") {
      maxInput.value = maxV;
    }

    if (minV > maxV) {
      if (source === "minInput" || source === "minSlider") {
        maxV = minV;
        maxSlider.value = maxV;
        maxInput.value = maxV;
      } else {
        minV = maxV;
        minSlider.value = minV;
        minInput.value = minV;
      }
    }

    if (badge) {
      badge.textContent = `₹${minV} - ₹${maxV}/${currentLang === "kn" ? "ಕೆಜಿ" : "kg"}`;
    }

    fetchMarketplaceListings();
  }

  if (searchInput) searchInput.addEventListener("input", fetchMarketplaceListings);

  if (minSlider) minSlider.addEventListener("input", () => syncPriceControls("minSlider"));
  if (maxSlider) maxSlider.addEventListener("input", () => syncPriceControls("maxSlider"));
  if (minInput) minInput.addEventListener("input", () => syncPriceControls("minInput"));
  if (maxInput) maxInput.addEventListener("input", () => syncPriceControls("maxInput"));

  modalBtn.addEventListener("click", () => {
    if (!checkAuthOrPrompt()) return;
    modal.classList.remove("hidden");
  });

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
    if (!checkAuthOrPrompt()) return;

    const formData = new FormData(form);

    try {
      const res = await fetch(`${API_BASE}/api/marketplace/listings`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: formData
      });
      if (res.ok) {
        modal.classList.add("hidden");
        form.reset();
        fetchMarketplaceListings();
        renderProfileStats();
      }
    } catch (err) {
      alert("Failed to publish listing: " + err.message);
    }
  });
}

async function fetchMarketplaceListings() {
  const feed = document.getElementById("marketplace-feed");
  if (!feed) return;
  feed.innerHTML = `<p class='empty-state'>${currentLang === "kn" ? "ಬೆಳೆ ವಿವರಗಳನ್ನು ಲೋಡ್ ಮಾಡಲಾಗುತ್ತಿದೆ..." : "Loading listings..."}</p>`;

  const searchInput = document.getElementById("market-search-input");
  const minSlider = document.getElementById("market-min-slider");
  const maxSlider = document.getElementById("market-max-slider");

  const queryVal = searchInput ? searchInput.value.trim() : "";
  const minPriceVal = minSlider ? parseFloat(minSlider.value) : 0;
  const maxPriceVal = maxSlider ? parseFloat(maxSlider.value) : 1000;

  try {
    let endpoint = activeMarketTab === "mine" ? `${API_BASE}/api/marketplace/my-listings` : `${API_BASE}/api/marketplace/listings`;
    
    // Append search & price parameters
    const params = new URLSearchParams();
    if (queryVal) params.append("query", queryVal);
    if (minPriceVal > 0) params.append("min_price", minPriceVal.toString());
    if (maxPriceVal < 1000) params.append("max_price", maxPriceVal.toString());

    if (params.toString() && activeMarketTab !== "mine") {
      endpoint += `?${params.toString()}`;
    }

    const headers = activeMarketTab === "mine" ? getAuthHeaders() : {};
    const res = await fetch(endpoint, { headers });

    if (res.status === 401) {
      checkAuthOrPrompt();
      return;
    }

    let listings = await res.json();

    // Client-side multi-field filter fallback for 'mine' tab
    if (activeMarketTab === "mine" && listings && listings.length) {
      listings = listings.filter(l => l.price_per_kg >= minPriceVal && l.price_per_kg <= maxPriceVal);
      if (queryVal) {
        const q = queryVal.toLowerCase();
        listings = listings.filter(l => 
          (l.crop_name && l.crop_name.toLowerCase().includes(q)) ||
          (l.variety && l.variety.toLowerCase().includes(q)) ||
          (l.address && l.address.toLowerCase().includes(q)) ||
          (l.farmer_name && l.farmer_name.toLowerCase().includes(q)) ||
          (l.description && l.description.toLowerCase().includes(q))
        );
      }
    }

    feed.innerHTML = "";
    if (!listings || !listings.length) {
      feed.innerHTML = `<p class='empty-state'>${activeMarketTab === "mine" ? (currentLang === "kn" ? "ನೀವು ಯಾವುದೇ ಬೆಳೆ ಮಾರಾಟ ವಿವರಗಳನ್ನು ಪ್ರಕಟಿಸಿಲ್ಲ." : "You have not published any crop listings yet.") : (currentLang === "kn" ? "ಯಾವುದೇ ಬೆಳೆ ಮಾರಾಟ ವಿವರಗಳು ಕಂಡುಬಂದಿಲ್ಲ." : "No crop listings found matching your search.")}</p>`;
      return;
    }

    listings.forEach(item => {
      const card = document.createElement("div");
      card.className = "market-card";
      const isOwner = currentUser && item.user_id === currentUser.id;

      card.innerHTML = `
        <div class="market-card-body">
          <div class="market-title-row" style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
              <h3 class="market-title">${item.crop_name}</h3>
              ${isOwner ? `<span style="background:#e0f2fe; color:#0369a1; font-size:0.7rem; font-weight:700; padding:2px 8px; border-radius:10px;">${currentLang === "kn" ? "ನಿಮ್ಮ ಪ್ರಕಟಣೆ" : "Your Listing"}</span>` : ''}
            </div>
            <span class="market-price">₹${item.price_per_kg}/${currentLang === "kn" ? "ಕೆಜಿ" : "kg"}</span>
          </div>
          <p class="market-meta">${currentLang === "kn" ? "ತಳಿ" : "Variety"}: <strong>${item.variety}</strong> | ${currentLang === "kn" ? "ಪ್ರಮಾಣ" : "Quantity"}: <strong>${item.quantity_kg} kg</strong></p>
          <div class="market-location">
            <i data-lucide="map-pin" class="pin-icon"></i>
            <span>${item.address} (${item.farmer_name} • ${item.contact_phone})</span>
          </div>
          ${item.description ? `<p class="market-meta">${item.description}</p>` : ''}
          <div style="display:flex; justify-content:space-between; align-items:center; margin-top: 10px;">
            <a href="${item.google_maps_url}" target="_blank" rel="noopener" class="btn-gmaps">
              <i data-lucide="navigation"></i> ${I18N[currentLang].viewGmaps}
            </a>
            ${isOwner ? `<button class="btn btn-sm btn-outline delete-listing-btn" data-id="${item.id}" style="border-color:#fca5a5; color:#dc2626;"><i data-lucide="trash-2"></i> ${currentLang === "kn" ? "ಅಳಿಸಿ" : "Delete"}</button>` : ''}
          </div>
        </div>
      `;

      if (isOwner) {
        const delBtn = card.querySelector(".delete-listing-btn");
        if (delBtn) {
          delBtn.onclick = async () => {
            if (confirm(currentLang === "kn" ? "ಈ ಪ್ರಕಟಣೆಯನ್ನು ಅಳಿಸಲು ಖಚಿತವಾಗಿದ್ದೀರಾ?" : "Are you sure you want to delete this listing?")) {
              await deleteMyListing(item.id);
            }
          };
        }
      }

      feed.appendChild(card);
    });
    lucide.createIcons();
  } catch (err) {
    feed.innerHTML = `<p class='empty-state'>${currentLang === "kn" ? "ಮಾರುಕಟ್ಟೆ ವಿವರಗಳನ್ನು ಪಡೆಯುವಲ್ಲಿ ದೋಷವಾಗಿದೆ." : "Error loading marketplace listings."}</p>`;
  }
}

async function deleteMyListing(listingId) {
  try {
    const res = await fetch(`${API_BASE}/api/marketplace/listings/${listingId}`, {
      method: "DELETE",
      headers: getAuthHeaders()
    });
    if (res.ok) {
      fetchMarketplaceListings();
      renderProfileStats();
    }
  } catch (e) {
    alert("Failed to delete listing.");
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
      if (!checkAuthOrPrompt()) return;
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
  if (!checkAuthOrPrompt()) return;

  const storageKey = getHistoryStorageKey();
  let history = JSON.parse(localStorage.getItem(storageKey) || "[]");
  if (index >= 0 && index < history.length) {
    const deletedItem = history.splice(index, 1)[0];
    localStorage.setItem(storageKey, JSON.stringify(history));
    renderHistoryFeed();
    renderProfileStats();

    if (deletedItem.sha256_hash) {
      try {
        await fetch(`${API_BASE}/api/cache/item/${deletedItem.sha256_hash}`, {
          method: "DELETE",
          headers: getAuthHeaders()
        });
      } catch (err) {
        console.warn("Backend cache delete request failed:", err);
      }
    }

    showUndoToast(I18N[currentLang].toastSingleDeleted, async () => {
      let currentHistory = JSON.parse(localStorage.getItem(storageKey) || "[]");
      currentHistory.splice(index, 0, deletedItem);
      localStorage.setItem(storageKey, JSON.stringify(currentHistory));
      renderHistoryFeed();
      renderProfileStats();
    });
  }
}

async function clearAllHistory() {
  if (!checkAuthOrPrompt()) return;

  const storageKey = getHistoryStorageKey();
  let history = JSON.parse(localStorage.getItem(storageKey) || "[]");
  if (!history.length) return;

  const previousHistory = [...history];
  localStorage.removeItem(storageKey);
  renderHistoryFeed();
  renderProfileStats();

  try {
    await fetch(`${API_BASE}/api/cache/clear`, {
      method: "DELETE",
      headers: getAuthHeaders()
    });
  } catch (err) {
    console.warn("Backend cache clear request failed:", err);
  }

  showUndoToast(I18N[currentLang].toastAllCleared, () => {
    localStorage.setItem(storageKey, JSON.stringify(previousHistory));
    renderHistoryFeed();
    renderProfileStats();
  });
}

function saveToHistoryLocal(item) {
  const storageKey = getHistoryStorageKey();
  let history = JSON.parse(localStorage.getItem(storageKey) || "[]");
  history.unshift(item);
  if (history.length > 15) history.pop();
  localStorage.setItem(storageKey, JSON.stringify(history));
  renderHistoryFeed();
  renderProfileStats();
}

function renderHistoryFeed() {
  const feed = document.getElementById("history-feed");
  if (!feed) return;
  const storageKey = getHistoryStorageKey();
  let history = JSON.parse(localStorage.getItem(storageKey) || "[]");
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

    div.querySelector(".view-scan-btn").onclick = () => {
      openImagePreviewModal(item);
    };

    div.querySelector(".delete-scan-btn").onclick = (e) => {
      e.stopPropagation();
      deleteHistoryItem(idx);
    };

    feed.appendChild(div);
  });
  lucide.createIcons();
}

/* -------------------------------------------------------------
 * 8. Farmer Profile Page Logic
 * ------------------------------------------------------------- */
async function renderProfileStats() {
  if (!currentUser) return;

  const nameElem = document.getElementById("profile-full-name");
  const usernameElem = document.getElementById("profile-username");
  const emailElem = document.getElementById("profile-email-val");
  const scansCountElem = document.getElementById("profile-stat-scans");
  const listingsCountElem = document.getElementById("profile-stat-listings");
  const logoutBtn = document.getElementById("profile-logout-btn");

  if (nameElem) nameElem.textContent = currentUser.full_name || currentUser.username;
  if (usernameElem) usernameElem.textContent = `@${currentUser.username}`;
  if (emailElem) emailElem.textContent = currentUser.email || "-";

  // Total Scans Count from User-Scoped LocalStorage
  let history = JSON.parse(localStorage.getItem(getHistoryStorageKey()) || "[]");
  if (scansCountElem) scansCountElem.textContent = history.length;

  // Total Listings Count from Backend API
  try {
    const res = await fetch(`${API_BASE}/api/marketplace/my-listings`, {
      headers: getAuthHeaders()
    });
    if (res.ok) {
      const myListings = await res.json();
      if (listingsCountElem) listingsCountElem.textContent = myListings.length;
    }
  } catch (e) {
    console.warn("Failed to fetch my listings count:", e);
  }

  if (logoutBtn) {
    logoutBtn.onclick = async () => {
      await performUserLogout();
    };
  }
}

/* -------------------------------------------------------------
 * 9. Language Toggle (English <-> Kannada) & Voice STT Input
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
  if (document.getElementById("txt-chat-welcome")) {
    document.getElementById("txt-chat-welcome").textContent = t.chatWelcome;
  }
  document.getElementById("txt-btn-select-img").textContent = t.btnSelectImg;
  if (document.getElementById("txt-btn-new-chat")) {
    document.getElementById("txt-btn-new-chat").textContent = t.btnNewChat;
  }
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

  // Auth Page & Modal
  document.getElementById("txt-auth-page-title").textContent = t.authPageTitle;
  document.getElementById("txt-auth-page-sub").textContent = t.authPageSub;
  document.getElementById("txt-page-tab-login").textContent = t.tabLogin;
  document.getElementById("txt-page-tab-register").textContent = t.tabRegister;
  document.getElementById("lbl-page-login-user").textContent = t.lblLoginUser;
  document.getElementById("lbl-page-login-pass").textContent = t.lblLoginPass;
  document.getElementById("txt-btn-page-login").textContent = t.btnSubmitLogin;
  document.getElementById("lbl-page-reg-fullname").textContent = t.lblRegFullname;
  document.getElementById("lbl-page-reg-email").textContent = t.lblRegEmail;
  document.getElementById("lbl-page-reg-username").textContent = t.lblRegUsername;
  document.getElementById("lbl-page-reg-pass").textContent = t.lblRegPass;
  document.getElementById("txt-btn-page-register").textContent = t.btnSubmitRegister;

  document.getElementById("txt-auth-modal-title").textContent = t.authTitleLogin;
  document.getElementById("txt-tab-login").textContent = t.tabLogin;
  document.getElementById("txt-tab-register").textContent = t.tabRegister;
  document.getElementById("lbl-login-user").textContent = t.lblLoginUser;
  document.getElementById("lbl-login-pass").textContent = t.lblLoginPass;
  document.getElementById("txt-btn-submit-login").textContent = t.tabLogin;
  document.getElementById("lbl-reg-fullname").textContent = t.lblRegFullname;
  document.getElementById("lbl-reg-email").textContent = t.lblRegEmail;
  document.getElementById("lbl-reg-username").textContent = t.lblRegUsername;
  document.getElementById("lbl-reg-pass").textContent = t.lblRegPass;
  document.getElementById("txt-btn-submit-register").textContent = t.tabRegister;

  // Toast
  document.getElementById("txt-btn-undo").textContent = t.btnUndo;

  // Marketplace screen & Dual Price Controls
  document.getElementById("txt-market-title").textContent = t.marketTitle;
  document.getElementById("txt-market-sub").textContent = t.marketSub;
  document.getElementById("txt-btn-sell").textContent = t.btnSell;
  document.getElementById("market-search-input").placeholder = t.marketSearchPlaceholder;
  if (document.getElementById("lbl-price-range-title")) document.getElementById("lbl-price-range-title").textContent = t.lblPriceRangeTitle;
  if (document.getElementById("lbl-min-price")) document.getElementById("lbl-min-price").textContent = t.lblMinPrice;
  if (document.getElementById("lbl-max-price")) document.getElementById("lbl-max-price").textContent = t.lblMaxPrice;
  if (document.getElementById("lbl-min-slider")) document.getElementById("lbl-min-slider").textContent = t.lblMinSlider;
  if (document.getElementById("lbl-max-slider")) document.getElementById("lbl-max-slider").textContent = t.lblMaxSlider;
  if (document.getElementById("txt-market-tab-all")) document.getElementById("txt-market-tab-all").textContent = t.marketTabAll;
  if (document.getElementById("txt-market-tab-mine")) document.getElementById("txt-market-tab-mine").textContent = t.marketTabMine;

  const minSlider = document.getElementById("market-min-slider");
  const maxSlider = document.getElementById("market-max-slider");
  const badge = document.getElementById("market-price-range-badge");
  if (minSlider && maxSlider && badge) {
    badge.textContent = `₹${minSlider.value} - ₹${maxSlider.value}/${currentLang === "kn" ? "ಕೆಜಿ" : "kg"}`;
  }

  // History screen
  document.getElementById("txt-history-title").textContent = t.historyTitle;
  document.getElementById("txt-history-sub").textContent = t.historySub;
  if (document.getElementById("txt-btn-clear-history")) {
    document.getElementById("txt-btn-clear-history").textContent = t.btnClearHistory;
  }

  // Profile screen
  if (document.getElementById("txt-profile-title")) document.getElementById("txt-profile-title").textContent = t.profileTitle;
  if (document.getElementById("txt-profile-sub")) document.getElementById("txt-profile-sub").textContent = t.profileSub;
  if (document.getElementById("txt-stat-scans-lbl")) document.getElementById("txt-stat-scans-lbl").textContent = t.statScansLbl;
  if (document.getElementById("txt-stat-listings-lbl")) document.getElementById("txt-stat-listings-lbl").textContent = t.statListingsLbl;
  if (document.getElementById("lbl-profile-email")) document.getElementById("lbl-profile-email").textContent = t.lblProfileEmail;
  if (document.getElementById("lbl-profile-status")) document.getElementById("lbl-profile-status").textContent = t.lblProfileStatus;
  if (document.getElementById("txt-profile-logout")) document.getElementById("txt-profile-logout").textContent = t.profileLogout;

  // Bottom Navigation Labels
  document.getElementById("nav-scanner-lbl").textContent = t.navScanner;
  document.getElementById("nav-chat-lbl").textContent = t.navChat;
  document.getElementById("nav-market-lbl").textContent = t.navMarket;
  document.getElementById("nav-history-lbl").textContent = t.navHistory;
  if (document.getElementById("nav-profile-lbl")) document.getElementById("nav-profile-lbl").textContent = t.navProfile;

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
  updateAuthProfileBar();
  lucide.createIcons();

  if (currentDiagnosisData) {
    renderDiagnosisResults(currentDiagnosisData);
  }
  fetchMarketplaceListings();
  renderHistoryFeed();
  renderProfileStats();
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
