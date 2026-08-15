// Profile & History Module (With Diagnostic Report Modal & 3-Second Undo Toast)
let activeDetailScan = null;
let undoToastTimer = null;
let undoCountdownInterval = null;
let pendingDeletedData = null;

async function initProfile() {
  const scansCountEl = document.getElementById("stat-scans-count");
  const listingsCountEl = document.getElementById("stat-listings-count");
  const userFullnameEl = document.getElementById("profile-fullname");
  const userEmailEl = document.getElementById("profile-email");
  const btnLogout = document.getElementById("btn-logout");

  const history = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  if (scansCountEl) scansCountEl.textContent = history.length;

  const cachedUserStr = localStorage.getItem("plantiq_user");
  if (cachedUserStr) {
    try {
      const user = JSON.parse(cachedUserStr);
      if (userFullnameEl) userFullnameEl.textContent = user.full_name || user.username;
      if (userEmailEl) userEmailEl.textContent = user.email;
    } catch(e){}
  }

  try {
    const userRes = await apiRequest("/api/auth/me");
    if (userRes.ok) {
      const user = await userRes.json();
      localStorage.setItem("plantiq_user", JSON.stringify(user));
      if (userFullnameEl) userFullnameEl.textContent = user.full_name || user.username;
      if (userEmailEl) userEmailEl.textContent = user.email;
    }

    const listRes = await apiRequest("/api/marketplace/my-listings");
    if (listRes.ok) {
      const myListings = await listRes.json();
      if (listingsCountEl) listingsCountEl.textContent = myListings.length;
    }
  } catch(e){}

  if (btnLogout) {
    btnLogout.onclick = () => {
      clearAuthToken();
      window.location.replace("/auth");
    };
  }

  initHistoryEvents();
  renderHistoryPage();
}

function initHistoryEvents() {
  const btnClearAll = document.getElementById("btn-clear-all-history");
  const detailsModal = document.getElementById("scan-details-modal");
  const closeDetailsBtn = document.getElementById("btn-close-details-modal");
  const btnDetailsChat = document.getElementById("btn-details-ask-chat");
  const btnDetailsDelete = document.getElementById("btn-details-delete-scan");

  if (btnClearAll) {
    btnClearAll.onclick = () => handleClearAllHistory();
  }

  if (closeDetailsBtn && detailsModal) {
    closeDetailsBtn.onclick = () => detailsModal.classList.add("hidden");
  }

  if (btnDetailsDelete && detailsModal) {
    btnDetailsDelete.onclick = () => {
      if (activeDetailScan) {
        detailsModal.classList.add("hidden");
        deleteSingleScanWithUndo(activeDetailScan.id);
      }
    };
  }

  if (btnDetailsChat) {
    btnDetailsChat.onclick = () => {
      if (activeDetailScan) {
        sessionStorage.setItem("plantiq_handoff", JSON.stringify({
          disease: activeDetailScan.disease,
          confidence: activeDetailScan.confidence,
          advisory: activeDetailScan.advisory,
          imageName: activeDetailScan.disease || "History Leaf",
          imageDataUrl: activeDetailScan.image
        }));
        window.location.href = "/chat";
      }
    };
  }
}

function renderHistoryPage() {
  const container = document.getElementById("history-feed-container");
  const btnClearAll = document.getElementById("btn-clear-all-history");
  if (!container) return;

  const history = JSON.parse(localStorage.getItem("plantiq_history") || "[]");

  if (btnClearAll) {
    if (history.length > 0) btnClearAll.classList.remove("hidden");
    else btnClearAll.classList.add("hidden");
  }

  if (history.length === 0) {
    container.innerHTML = `<div class="card" style="text-align:center; padding: 28px; color: var(--text-muted);">${t("noScansFound")}</div>`;
    return;
  }

  container.innerHTML = history.map(item => `
    <div class="card" style="display:flex; gap:12px; align-items:center; margin-bottom:12px; cursor:pointer; padding:12px;" onclick="openScanDetails('${item.id}')">
      <img src="${item.image}" style="width:68px; height:68px; border-radius:10px; object-fit:cover; border:1px solid var(--border-subtle);">
      <div style="flex:1;">
        <strong style="font-size:0.95rem; color:var(--text-main); display:block; margin-bottom:2px;">${item.disease}</strong>
        <div style="font-size:0.75rem; color:var(--text-muted); margin-bottom:4px;">${item.date} • ${item.confidence ? Number(item.confidence).toFixed(1) : 95.0}% ${t("confidenceLabel")}</div>
        <span class="${item.is_healthy ? 'badge-healthy' : 'badge-disease'}">${item.is_healthy ? t("healthyLabel") : t("diseaseLabel")}</span>
      </div>
      <div style="display:flex; flex-direction:column; gap:6px; align-items:flex-end;">
        <button class="btn btn-sm btn-outline" style="padding:4px 8px; font-size:0.72rem;" onclick="event.stopPropagation(); openScanDetails('${item.id}')">
          <i data-lucide="eye" style="width:13px; height:13px;"></i>
        </button>
        <button class="btn-icon" style="width:28px; height:28px; color:var(--danger); border-color:var(--border-subtle);" onclick="event.stopPropagation(); deleteSingleScanWithUndo('${item.id}')" title="${t('btnDeleteScan')}">
          <i data-lucide="trash-2" style="width:14px; height:14px;"></i>
        </button>
      </div>
    </div>
  `).join("");

  if (window.lucide) lucide.createIcons();
}

function openScanDetails(scanId) {
  const history = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  const item = history.find(h => String(h.id) === String(scanId));
  if (!item) return;

  activeDetailScan = item;
  const modal = document.getElementById("scan-details-modal");
  const body = document.getElementById("scan-details-body");
  if (!modal || !body) return;

  let distHtml = "";
  if (item.distribution && Object.keys(item.distribution).length > 0) {
    distHtml = `
      <div style="margin:12px 0;">
        <strong style="font-size:0.78rem; color:var(--text-muted); display:block; margin-bottom:6px;">${t("classProbabilities")}</strong>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
          ${Object.entries(item.distribution).map(([cls, pct]) => `
            <div class="distribution-item"><span>${cls}</span><strong>${Number(pct).toFixed(1)}%</strong></div>
          `).join('')}
        </div>
      </div>
    `;
  }

  let envHtml = "";
  if (item.env_data && item.env_data.location_status !== "Disallowed / Unavailable") {
    envHtml = `
      <div style="margin:12px 0; background:var(--bg-card-subtle); padding:10px; border-radius:8px; border:1px solid var(--border-subtle);">
        <strong style="font-size:0.78rem; color:var(--primary); display:block; margin-bottom:6px;">📍 ${t("envConditions")}</strong>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:0.75rem;">
          ${Object.entries(item.env_data).map(([k, v]) => `
            <div><span style="color:var(--text-muted);">${k}:</span> <strong>${v}</strong></div>
          `).join('')}
        </div>
      </div>
    `;
  }

  const advisoryFormatted = typeof window.formatMarkdown === "function" 
    ? window.formatMarkdown(item.advisory || "Standard CCRI coffee agronomy advisory applied.") 
    : (item.advisory || "Standard CCRI coffee agronomy advisory applied.");

  body.innerHTML = `
    <div style="text-align:center; margin-bottom:12px;">
      <img src="${item.image}" style="max-width:100%; height:180px; object-fit:cover; border-radius:12px; border:1px solid var(--border-subtle); margin-bottom:8px;">
      <div style="display:flex; justify-content:center; gap:8px; align-items:center; margin-bottom:4px;">
        <span class="${item.is_healthy ? 'badge-healthy' : 'badge-disease'}">${item.is_healthy ? t("healthyLabel") : t("diseaseLabel")}</span>
        <span style="font-size:0.85rem; font-weight:800;">${item.confidence ? Number(item.confidence).toFixed(1) : 95.0}% ${t("confidenceLabel")}</span>
      </div>
      <h2 style="font-size:1.3rem; font-weight:800; color:var(--text-main); margin:0;">${item.disease}</h2>
      <div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">${item.date}</div>
    </div>

    ${distHtml}
    ${envHtml}

    <div class="advisory-box">
      <strong style="font-size:0.88rem; color:var(--primary); display:flex; align-items:center; gap:6px; margin-bottom:8px;">
        <i data-lucide="shield-check"></i> ${t("recommendedSolution")}
      </strong>
      <div>${advisoryFormatted}</div>
    </div>
  `;

  modal.classList.remove("hidden");
  if (window.lucide) lucide.createIcons();
}

function showUndoToast(msgText, onUndoCallback, onCommitCallback) {
  if (pendingDeletedData && typeof pendingDeletedData.commit === "function") {
    clearTimeout(undoToastTimer);
    clearInterval(undoCountdownInterval);
    pendingDeletedData.commit();
  }

  let timeLeft = 3;
  const toast = document.getElementById("undo-toast");
  const msgEl = document.getElementById("undo-toast-msg");
  const undoBtn = document.getElementById("btn-undo-action");
  const timeBar = document.getElementById("undo-toast-timer-bar");

  if (!toast) {
    if (typeof onCommitCallback === "function") onCommitCallback();
    return;
  }

  msgEl.textContent = msgText;
  undoBtn.innerHTML = `${t("btnUndo")} (<span id="undo-count-num">${timeLeft}</span>s)`;
  toast.classList.remove("hidden");

  if (timeBar) {
    timeBar.style.transition = "none";
    timeBar.style.width = "100%";
    setTimeout(() => {
      timeBar.style.transition = "width 3s linear";
      timeBar.style.width = "0%";
    }, 20);
  }

  undoCountdownInterval = setInterval(() => {
    timeLeft -= 1;
    const numEl = document.getElementById("undo-count-num");
    if (numEl && timeLeft >= 0) numEl.textContent = timeLeft;
    if (timeLeft <= 0) clearInterval(undoCountdownInterval);
  }, 1000);

  undoToastTimer = setTimeout(() => {
    clearInterval(undoCountdownInterval);
    toast.classList.add("hidden");
    if (typeof onCommitCallback === "function") onCommitCallback();
    pendingDeletedData = null;
  }, 3000);

  undoBtn.onclick = (e) => {
    e.preventDefault();
    clearTimeout(undoToastTimer);
    clearInterval(undoCountdownInterval);
    toast.classList.add("hidden");
    if (typeof onUndoCallback === "function") onUndoCallback();
    pendingDeletedData = null;
  };

  pendingDeletedData = { undo: onUndoCallback, commit: onCommitCallback };
}

function deleteSingleScanWithUndo(scanId) {
  let history = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  const targetIndex = history.findIndex(h => String(h.id) === String(scanId));
  if (targetIndex === -1) return;

  const deletedItem = history[targetIndex];
  history.splice(targetIndex, 1);
  localStorage.setItem("plantiq_history", JSON.stringify(history));
  renderHistoryPage();

  showUndoToast(
    t("toastSingleDeleted"),
    () => {
      let currentHistory = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
      currentHistory.splice(targetIndex, 0, deletedItem);
      localStorage.setItem("plantiq_history", JSON.stringify(currentHistory));
      renderHistoryPage();
    },
    () => {}
  );
}

function handleClearAllHistory() {
  const previousHistory = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  if (previousHistory.length === 0) return;

  localStorage.setItem("plantiq_history", "[]");
  renderHistoryPage();

  showUndoToast(
    t("toastAllCleared"),
    () => {
      localStorage.setItem("plantiq_history", JSON.stringify(previousHistory));
      renderHistoryPage();
    },
    () => {}
  );
}

window.openScanDetails = openScanDetails;
window.deleteSingleScanWithUndo = deleteSingleScanWithUndo;
window.handleClearAllHistory = handleClearAllHistory;
window.renderHistoryPage = renderHistoryPage;

document.addEventListener("DOMContentLoaded", () => initProfile());
