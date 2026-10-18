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

  // Sell Form submission
  if (sellForm) {
    sellForm.onsubmit = async (e) => {
      e.preventDefault();

      // Phone number strict 10-digit regex check
      const rawPhone = document.getElementById("sell-phone")?.value?.trim() || "";
      const cleanPhone = rawPhone.replace(/\D/g, "");
      const finalPhone = (cleanPhone.length === 12 && cleanPhone.startsWith("91")) ? cleanPhone.slice(2) : cleanPhone;
      if (!/^\d{10}$/.test(finalPhone)) {
        alert("Phone number must contain exactly 10 digits (e.g. 9876543210).");
        document.getElementById("sell-phone")?.focus();
        return;
      }

      // Quantity & Pricing Units Resolution
      let selectedQtyUnit = qtyUnitSelect?.value || "kg";
      if (selectedQtyUnit === "custom") {
        selectedQtyUnit = qtyUnitCustom?.value?.trim() || "kg";
      }

      let selectedPriceUnit = priceUnitSelect?.value || "per kg";
      if (selectedPriceUnit === "custom") {
        selectedPriceUnit = priceUnitCustom?.value?.trim() || "per kg";
      }

      const latVal = parseFloat(document.getElementById("sell-lat")?.value);
      const lngVal = parseFloat(document.getElementById("sell-lng")?.value);
      const qtyVal = parseFloat(document.getElementById("sell-qty")?.value);
      const priceVal = parseFloat(document.getElementById("sell-price")?.value);

      const payload = {
        title: document.getElementById("sell-title")?.value?.trim() || "Coffee Crop Lot",
        variety: document.getElementById("sell-variety")?.value?.trim() || "Arabica",
        quantity: !isNaN(qtyVal) ? qtyVal : 100.0,
        quantity_unit: selectedQtyUnit,
        price: !isNaN(priceVal) ? priceVal : 0.0,
        price_unit: selectedPriceUnit,
        farmer_name: document.getElementById("sell-farmer")?.value?.trim() || "Coffee Grower",
        phone_number: finalPhone,
        address: document.getElementById("sell-address")?.value?.trim() || "Karnataka, India",
        latitude: !isNaN(latVal) ? latVal : (window.LocationManager && LocationManager.coords.allowed ? LocationManager.coords.lat : null),
        longitude: !isNaN(lngVal) ? lngVal : (window.LocationManager && LocationManager.coords.allowed ? LocationManager.coords.lng : null),
        photos: uploadedListingPhotos || []
      };

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
          let errMsg = "Failed to publish listing.";
          if (errData && errData.detail) {
            if (Array.isArray(errData.detail)) {
              errMsg += " " + errData.detail.map(d => `${d.loc?.slice(-1)[0] || 'field'}: ${d.msg}`).join(", ");
            } else {
              errMsg += " " + errData.detail;
            }
          }
          alert(errMsg);
        }
      } catch (err) {
        console.error("Listing create error:", err);
      }
    };

  }

  fetchListings();
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
