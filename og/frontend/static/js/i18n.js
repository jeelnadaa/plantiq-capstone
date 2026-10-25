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
    envCardTitle: "Live Microclimate & Disease Risk",
    envRefresh: "Refresh Weather",
    envTemp: "Temperature",
    envFeels: "Feels Like",
    envHumidity: "Humidity",
    envRainfall: "24h Rainfall",
    envElevation: "Elevation",
    envWind: "Wind Speed",
    envRiskHigh: "HIGH INFECTION RISK",
    envRiskMod: "MODERATE RISK",
    envRiskLow: "LOW INFECTION RISK",
    envLoading: "Loading live site environmental data...",
    notAvailable: "Not Available",
    envLoadingBadge: "LOADING",
    envUnavailableMsg: "Live microclimate sensor data unavailable.",
    envRiskHighBadge: "HIGH RISK",
    envRiskHighText: "High Infection Risk: Sustained humidity favors Coffee Leaf Rust spore germination!",
    envRiskModBadge: "MODERATE",
    envRiskModText: "Moderate Risk: Monitor canopy spore activity and wet leaf duration.",
    envRiskLowBadge: "LOW RISK",
    envRiskLowText: "Favorable Weather: Ideal window for foliar nourishment and spraying.",
    locGpsAcquiring: "Acquiring GPS...",
    locAutoGpsLabel: "(Auto GPS)",
    locManualLabel: "(Manual)",
    locPrefix: "Location",
    btnApplyCoords: "Apply Coordinates & Get Weather",
    btnChangeLoc: "Change",
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
    unitKg: "kg",
    unitTon: "ton",
    unitQuintal: "quintal",
    unitBag50: "bag (50kg)",
    unitBag60: "bag (60kg)",
    unitCustom: "Custom...",
    pricePerKg: "/ kg",
    pricePerTon: "/ ton",
    pricePerQuintal: "/ quintal",
    pricePer50Bag: "/ 50kg bag",
    pricePer60Bag: "/ 60kg bag",
    optUploadSub: "Take photo with camera or gallery",
    paletteModalTitle: "Neo-Brutalist Themes",
    paletteModalDesc: "Choose from 5 high-voltage dual-color palettes. Each theme is engineered with fluid transitions for both Light and Dark modes.",
    badgeActive: "ACTIVE",
    btnTapToSet: "TAP TO SET",
    diseaseClassMiner: "Leaf Miner",
    diseaseClassRust: "Coffee Leaf Rust",
    diseaseClassPhoma: "Phoma",
    diseaseClassHealthy: "Healthy",
    diseaseClassCercospora: "Cercospora",

    // Marketplace Form & Modals
    lblQuantityAndUnit: "Quantity & Unit",
    lblPriceAndUnit: "Price & Pricing Unit",
    promptSelectPhotos: "+ Click to select 1 or multiple photos",
    hintSelectPhotos: "Add lots, drying yards, parchment images",
    btnEditListing: "Edit",
    lblYourListingBadge: "Your Listing",
    editModalTitle: "Edit Coffee Crop Listing",
    btnUpdateListing: "Update Listing",
    toastListingUpdated: "Listing updated successfully!",
    toastListingDeleted: "Listing deleted successfully.",

    // Multi-Criteria Filters & Haversine Sorting
    lblSortBy: "Sort By",
    sortNearest: "📍 Nearest First (Haversine)",
    sortNewest: "⏱️ Newest First",
    sortPriceAsc: "💰 Price: Low to High",
    sortPriceDesc: "💎 Price: High to Low",
    sortQtyDesc: "⚖️ Quantity: Largest First",
    lblFilterDistance: "Max Distance",
    distAll: "🌐 Any Distance",
    dist15: "Within 15 km",
    dist30: "Within 30 km",
    dist60: "Within 60 km",
    dist120: "Within 120 km",
    lblFilterVariety: "Coffee Variety",
    optAllVarieties: "☕ All Varieties",
    lblFilterQty: "Min Harvest Lot",
    qtyAll: "📦 Any Quantity",
    qty50: "≥ 50 kg (Small Lots)",
    qty200: "≥ 200 kg (Commercial)",
    qty1000: "≥ 1,000 kg (1 Ton+ Bulk)",
    lblPhotosOnly: "📸 Photos Only",
    btnResetFilters: "Reset Filters",
    lblBuyerLocation: "Your Reference Location",
    btnRefreshGPS: "Update GPS",
    kmAway: "km away",
    coordsPending: "Location Pending",

    // Validation Modal
    valModalTitle: "Cannot List Crop Yet",
    valModalSubtitle: "Mandatory Information Missing",
    valModalIntro: "All listing fields are strictly mandatory. Verified buyers, roasters, and logistics partners need complete details to evaluate and make direct purchase offers for your harvest.",
    valEditModalTitle: "Cannot Update Listing Yet",
    valEditModalSubtitle: "Mandatory Information Missing or Invalid",
    valEditModalIntro: "All listing fields are strictly validated upon edit to maintain marketplace quality, fair buyer pricing, and verified origin traceability.",
    btnReviewAndFix: "Review & Complete Fields",
    btnDismiss: "Dismiss",

    // Delete Confirmation Modal
    deleteModalTitle: "Delete Crop Listing?",
    deleteModalSubtitle: "Irreversible Action",
    deleteModalMsg: "Are you sure you want to delete this listing? Once deleted, verified buyers will no longer be able to find your harvest lot or contact you about it.",
    btnConfirmDeleteListing: "Yes, Delete Listing",
    btnCancelDelete: "Cancel / Keep",

    // Server Settings & Themes
    serverModalTitle: "Backend Server Connection",
    serverModalDesc: "Connect your mobile app to your laptop or cloud server. If your Wi-Fi IP changes, simply update it below.",
    lblServerIp: "Server IP / URL",
    serverIpHint: "Enter your laptop's Wi-Fi IP (from ipconfig) with port 8000",
    btnTestPing: "Test Ping",
    btnSaveConnect: "Save & Connect",
    btnResetDefault: "Reset to Default",
    colorPaletteTitle: "Color Theme Palette",
    gmapsGuideModalTitle: "Google Maps Coordinates Guide",

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
    btnCancel: "Cancel",

    // Auth & Accounts
    authPageTitle: "Sign In / Register",
    authPageSubtitle: "Sign in or register to sync coffee disease diagnostics, estate lots, and CCRI advisories.",
    tabSignIn: "Sign In",
    tabRegister: "Register",
    lblUsernameOrEmail: "Username or Email",
    lblPassword: "Password",
    lblFullName: "Full Name",
    lblUsername: "Username",
    lblEmailAddress: "Email Address",
    btnSignIn: "Sign In",
    btnCreateAccount: "Create Account",
    placeholderUsernameOrEmail: "e.g. jeel_nada",
    placeholderFullName: "Your Name",
    placeholderUsername: "username",
    placeholderEmail: "farmer@example.com"
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
    envCardTitle: "ಲೈವ್ ಸೂಕ್ಷ್ಮ ವಾತಾವರಣ & ರೋಗದ ಅಪಾಯ",
    envRefresh: "ಹವಾಮಾನ ರಿಫ್ರೆಶ್",
    envTemp: "ತಾಪಮಾನ",
    envFeels: "ಅನುಭವ",
    envHumidity: "ಆರ್ದ್ರತೆ / ತೇವಾಂಶ",
    envRainfall: "24 ಗಂಟೆಗಳ ಮಳೆ",
    envElevation: "ಸಮುದ್ರ ಮಟ್ಟದಿಂದ ಎತ್ತರ",
    envWind: "ಗಾಳಿಯ ವೇಗ",
    envRiskHigh: "ಹೆಚ್ಚಿನ ರೋಗದ ಅಪಾಯ",
    envRiskMod: "ಮಧ್ಯಮ ಅಪಾಯ",
    envRiskLow: "ಕಡಿಮೆ ರೋಗದ ಅಪಾಯ",
    envLoading: "ವಾತಾವರಣದ ಲೈವ್ ಮಾಹಿತಿ ಪಡೆಯಲಾಗುತ್ತಿದೆ...",
    notAvailable: "ಲಭ್ಯವಿಲ್ಲ",
    envLoadingBadge: "ಲೋಡ್ ಆಗುತ್ತಿದೆ",
    envUnavailableMsg: "ಲೈವ್ ವಾತಾವರಣದ ಸೆನ್ಸರ್ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ.",
    envRiskHighBadge: "ಹೆಚ್ಚಿನ ಅಪಾಯ",
    envRiskHighText: "ಎಚ್ಚರಿಕೆ: ಹೆಚ್ಚಿನ ಆರ್ದ್ರತೆ - ಎಲೆ ತುಕ್ಕು ಶಿಲೀಂಧ್ರ ಹರಡುವಿಕೆ ಹೆಚ್ಚಾಗಬಹುದು!",
    envRiskModBadge: "ಮಧ್ಯಮ ಅಪಾಯ",
    envRiskModText: "ಮಧ್ಯಮ ಅಪಾಯ: ಎಲೆಯ ತೇವಾಂಶ ಮತ್ತು ನೆರಳಿನ ಸಾಂದ್ರತೆಯನ್ನು ಗಮನಿಸಿ.",
    envRiskLowBadge: "ಕಡಿಮೆ ಅಪಾಯ",
    envRiskLowText: "ಅನುಕೂಲಕರ ವಾತಾವರಣ: ಸಿಂಪರಣೆಗೆ ಮತ್ತು ಬೆಳೆ ಪೋಷಣೆಗೆ ಸೂಕ್ತ ಸಮಯ.",
    locGpsAcquiring: "ಜಿಪಿಎಸ್ ಪಡೆಯಲಾಗುತ್ತಿದೆ...",
    locAutoGpsLabel: "(ಸ್ವಯಂಚಾಲಿತ ಜಿಪಿಎಸ್)",
    locManualLabel: "(ಹಸ್ತಚಾಲಿತ)",
    locPrefix: "ಸ್ಥಳ",
    btnApplyCoords: "ನಿರ್ದೇಶಾಂಕಗಳನ್ನು ಅನ್ವಯಿಸಿ & ಹವಾಮಾನ ಪಡೆಯಿರಿ",
    btnChangeLoc: "ಬದಲಾಯಿಸಿ",
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
    noMyListings: "ನೀವು ಇನ್ನೂ ಯಾವುದೇ ಬೆಳೆ ಮಾರಾಟದ ಪ್ರಕಟಣೆಯನ್ನು ಹಾಕಿಲ್ಲ.",
    unitKg: "ಕೆಜಿ",
    unitTon: "ಟನ್",
    unitQuintal: "ಕ್ವಿಂಟಾಲ್",
    unitBag50: "ಚೀಲ (50ಕೆಜಿ)",
    unitBag60: "ಚೀಲ (60ಕೆಜಿ)",
    unitCustom: "ಗ್ರಾಹಕೀಯ...",
    pricePerKg: "/ ಕೆಜಿ",
    pricePerTon: "/ ಟನ್",
    pricePerQuintal: "/ ಕ್ವಿಂಟಾಲ್",
    pricePer50Bag: "/ 50ಕೆಜಿ ಚೀಲ",
    pricePer60Bag: "/ 60kg ಚೀಲ",
    optUploadSub: "ಕ್ಯಾಮೆರಾ ಅಥವಾ ಗ್ಯಾಲರಿಯಿಂದ ಫೋಟೋ ತೆಗೆದುಕೊಳ್ಳಿ",
    paletteModalTitle: "ಬಣ್ಣದ ಥೀಮ್ ಆಯ್ಕೆ",
    paletteModalDesc: "5 ಆಕರ್ಷಕ ಡ್ಯುಯಲ್ ಬಣ್ಣದ ಥೀಮ್‌ಗಳಿಂದ ಆಯ್ಕೆಮಾಡಿ. ಲೈಟ್ ಮತ್ತು ಡಾರ್ಕ್ ಮೋಡ್‌ಗಳೆರಡರಲ್ಲೂ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ.",
    badgeActive: "ಸಕ್ರಿಯ",
    btnTapToSet: "ಆಯ್ಕೆ ಮಾಡಲು ಟ್ಯಾಪ್ ಮಾಡಿ",
    diseaseClassMiner: "ಎಲೆ ಕೊರೆಯುವ ಕೀಟ (Leaf Miner)",
    diseaseClassRust: "ಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗ (Coffee Leaf Rust)",
    diseaseClassPhoma: "ಫೋಮಾ ರೋಗ (Phoma)",
    diseaseClassHealthy: "ಆರೋಗ್ಯಕರ ಎಲೆ (Healthy)",
    diseaseClassCercospora: "ಸರ್ಕೋಸ್ಪೊರಾ ಚುಕ್ಕೆ ರೋಗ (Cercospora)",
    // Marketplace Form & Modals
    lblQuantityAndUnit: "ಪ್ರಮಾಣ ಮತ್ತು ಘಟಕ",
    lblPriceAndUnit: "ದರ ಮತ್ತು ಘಟಕ",
    promptSelectPhotos: "+ 1 ಅಥವಾ ಹೆಚ್ಚಿನ ಫೋಟೋಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಲು ಕ್ಲಿಕ್ ಮಾಡಿ",
    hintSelectPhotos: "ಲಾಟ್‌ಗಳು, ಕಣದ ಫೋಟೋ, ಪಾರ್ಚ್‌ಮೆಂಟ್ ಚಿತ್ರಗಳನ್ನು ಸೇರಿಸಿ",
    btnEditListing: "ತಿದ್ದುಪಡಿ",
    lblYourListingBadge: "ನಿಮ್ಮ ಪ್ರಕಟಣೆ",
    editModalTitle: "ಕಾಫಿ ಬೆಳೆ ಪ್ರಕಟಣೆ ತಿದ್ದುಪಡಿ ಮಾಡಿ",
    btnUpdateListing: "ಪಟ್ಟಿಯನ್ನು ನವೀಕರಿಸಿ",
    toastListingUpdated: "ಬೆಳೆ ಪಟ್ಟಿಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ!",
    toastListingDeleted: "ಬೆಳೆ ಪಟ್ಟಿಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಅಳಿಸಲಾಗಿದೆ.",

    // Multi-Criteria Filters & Haversine Sorting
    lblSortBy: "ವಿಂಗಡಣೆ",
    sortNearest: "📍 ಹತ್ತಿರದ ಮೊದಲಿಗೆ (ಹ್ಯಾವರ್ಸಿನ್)",
    sortNewest: "⏱️ ಇತ್ತೀಚಿನದು",
    sortPriceAsc: "💰 ಬೆಲೆ: ಕಡಿಮೆಯಿಂದ ಹೆಚ್ಚಿಗೆ",
    sortPriceDesc: "💎 ಬೆಲೆ: ಹೆಚ್ಚಿನಿಂದ ಕಡಿಮೆಗೆ",
    sortQtyDesc: "⚖️ ಪ್ರಮಾಣ: ಹೆಚ್ಚಿನಿಂದ ಕಡಿಮೆಗೆ",
    lblFilterDistance: "ಗರಿಷ್ಠ ಅಂತರ",
    distAll: "🌐 ಯಾವುದೇ ಅಂತರ",
    dist15: "15 ಕಿ.ಮೀ ಒಳಗೆ",
    dist30: "30 ಕಿ.ಮೀ ಒಳಗೆ",
    dist60: "60 ಕಿ.ಮೀ ಒಳಗೆ",
    dist120: "120 ಕಿ.ಮೀ ಒಳಗೆ",
    lblFilterVariety: "ಕಾಫಿ ತಳಿ",
    optAllVarieties: "☕ ಎಲ್ಲಾ ತಳಿಗಳು",
    lblFilterQty: "ಕನಿಷ್ಠ ಕೊಯ್ಲು ಲಾಟ್",
    qtyAll: "📦 ಯಾವುದೇ ಪ್ರಮಾಣ",
    qty50: "≥ 50 ಕೆ.ಜಿ (ಸಣ್ಣ ಲಾಟ್)",
    qty200: "≥ 200 ಕೆ.ಜಿ (ವಾಣಿಜ್ಯ)",
    qty1000: "≥ 1,000 ಕೆ.ಜಿ (1 ಟನ್+ ಬೃಹತ್)",
    lblPhotosOnly: "📸 ಚಿತ್ರಗಳಿರುವ ಪಟ್ಟಿಗಳು ಮಾತ್ರ",
    btnResetFilters: "ಫಿಲ್ಟರ್ ರದ್ದುಮಾಡಿ",
    lblBuyerLocation: "ನಿಮ್ಮ ಉಲ್ಲೇಖಿತ ಸ್ಥಳ",
    btnRefreshGPS: "ಜಿಪಿಎಸ್ ಅಪ್‌ಡೇಟ್",
    kmAway: "ಕಿ.ಮೀ ದೂರ",
    coordsPending: "ಸ್ಥಳ ಬಾಕಿ ಇದೆ",

    // Validation Modal
    valModalTitle: "ಬೆಳೆ ಪಟ್ಟಿ ಮಾಡಲು ಸಾಧ್ಯವಿಲ್ಲ",
    valModalSubtitle: "ಕಡ್ಡಾಯ ಮಾಹಿತಿ ಅಗತ್ಯವಿದೆ",
    valModalIntro: "ಎಲ್ಲಾ ವಿವರಗಳನ್ನು ನಮೂದಿಸುವುದು ಕಡ್ಡಾಯವಾಗಿದೆ. ಪರಿಶೀಲಿಸಿದ ಖರೀದಿದಾರರು ಮತ್ತು ರಫ್ತುದಾರರು ನಿಮ್ಮ ಬೆಳೆಯನ್ನು ಖರೀದಿಸಲು ಸಂಪೂರ್ಣ ಮಾಹಿತಿ ಅಗತ್ಯ.",
    valEditModalTitle: "ಪ್ರಕಟಣೆ ತಿದ್ದುಪಡಿ ಮಾಡಲು ಸಾಧ್ಯವಿಲ್ಲ",
    valEditModalSubtitle: "ಕಡ್ಡಾಯ ಮಾಹಿತಿ ಅಗತ್ಯವಿದೆ ಅಥವಾ ತಪ್ಪಾಗಿದೆ",
    valEditModalIntro: "ಮಾರುಕಟ್ಟೆಯ ನಿಖರತೆ ಮತ್ತು ಗುಣಮಟ್ಟವನ್ನು ಕಾಪಾಡಲು ತಿದ್ದುಪಡಿ ಮಾಡುವಾಗಲೂ ಎಲ್ಲಾ ವಿವರಗಳನ್ನು ಕಡ್ಡಾಯವಾಗಿ ಪರಿಶೀಲಿಸಲಾಗುತ್ತದೆ. ದಯವಿಟ್ಟು ಸರಿಯಾದ ಮಾಹಿತಿ ನಮೂದಿಸಿ.",
    btnReviewAndFix: "ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಭರ್ತಿ ಮಾಡಿ",
    btnDismiss: "ರದ್ದುಮಾಡಿ",

    // Delete Confirmation Modal
    deleteModalTitle: "ಬೆಳೆ ಪಟ್ಟಿಯನ್ನು ಅಳಿಸುವುದೇ?",
    deleteModalSubtitle: "ಹಿಂಪಡೆಯಲಾಗದ ಕ್ರಿಯೆ",
    deleteModalMsg: "ನೀವು ಖಚಿತವಾಗಿ ಈ ಬೆಳೆ ಪಟ್ಟಿಯನ್ನು ಅಳಿಸಲು ಬಯಸುವಿರಾ? ಅಳಿಸಿದ ನಂತರ ಖರೀದಿದಾರರಿಗೆ ನಿಮ್ಮ ಬೆಳೆ ಇನ್ನು ಮುಂದೆ ಕಾಣಿಸುವುದಿಲ್ಲ.",
    btnConfirmDeleteListing: "ಹೌದು, ಪಟ್ಟಿಯನ್ನು ಅಳಿಸಿ",
    btnCancelDelete: "ರದ್ದುಮಾಡಿ / ಇರಿಸಿಕೊಳ್ಳಿ",

    // Server Settings & Themes
    serverModalTitle: "ಸರ್ವರ್ ಸಂಪರ್ಕ ಸಂಯೋಜನೆ",
    serverModalDesc: "ನಿಮ್ಮ ಮೊಬೈಲ್ ಅನ್ನು ಲ್ಯಾಪ್‌ಟಾಪ್ ಅಥವಾ ಕ್ಲೌಡ್ ಸರ್ವರ್‌ಗೆ ಸಂಪರ್ಕಿಸಿ. ನಿಮ್ಮ Wi-Fi IP ಬದಲಾದರೆ ಕೆಳಗೆ ಅಪ್‌ಡೇಟ್ ಮಾಡಿ.",
    lblServerIp: "ಸರ್ವರ್ ಐಪಿ / ವಿಳಾಸ",
    serverIpHint: "ನಿಮ್ಮ ಲ್ಯಾಪ್‌ಟಾಪ್‌ನ Wi-Fi IP (ಪೋರ್ಟ್ 8000 ನೊಂದಿಗೆ) ನಮೂದಿಸಿ",
    btnTestPing: "ಪಿಂಗ್ ಪರೀಕ್ಷಿಸಿ",
    btnSaveConnect: "ಉಳಿಸಿ ಮತ್ತು ಸಂಪರ್ಕಿಸಿ",
    btnResetDefault: "ಮೂಲ ಸ್ಥಿತಿಗೆ ಮರುಹೊಂದಿಸಿ",
    colorPaletteTitle: "ಬಣ್ಣದ ಥೀಮ್ ಆಯ್ಕೆ",
    gmapsGuideModalTitle: "ಗೂಗಲ್ ಮ್ಯಾಪ್ಸ್ ನಿರ್ದೇಶಾಂಕ ಮಾರ್ಗದರ್ಶಿ",

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
    btnCancel: "ರದ್ದುಗೊಳಿಸಿ",

    // Auth & Accounts
    authPageTitle: "ಸೈನ್ ಇನ್ / ನೋಂದಣಿ",
    authPageSubtitle: "ಕಾಫಿ ರೋಗ ಪರಿಶೋಧನೆಗಳು ಮತ್ತು ಮಾರುಕಟ್ಟೆ ವಿವರಗಳನ್ನು ಪಡೆಯಲು ಲಾಗಿನ್ ಮಾಡಿ ಅಥವಾ ನೋಂದಾಯಿಸಿ.",
    tabSignIn: "ಸೈನ್ ಇನ್",
    tabRegister: "ನೋಂದಾಯಿಸಿ",
    lblUsernameOrEmail: "ಬಳಕೆದಾರ ಹೆಸರು ಅಥವಾ ಇಮೇಲ್",
    lblPassword: "ಪಾಸ್‌ವರ್ಡ್",
    lblFullName: "ಪೂರ್ಣ ಹೆಸರು",
    lblUsername: "ಬಳಕೆದಾರ ಹೆಸರು",
    lblEmailAddress: "ಇಮೇಲ್ ವಿಳಾಸ",
    btnSignIn: "ಸೈನ್ ಇನ್",
    btnCreateAccount: "ಖಾತೆ ರಚಿಸಿ",
    placeholderUsernameOrEmail: "ಉದಾ: jeel_nada",
    placeholderFullName: "ನಿಮ್ಮ ಹೆಸರು",
    placeholderUsername: "ಬಳಕೆದಾರ ಹೆಸರು",
    placeholderEmail: "farmer@example.com"
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
      if (el.tagName === "INPUT" && (el.type === "button" || el.type === "submit")) {
        el.value = I18N_DICTIONARY[currentLang][key];
      } else {
        el.textContent = I18N_DICTIONARY[currentLang][key];
      }
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
  if (typeof window.refreshScannerUI === "function") {
    window.refreshScannerUI();
  }
  if (typeof renderHistoryPage === "function") {
    renderHistoryPage();
  }
  if (typeof filterAndRenderListings === "function") {
    filterAndRenderListings();
  }
}

function initI18n() {
  const langToggleBtn = document.getElementById("btn-lang-toggle");
  if (langToggleBtn) {
    langToggleBtn.onclick = () => {
      setLanguage(currentLang === "en" ? "kn" : "en");
    };
  }
  updateDOMTranslations();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initI18n);
} else {
  initI18n();
}
// Execute immediately as well
updateDOMTranslations();

