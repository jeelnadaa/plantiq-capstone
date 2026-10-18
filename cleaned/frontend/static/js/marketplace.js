// Marketplace Module (With Tabs, Inline Estate GPS, Multi-Photo Upload & Captions)
let allListings = [];
let activeMarketTab = "all"; // 'all' or 'mine'
let uploadedListingPhotos = []; // [{url: 'base64...', caption: '...'}]

function initMarketplace() {
  const tabAll = document.getElementById("tab-market-all");
  const tabMine = document.getElementById("tab-market-mine");
  const searchInput = document.getElementById("market-search-input");
  const minSlider = document.getElementById("price-min-slider");
  const maxSlider = document.getElementById("price-max-slider");
  const minInput = document.getElementById("price-min-input");
  const maxInput = document.getElementById("price-max-input");
  const btnSellModal = document.getElementById("btn-open-sell-modal");
  const sellModal = document.getElementById("sell-crop-modal");
  const closeSellBtn = document.getElementById("btn-close-sell-modal");
  const sellForm = document.getElementById("sell-crop-form");

  // Tab switcher
  if (tabAll && tabMine) {
    tabAll.onclick = () => {
      activeMarketTab = "all";
      tabAll.classList.add("active");
      tabMine.classList.remove("active");
      filterAndRenderListings();
    };

    tabMine.onclick = () => {
      activeMarketTab = "mine";
      tabMine.classList.add("active");
      tabAll.classList.remove("active");
      filterAndRenderListings();
    };
  }

  if (searchInput) {
    let debounce = null;
    searchInput.oninput = () => {
      clearTimeout(debounce);
      debounce = setTimeout(() => filterAndRenderListings(), 200);
    };
  }

  // Price sliders sync
  function syncPrices(fromSlider = true) {
    if (fromSlider) {
      minInput.value = minSlider.value;
      maxInput.value = maxSlider.value;
    } else {
      minSlider.value = minInput.value;
      maxSlider.value = maxInput.value;
    }
    filterAndRenderListings();
  }

  if (minSlider && maxSlider && minInput && maxInput) {
    minSlider.oninput = () => syncPrices(true);
    maxSlider.oninput = () => syncPrices(true);
    minInput.oninput = () => syncPrices(false);
    maxInput.oninput = () => syncPrices(false);
  }

  // Modal setup
  if (btnSellModal && sellModal) {
    btnSellModal.onclick = () => {
      sellModal.classList.remove("hidden");
      initSellLocation();
    };
  }
  if (closeSellBtn && sellModal) {
    closeSellBtn.onclick = () => sellModal.classList.add("hidden");
  }

  // Multi-Photo Upload setup inside form
  initPhotoUploader();

  // Dynamic Unit Selectors (Custom Unit Toggles)
  const qtyUnitSelect = document.getElementById("sell-qty-unit-select");
  const qtyUnitCustom = document.getElementById("sell-qty-unit-custom");
  if (qtyUnitSelect && qtyUnitCustom) {
    qtyUnitSelect.onchange = () => {
      if (qtyUnitSelect.value === "custom") {
        qtyUnitCustom.classList.remove("hidden");
        qtyUnitCustom.focus();
      } else {
        qtyUnitCustom.classList.add("hidden");
      }
    };
  }

  const priceUnitSelect = document.getElementById("sell-price-unit-select");
  const priceUnitCustom = document.getElementById("sell-price-unit-custom");
  if (priceUnitSelect && priceUnitCustom) {
    priceUnitSelect.onchange = () => {
      if (priceUnitSelect.value === "custom") {
        priceUnitCustom.classList.remove("hidden");
        priceUnitCustom.focus();
      } else {
        priceUnitCustom.classList.add("hidden");
      }
    };
  }

  // Sell Form submission with Mandatory Field Validation & Custom Modal
  if (sellForm) {
    sellForm.onsubmit = async (e) => {
      e.preventDefault();

      // Clear previous error highlights
      document.querySelectorAll(".validation-error-highlight").forEach(el => {
        el.classList.remove("validation-error-highlight");
      });

      // Run strict mandatory field validation
      const validation = validateListingForm();
      if (!validation.valid) {
        showListingValidationModal(validation.issues);
        return;
      }

      const payload = validation.data;

      try {
        const res = await apiRequest("/api/marketplace/listings", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          sellModal.classList.add("hidden");
          sellForm.reset();
          uploadedListingPhotos = [];
          if (qtyUnitCustom) qtyUnitCustom.classList.add("hidden");
          if (priceUnitCustom) priceUnitCustom.classList.add("hidden");
          renderUploadedPhotosList();
          fetchListings();
        } else {
          const errData = await res.json().catch(() => ({}));
          const serverIssues = [];
          if (errData && errData.detail) {
            if (Array.isArray(errData.detail)) {
              errData.detail.forEach(d => {
                const fieldRaw = d.loc?.slice(-1)[0] || "field";
                const cleanMsg = d.msg || "Invalid value";
                serverIssues.push({
                  fieldId: `sell-${fieldRaw.replace('_kg', '').replace('_per_kg', '')}`,
                  fieldName: fieldRaw.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()),
                  icon: "alert-triangle",
                  whatToFill: cleanMsg,
                  whyRequired: "All marketplace fields are mandatory and strictly audited for quality and platform security."
                });
              });
            } else {
              serverIssues.push({
                fieldId: "sell-title",
                fieldName: "Marketplace Listing Error",
                icon: "alert-triangle",
                whatToFill: String(errData.detail),
                whyRequired: "The listing server requires complete and accurate harvest information before publishing."
              });
            }
          }
          if (serverIssues.length > 0) {
            showListingValidationModal(serverIssues);
          } else {
            showListingValidationModal([{
              fieldId: "sell-title",
              fieldName: "Listing Error",
              icon: "alert-triangle",
              whatToFill: "Please check all fields and submit again.",
              whyRequired: "Unable to publish listing due to a server response error."
            }]);
          }
        }
      } catch (err) {
        console.error("Listing create error:", err);
        showListingValidationModal([{
          fieldId: "sell-title",
          fieldName: "Connection Error",
          icon: "wifi-off",
          whatToFill: "Ensure your backend server is running and reachable.",
          whyRequired: "Cannot connect to the marketplace database server to publish your crop."
        }]);
      }
    };
  }

  fetchListings();
}

// Custom Validation Modal: Displays what to fill and why it cannot list the crop
function showListingValidationModal(issues) {
  const modal = document.getElementById("listing-validation-modal");
  const listEl = document.getElementById("listing-validation-issues-list");
  const btnClose = document.getElementById("btn-close-val-modal");
  const btnDismiss = document.getElementById("btn-dismiss-val-modal");
  const btnFix = document.getElementById("btn-fix-listing-validation");

  if (!modal || !listEl) return;

  const isKn = (typeof currentLang !== "undefined" && currentLang === "kn");

  listEl.innerHTML = issues.map((issue, idx) => {
    const title = isKn ? (issue.fieldNameKn || issue.fieldName) : issue.fieldName;
    const fill = isKn ? (issue.whatToFillKn || issue.whatToFill) : issue.whatToFill;
    const why = isKn ? (issue.whyRequiredKn || issue.whyRequired) : issue.whyRequired;
    const fillLbl = isKn ? "ತುಂಬಬೇಕಾದ ವಿವರ:" : "What to fill:";
    const whyLbl = isKn ? "ಏಕೆ ಕಡ್ಡಾಯವಾಗಿದೆ:" : "Why it's required:";

    return `
      <div class="validation-issue-card" data-target="${issue.fieldId || ''}" title="Click to fix this field">
        <div class="validation-issue-header">
          <i data-lucide="${issue.icon || 'alert-circle'}" style="width:16px; height:16px; flex-shrink:0;"></i>
          <span>${idx + 1}. ${title}</span>
        </div>
        <div class="validation-issue-fill">
          <strong style="color:var(--text-main); font-weight:700;">${fillLbl}</strong> ${fill}
        </div>
        <div class="validation-issue-why">
          <strong style="color:var(--primary); font-weight:700;">${whyLbl}</strong> ${why}
        </div>
      </div>
    `;
  }).join("");

  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Highlight all invalid fields with pulsing red border and attach one-time clear listeners
  issues.forEach(issue => {
    if (issue.fieldId) {
      const el = document.getElementById(issue.fieldId);
      if (el) {
        el.classList.add("validation-error-highlight");
        el.addEventListener("input", () => el.classList.remove("validation-error-highlight"), { once: true });
        el.addEventListener("change", () => el.classList.remove("validation-error-highlight"), { once: true });
      }
    }
  });

  function closeModal() {
    modal.classList.add("hidden");
  }

  function focusTargetField(targetId) {
    closeModal();
    if (!targetId) return;
    const el = document.getElementById(targetId);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      setTimeout(() => {
        el.focus();
        el.classList.add("validation-error-highlight");
      }, 250);
    }
  }

  // Clicking an individual card focuses that specific field
  listEl.querySelectorAll(".validation-issue-card").forEach(card => {
    card.onclick = () => {
      const targetId = card.getAttribute("data-target");
      focusTargetField(targetId);
    };
  });

  if (btnClose) btnClose.onclick = closeModal;
  if (btnDismiss) btnDismiss.onclick = closeModal;

  if (btnFix) {
    btnFix.onclick = () => {
      const firstTargetId = issues[0]?.fieldId;
      focusTargetField(firstTargetId);
    };
  }

  modal.classList.remove("hidden");
}

// Client-side Validation: Ensures no field is left optional
function validateListingForm() {
  const issues = [];
  const isKn = (typeof currentLang !== "undefined" && currentLang === "kn");

  // 1. Title (mandatory, min 3 chars)
  const titleEl = document.getElementById("sell-title");
  const titleVal = titleEl?.value?.trim() || "";
  if (!titleVal || titleVal.length < 3) {
    issues.push({
      fieldId: "sell-title",
      fieldName: "Crop Title",
      fieldNameKn: "ಬೆಳೆ ಹೆಸರು (ಶೀರ್ಷಿಕೆ)",
      icon: "file-text",
      whatToFill: "Enter a descriptive name for your coffee lot (at least 3 characters, e.g. 'Premium Washed Arabica A-Grade').",
      whatToFillKn: "ನಿಮ್ಮ ಕಾಫಿ ಬೆಳೆಗೆ ಸ್ಪಷ್ಟ ಹೆಸರನ್ನು ನಮೂದಿಸಿ (ಕನಿಷ್ಠ 3 ಅಕ್ಷರಗಳು, ಉದಾ: ಪ್ರೀಮಿಯಂ ಅರೇಬಿಕಾ).",
      whyRequired: "Buyers and roasters search listings by crop lot name. Without a descriptive title, buyers cannot find or evaluate your harvest in search results.",
      whyRequiredKn: "ಖರೀದಿದಾರರು ಬೆಳೆಯ ಹೆಸರು ಮತ್ತು ದರ್ಜೆಯ ಮೂಲಕ ಹುಡುಕುತ್ತಾರೆ. ಹೆಸರಿಲ್ಲದೆ ನಿಮ್ಮ ಬೆಳೆ ಹುಡುಕಾಟದಲ್ಲಿ ಕಾಣಿಸುವುದಿಲ್ಲ."
    });
  }

  // 2. Variety (mandatory, min 2 chars)
  const varietyEl = document.getElementById("sell-variety");
  const varietyVal = varietyEl?.value?.trim() || "";
  if (!varietyVal || varietyVal.length < 2) {
    issues.push({
      fieldId: "sell-variety",
      fieldName: "Crop Variety / Cultivar",
      fieldNameKn: "ಕಾಫಿ ತಳಿ (Variety)",
      icon: "sprout",
      whatToFill: "Specify the coffee cultivar (e.g. 'Arabica Sln 795', 'Robusta CXR', 'Chandragiri', 'Geisha').",
      whatToFillKn: "ಕಾಫಿ ತಳಿಯನ್ನು ನಮೂದಿಸಿ (ಉದಾ: ಅರೇಬಿಕಾ Sln 795, ರೋಬಸ್ಟಾ CXR, ಚಂದ್ರಗಿರಿ).",
      whyRequired: "Roasters and exporters buy coffee based on cup profile and bean genetics. They cannot evaluate flavor profile or market pricing without the cultivar.",
      whyRequiredKn: "ರೋಸ್ಟರ್‌ಗಳು ಮತ್ತು ರಫ್ತುದಾರರು ಕಾಫಿಯ ರುಚಿ ಮತ್ತು ತಳಿಯ ಆಧಾರದ ಮೇಲೆ ಖರೀದಿಸುತ್ತಾರೆ. ತಳಿ ತಿಳಿಯದೆ ಬೆಲೆ ನಿಗದಿಪಡಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ."
    });
  }

  // 3. Harvest Quantity & Unit (mandatory, > 0)
  const qtyEl = document.getElementById("sell-qty");
  const qtyVal = parseFloat(qtyEl?.value);
  const qtySelect = document.getElementById("sell-qty-unit-select");
  const qtyCustom = document.getElementById("sell-qty-unit-custom");
  const isQtyCustom = (qtySelect?.value === "custom");
  const customQtyUnitVal = qtyCustom?.value?.trim() || "";

  if (isNaN(qtyVal) || qtyVal <= 0) {
    issues.push({
      fieldId: "sell-qty",
      fieldName: "Harvest Quantity",
      fieldNameKn: "ಬೆಳೆಯ ಪ್ರಮಾಣ (Quantity)",
      icon: "scale",
      whatToFill: "Enter available harvest amount strictly greater than 0 (e.g. 500, 20, 5).",
      whatToFillKn: "ಲಭ್ಯವಿರುವ ಬೆಳೆಯ ಪ್ರಮಾಣವನ್ನು 0 ಕ್ಕಿಂತ ಹೆಚ್ಚು ನಮೂದಿಸಿ (ಉದಾ: 500).",
      whyRequired: "Logistics partners and wholesale buyers require exact volume metrics to plan transport freight, warehouse capacity, and container contracts.",
      whyRequiredKn: "ಸಾಗಾಟ ಮತ್ತು ಗೋದಾಮು ವ್ಯವಸ್ಥೆಗೆ ನಿಖರವಾದ ತೂಕದ ಮಾಹಿತಿ ಕಡ್ಡಾಯವಾಗಿದೆ."
    });
  } else if (qtyVal > 100000) {
    issues.push({
      fieldId: "sell-qty",
      fieldName: "Harvest Quantity Exceeds Limit",
      fieldNameKn: "ಪ್ರಮಾಣದ ಮಿತಿ ಮೀರಿದೆ",
      icon: "scale",
      whatToFill: "Quantity cannot exceed 100,000 kg (100 metric tons) per single lot listing.",
      whatToFillKn: "ಒಂದು ಬಾರಿಗೆ 100,000 ಕೆಜಿ (100 ಮೆಟ್ರಿಕ್ ಟನ್) ಗಿಂತ ಹೆಚ್ಚು ಪಟ್ಟಿ ಮಾಡಲು ಸಾಧ್ಯವಿಲ್ಲ.",
      whyRequired: "Protects marketplace integrity against bulk spam entries and ensures manageable contract lot fulfillment.",
      whyRequiredKn: "ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ನಿಖರತೆ ಕಾಪಾಡಲು ಈ ಮಿತಿ ನಿಗದಿಪಡಿಸಲಾಗಿದೆ."
    });
  } else if (isQtyCustom && !customQtyUnitVal) {
    issues.push({
      fieldId: "sell-qty-unit-custom",
      fieldName: "Custom Quantity Unit",
      fieldNameKn: "ಗ್ರಾಹಕೀಯ ಘಟಕ (Custom Unit)",
      icon: "package",
      whatToFill: "Specify the custom packaging unit (e.g. '25 kg sack', '50 kg crate', 'bags').",
      whatToFillKn: "ನಿಮ್ಮ ಘಟಕದ ಹೆಸರನ್ನು ನಮೂದಿಸಿ (ಉದಾ: 25 ಕೆಜಿ ಚೀಲ, ಕ್ರೇಟ್).",
      whyRequired: "Custom quantity amounts must specify the packaging container so buyers understand the exact batch volume.",
      whyRequiredKn: "ಖರೀದಿದಾರರಿಗೆ ಪ್ಯಾಕೇಜಿಂಗ್ ಘಟಕ ಸ್ಪಷ್ಟವಾಗಿ ತಿಳಿಯಬೇಕಾಗಿದೆ."
    });
  }

  // 4. Selling Price & Pricing Unit (mandatory, > 0)
  const priceEl = document.getElementById("sell-price");
  const priceVal = parseFloat(priceEl?.value);
  const priceSelect = document.getElementById("sell-price-unit-select");
  const priceCustom = document.getElementById("sell-price-unit-custom");
  const isPriceCustom = (priceSelect?.value === "custom");
  const customPriceUnitVal = priceCustom?.value?.trim() || "";

  if (isNaN(priceVal) || priceVal <= 0) {
    issues.push({
      fieldId: "sell-price",
      fieldName: "Crop Price",
      fieldNameKn: "ಬೆಳೆಯ ಬೆಲೆ (Price)",
      icon: "indian-rupee",
      whatToFill: "Enter your asking price strictly greater than ₹0 (e.g. ₹420).",
      whatToFillKn: "ನಿಮ್ಮ ನಿರೀಕ್ಷಿತ ಬೆಲೆಯನ್ನು ₹0 ಕ್ಕಿಂತ ಹೆಚ್ಚು ನಮೂದಿಸಿ (ಉದಾ: ₹420).",
      whyRequired: "Mandatory for transparent marketplace commerce. Verified buyers cannot make purchase offers without upfront price transparency.",
      whyRequiredKn: "ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಪಾರದರ್ಶಕತೆಗಾಗಿ ಬೆಲೆ ನಮೂದಿಸುವುದು ಕಡ್ಡಾಯವಾಗಿದೆ."
    });
  } else if (isPriceCustom && !customPriceUnitVal) {
    issues.push({
      fieldId: "sell-price-unit-custom",
      fieldName: "Custom Pricing Unit",
      fieldNameKn: "ಗ್ರಾಹಕೀಯ ಬೆಲೆ ಘಟಕ (Custom Price Unit)",
      icon: "tag",
      whatToFill: "Specify the pricing terms (e.g. 'per 2 kg', 'per 5 ton', 'per box').",
      whatToFillKn: "ಬೆಲೆಯ ನಿಯಮಗಳನ್ನು ನಮೂದಿಸಿ (ಉದಾ: ಪ್ರತಿ 2 ಕೆಜಿ, ಪ್ರತಿ 5 ಟನ್).",
      whyRequired: "The pricing denominator is required to calculate the normalized ₹/kg rate for fair market comparisons.",
      whyRequiredKn: "ಪ್ರತಿ ಕೆಜಿ ದರವನ್ನು ಲೆಕ್ಕಹಾಕಿ ಹೋಲಿಕೆ ಮಾಡಲು ಘಟಕ ಅಗತ್ಯವಿದೆ."
    });
  }

  // 5. Farmer Name (mandatory, min 2 chars)
  const farmerEl = document.getElementById("sell-farmer");
  const farmerVal = farmerEl?.value?.trim() || "";
  if (!farmerVal || farmerVal.length < 2) {
    issues.push({
      fieldId: "sell-farmer",
      fieldName: "Farmer / Estate Owner Name",
      fieldNameKn: "ರೈತರ / ತೋಟದ ಮಾಲೀಕರ ಹೆಸರು",
      icon: "user",
      whatToFill: "Enter your full name or registered estate brand name (at least 2 characters).",
      whatToFillKn: "ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರು ಅಥವಾ ತೋಟದ ಹೆಸರನ್ನು ನಮೂದಿಸಿ (ಕನಿಷ್ಠ 2 ಅಕ್ಷರಗಳು).",
      whyRequired: "Direct farm-to-cup traceability builds buyer trust and verifies genuine agricultural producer identity.",
      whyRequiredKn: "ಖರೀದಿದಾರರಿಗೆ ವಿಶ್ವಾಸ ಮೂಡಿಸಲು ಮತ್ತು ಮಧ್ಯವರ್ತಿ ರಹಿತ ಸಂಪರ್ಕಕ್ಕೆ ಮಾಲೀಕರ ಹೆಸರು ಅಗತ್ಯವಿದೆ."
    });
  }

  // 6. Phone Number (mandatory, exact 10 digits)
  const phoneEl = document.getElementById("sell-phone");
  const rawPhone = phoneEl?.value?.trim() || "";
  const cleanPhone = rawPhone.replace(/\D/g, "");
  const finalPhone = (cleanPhone.length === 12 && cleanPhone.startsWith("91")) ? cleanPhone.slice(2) : cleanPhone;
  if (!finalPhone || !/^\d{10}$/.test(finalPhone)) {
    issues.push({
      fieldId: "sell-phone",
      fieldName: "Phone / WhatsApp Number",
      fieldNameKn: "ದೂರವಾಣಿ / ವಾಟ್ಸಾಪ್ ಸಂಖ್ಯೆ",
      icon: "phone",
      whatToFill: "Enter an exact 10-digit mobile number (e.g. 9876543210, without country code or special characters).",
      whatToFillKn: "ನಿಖರವಾಗಿ 10 ಅಂಕಿಯ ಮೊಬೈಲ್ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ (ಉದಾ: 9876543210).",
      whyRequired: "PlantIQ connects growers directly with buyers without middlemen. A verified 10-digit number is required for direct voice calls and WhatsApp deal closing.",
      whyRequiredKn: "ಖರೀದಿದಾರರು ನೇರವಾಗಿ ಕರೆ ಅಥವಾ ವಾಟ್ಸಾಪ್ ಮೂಲಕ ಸಂಪರ್ಕಿಸಲು 10 ಅಂಕಿಯ ಸಂಖ್ಯೆ ಕಡ್ಡಾಯವಾಗಿದೆ."
    });
  }

  // 7. Estate Address (mandatory, min 3 chars)
  const addressEl = document.getElementById("sell-address");
  const addressVal = addressEl?.value?.trim() || "";
  if (!addressVal || addressVal.length < 3) {
    issues.push({
      fieldId: "sell-address",
      fieldName: "Estate Address / Village",
      fieldNameKn: "ತೋಟದ ವಿಳಾಸ / ಊರು",
      icon: "map-pin",
      whatToFill: "Enter your estate village, taluk, or town (at least 3 characters, e.g. 'Aldur, Chikkamagaluru').",
      whatToFillKn: "ನಿಮ್ಮ ತೋಟದ ಊರು ಅಥವಾ ತಾಲೂಕನ್ನು ನಮೂದಿಸಿ (ಉದಾ: ಆಲ್ದೂರು, ಚಿಕ್ಕಮಗಳೂರು).",
      whyRequired: "Origin region dictates terroir and freight logistics. Buyers need your address to plan transport pickup and verify geographic origin.",
      whyRequiredKn: "ಕಾಫಿಯ ಮೂಲ ಪ್ರದೇಶ ತಿಳಿಯಲು ಮತ್ತು ಸಾಗಾಟ ವಾಹನ ಕಳುಹಿಸಲು ವಿಳಾಸ ಕಡ್ಡಾಯವಾಗಿದೆ."
    });
  }

  // 8. Estate GPS Coordinates (mandatory, valid coordinates)
  const latEl = document.getElementById("sell-lat");
  const lngEl = document.getElementById("sell-lng");
  let latVal = parseFloat(latEl?.value);
  let lngVal = parseFloat(lngEl?.value);
  if (isNaN(latVal) || isNaN(lngVal)) {
    if (window.LocationManager && LocationManager.coords.allowed && LocationManager.coords.lat && LocationManager.coords.lng) {
      latVal = LocationManager.coords.lat;
      lngVal = LocationManager.coords.lng;
    }
  }
  const hasValidCoords = (!isNaN(latVal) && !isNaN(lngVal) && latVal >= -90 && latVal <= 90 && lngVal >= -180 && lngVal <= 180 && (latVal !== 0 || lngVal !== 0));
  if (!hasValidCoords) {
    issues.push({
      fieldId: "btn-sell-gps",
      fieldName: "Estate GPS / Coordinates",
      fieldNameKn: "ತೋಟದ ಜಿಪಿಎಸ್ ಸ್ಥಳ",
      icon: "crosshair",
      whatToFill: "Click 'Auto GPS' to fetch device location, or click 'Manual Entry' to enter your latitude and longitude.",
      whatToFillKn: "'Auto GPS' ಕ್ಲಿಕ್ ಮಾಡಿ ಅಥವಾ 'Manual Entry' ಮೂಲಕ ಅಕ್ಷಾಂಶ-ರೇಖಾಂಶ ನಮೂದಿಸಿ.",
      whyRequired: "Required to place your coffee plantation on the interactive buyer discovery map, allowing nearby roasters to locate you.",
      whyRequiredKn: "ಖರೀದಿದಾರರ ಮ್ಯಾಪ್‌ನಲ್ಲಿ ನಿಮ್ಮ ತೋಟ ಕಾಣಿಸಲು ಜಿಪಿಎಸ್ ನಿರ್ದೇಶಾಂಕಗಳು ಅಗತ್ಯವಿದೆ."
    });
  }

  return {
    valid: issues.length === 0,
    issues,
    data: {
      title: titleVal,
      variety: varietyVal,
      quantity: qtyVal,
      quantity_unit: isQtyCustom ? customQtyUnitVal : (qtySelect?.value || "kg"),
      price: priceVal,
      price_unit: isPriceCustom ? customPriceUnitVal : (priceSelect?.value || "per kg"),
      farmer_name: farmerVal,
      phone_number: finalPhone,
      address: addressVal,
      latitude: hasValidCoords ? latVal : null,
      longitude: hasValidCoords ? lngVal : null,
      photos: uploadedListingPhotos || []
    }
  };
}

// Inline Location in Sell Form
function initSellLocation() {
  const btnGps = document.getElementById("btn-sell-gps");
  const btnManual = document.getElementById("btn-sell-manual");
  const manualBox = document.getElementById("sell-manual-latlng-box");
  const latInput = document.getElementById("sell-lat");
  const lngInput = document.getElementById("sell-lng");
  const statusEl = document.getElementById("sell-loc-status-text");

  if (!btnGps || !btnManual) return;

  function updateStatus(mode, lat, lng) {
    const modeStr = mode === "gps"
      ? (currentLang === "kn" ? "(ಸ್ವಯಂಚಾಲಿತ ಜಿಪಿಎಸ್)" : "(Auto GPS)")
      : (currentLang === "kn" ? "(ಹಸ್ತಚಾಲಿತ)" : "(Manual)");
    if (statusEl) statusEl.textContent = `${lat.toFixed(4)}, ${lng.toFixed(4)} ${modeStr}`;
  }

  btnGps.onclick = () => {
    btnGps.className = "btn btn-sm btn-primary";
    btnManual.className = "btn btn-sm btn-secondary";
    if (manualBox) manualBox.classList.add("hidden");
    if ("geolocation" in navigator) {
      if (statusEl) statusEl.textContent = currentLang === "kn" ? "ಜಿಪಿಎಸ್ ಪಡೆಯಲಾಗುತ್ತಿದೆ..." : "Acquiring GPS...";
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          if (latInput) latInput.value = pos.coords.latitude.toFixed(4);
          if (lngInput) lngInput.value = pos.coords.longitude.toFixed(4);
          updateStatus("gps", pos.coords.latitude, pos.coords.longitude);
        },
        () => {
          if (latInput) latInput.value = LocationManager.coords.lat.toFixed(4);
          if (lngInput) lngInput.value = LocationManager.coords.lng.toFixed(4);
          updateStatus("gps", LocationManager.coords.lat, LocationManager.coords.lng);
        }
      );
    }
  };

  btnManual.onclick = () => {
    btnGps.className = "btn btn-sm btn-secondary";
    btnManual.className = "btn btn-sm btn-primary";
    if (manualBox) manualBox.classList.remove("hidden");
    if (latInput && !latInput.value) latInput.value = LocationManager.coords.lat.toFixed(4);
    if (lngInput && !lngInput.value) lngInput.value = LocationManager.coords.lng.toFixed(4);
    updateStatus("manual", parseFloat(latInput.value), parseFloat(lngInput.value));
  };

  if (latInput && lngInput) {
    latInput.oninput = () => updateStatus("manual", parseFloat(latInput.value || 0), parseFloat(lngInput.value || 0));
    lngInput.oninput = () => updateStatus("manual", parseFloat(latInput.value || 0), parseFloat(lngInput.value || 0));
  }

  // Pre-fill default
  if (latInput) latInput.value = LocationManager.coords.lat.toFixed(4);
  if (lngInput) lngInput.value = LocationManager.coords.lng.toFixed(4);
  updateStatus("gps", LocationManager.coords.lat, LocationManager.coords.lng);
}

// Multi-Photo Upload & Individual Descriptions
function initPhotoUploader() {
  const uploadDrop = document.getElementById("sell-photo-dropzone");
  const photoInput = document.getElementById("sell-photo-input");

  if (!uploadDrop || !photoInput) return;

  uploadDrop.onclick = () => photoInput.click();

  photoInput.onchange = (e) => {
    const files = Array.from(e.target.files || []);
    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = (ev) => {
        uploadedListingPhotos.push({
          url: ev.target.result,
          caption: ""
        });
        renderUploadedPhotosList();
      };
      reader.readAsDataURL(file);
    });
    photoInput.value = "";
  };
}

function renderUploadedPhotosList() {
  const listContainer = document.getElementById("sell-photos-preview-list");
  if (!listContainer) return;

  if (uploadedListingPhotos.length === 0) {
    listContainer.innerHTML = "";
    return;
  }

  listContainer.innerHTML = uploadedListingPhotos.map((p, idx) => `
    <div class="photo-item-card">
      <img src="${p.url}" class="photo-item-thumb" alt="Photo ${idx+1}">
      <input type="text" class="form-control" style="flex:1; padding:6px 10px; font-size:0.78rem;" 
        placeholder="${t('photoCaptionPlaceholder')}" 
        value="${p.caption || ''}" 
        oninput="updatePhotoCaption(${idx}, this.value)">
      <button type="button" class="btn-icon" style="width:28px; height:28px; color:var(--danger);" onclick="removeUploadedPhoto(${idx})">
        <i data-lucide="trash-2" style="width:14px; height:14px;"></i>
      </button>
    </div>
  `).join("");

  if (window.lucide) lucide.createIcons();
}

function updatePhotoCaption(idx, val) {
  if (uploadedListingPhotos[idx]) {
    uploadedListingPhotos[idx].caption = val;
  }
}

function removeUploadedPhoto(idx) {
  uploadedListingPhotos.splice(idx, 1);
  renderUploadedPhotosList();
}

window.updatePhotoCaption = updatePhotoCaption;
window.removeUploadedPhoto = removeUploadedPhoto;

async function fetchListings() {
  try {
    const res = await apiRequest("/api/marketplace/listings");
    if (res.ok) {
      allListings = await res.json();
      filterAndRenderListings();
    }
  } catch(e){}
}

function filterAndRenderListings() {
  const container = document.getElementById("marketplace-listings-container");
  if (!container) return;

  const query = (document.getElementById("market-search-input")?.value || "").toLowerCase().trim();
  const minP = parseFloat(document.getElementById("price-min-input")?.value || 0);
  const maxP = parseFloat(document.getElementById("price-max-input")?.value || 1000);

  const filtered = allListings.filter(item => {
    if (activeMarketTab === "mine" && !item.is_owner) return false;
    const matchSearch = !query || 
      item.title.toLowerCase().includes(query) ||
      item.variety.toLowerCase().includes(query) ||
      item.address.toLowerCase().includes(query) ||
      item.farmer_name.toLowerCase().includes(query);
    const matchPrice = item.price_per_kg >= minP && item.price_per_kg <= maxP;
    return matchSearch && matchPrice;
  });

  if (filtered.length === 0) {
    const emptyMsg = activeMarketTab === "mine" ? t("noMyListings") : "No crop listings match your filter.";
    container.innerHTML = `<div class="card" style="text-align:center; padding: 28px 16px; color: var(--text-muted);">${emptyMsg}</div>`;
    return;
  }

  container.innerHTML = filtered.map(item => renderListingCard(item)).join("");
  if (window.lucide) lucide.createIcons();
}

function renderListingCard(item) {
  const photos = item.photos || [];
  let galleryHTML = "";

  if (photos.length > 0) {
    const firstPhoto = photos[0];
    const hasThumbs = photos.length > 1;

    galleryHTML = `
      <div class="listing-gallery" id="gallery-${item.id}">
        <div class="gallery-hero-wrapper">
          <img src="${firstPhoto.url}" class="gallery-hero-img" id="hero-img-${item.id}" alt="${item.title}">
          <div class="gallery-caption-overlay" id="hero-cap-${item.id}" style="${firstPhoto.caption ? '' : 'display:none;'}">
            ${firstPhoto.caption || ''}
          </div>
        </div>
        ${hasThumbs ? `
          <div class="gallery-thumbs-row">
            ${photos.map((p, pIdx) => `
              <div class="gallery-thumb-item ${pIdx === 0 ? 'active' : ''}" onclick="selectListingPhoto(${item.id}, ${pIdx})">
                <img src="${p.url}" alt="Thumb ${pIdx+1}">
              </div>
            `).join('')}
          </div>
        ` : ''}
      </div>
    `;
  }

    const qtyVal = item.quantity != null ? item.quantity : item.quantity_kg;
    const qtyUnit = item.quantity_unit || 'kg';
    const qtyDisplay = `${qtyVal} ${qtyUnit}`;

    const priceVal = item.price != null ? item.price : item.price_per_kg;
    let pUnit = item.price_unit || '/kg';
    if (!pUnit.startsWith('/') && !pUnit.startsWith('per')) {
      pUnit = '/' + pUnit;
    }
    const priceDisplay = `₹${priceVal} ${pUnit}`;
    const showApproxPerKg = (pUnit !== '/kg' && pUnit !== '/ kg' && pUnit !== 'per kg') && item.price_per_kg > 0;

    return `
      <div class="listing-card">
        ${galleryHTML}
        <div class="listing-header">
          <div>
            <div class="listing-title">${item.title}</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">${item.variety} • ${qtyDisplay}</div>
          </div>
          <div class="listing-price" style="text-align:right;">
            <div>${priceDisplay}</div>
            ${showApproxPerKg ? `<div style="font-size:0.68rem; font-weight:normal; color:var(--text-muted);">(≈ ₹${item.price_per_kg.toFixed(1)}/kg)</div>` : ''}
          </div>
        </div>
        <div class="listing-meta">
          <span>📍 ${item.address}</span>
          <span>👨‍🌾 ${item.farmer_name}</span>
        </div>

      <div class="listing-actions">
        <button type="button" onclick="openExternalApp('tel:${item.phone_number}')" class="btn btn-sm btn-secondary" style="flex:1;"><i data-lucide="phone"></i> ${t("btnContactPhone")}</button>
        <button type="button" onclick="openExternalApp('https://wa.me/${item.phone_number.replace(/[^0-9]/g, '')}?text=Hi%20${encodeURIComponent(item.farmer_name)},%20I%20saw%20your%20listing%20on%20PlantIQ%20for%20${encodeURIComponent(item.title)}')" class="btn btn-sm btn-primary" style="flex:1; background:#25D366; box-shadow:none;"><i data-lucide="message-circle"></i> ${t("btnContactWhatsapp")}</button>
        ${item.google_maps_url ? `<button type="button" onclick="openExternalApp('${item.google_maps_url}')" class="btn btn-sm btn-outline"><i data-lucide="map-pin"></i> ${t("btnNavMaps")}</button>` : ''}
        ${item.is_owner ? `<button onclick="deleteListing(${item.id})" class="btn btn-sm btn-outline" style="color:var(--danger); border-color:var(--danger);"><i data-lucide="trash-2"></i></button>` : ''}
      </div>
    </div>
  `;
}

function selectListingPhoto(listingId, photoIndex) {
  const item = allListings.find(l => l.id === listingId);
  if (!item || !item.photos || !item.photos[photoIndex]) return;

  const p = item.photos[photoIndex];
  const heroImg = document.getElementById(`hero-img-${listingId}`);
  const heroCap = document.getElementById(`hero-cap-${listingId}`);
  const galleryEl = document.getElementById(`gallery-${listingId}`);

  if (heroImg) heroImg.src = p.url;
  if (heroCap) {
    if (p.caption) {
      heroCap.textContent = p.caption;
      heroCap.style.display = "block";
    } else {
      heroCap.style.display = "none";
    }
  }

  if (galleryEl) {
    galleryEl.querySelectorAll(".gallery-thumb-item").forEach((thumb, idx) => {
      if (idx === photoIndex) thumb.classList.add("active");
      else thumb.classList.remove("active");
    });
  }
}

window.selectListingPhoto = selectListingPhoto;

async function deleteListing(id) {
  if (!confirm(currentLang === "kn" ? "ಈ ಪ್ರಕಟಣೆಯನ್ನು ಅಳಿಸಲು ನೀವು ಖಚಿತವಾಗಿ ಬಯಸುವಿರಾ?" : "Are you sure you want to delete this listing?")) return;
  try {
    const res = await apiRequest(`/api/marketplace/listings/${id}`, { method: "DELETE" });
    if (res.ok) {
      fetchListings();
    }
  } catch(e){}
}

window.deleteListing = deleteListing;
window.filterAndRenderListings = filterAndRenderListings;
document.addEventListener("DOMContentLoaded", () => initMarketplace());
