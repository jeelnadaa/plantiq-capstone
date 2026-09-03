// Scanner Module (ResNet50 CNN + RAG Advisory Pipeline)
let selectedScanFile = null;
let currentDiagnosisData = null;

function initScanner() {
  const dropzone = document.getElementById("upload-dropzone");
  const fileInput = document.getElementById("scan-file-input");
  const previewWrapper = document.getElementById("preview-wrapper");
  const previewImg = document.getElementById("preview-img");
  const btnRemovePhoto = document.getElementById("btn-remove-photo");
  const btnAnalyze = document.getElementById("btn-analyze-leaf");
  const diagnosisCard = document.getElementById("diagnosis-card");
  const btnClearScan = document.getElementById("btn-clear-scan");
  const btnAskInChat = document.getElementById("btn-ask-in-chat");

  if (!dropzone || !fileInput) return;

  dropzone.onclick = () => fileInput.click();

  fileInput.onchange = (e) => {
    if (e.target.files && e.target.files[0]) {
      selectedScanFile = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (ev) => {
        previewImg.src = ev.target.result;
        previewWrapper.classList.remove("hidden");
        dropzone.classList.add("hidden");
      };
      reader.readAsDataURL(selectedScanFile);
    }
  };

  if (btnRemovePhoto) {
    btnRemovePhoto.onclick = (e) => {
      e.stopPropagation();
      selectedScanFile = null;
      fileInput.value = "";
      previewWrapper.classList.add("hidden");
      dropzone.classList.remove("hidden");
    };
  }

  // Voice STT setup for specific question
  setupVoiceInput("btn-scan-mic", "input-scan-question");

  if (btnAnalyze) {
    btnAnalyze.onclick = async () => {
      if (!selectedScanFile) {
        alert(currentLang === "kn" ? "ದಯವಿಟ್ಟು ಮೊದಲಿಗೆ ಕಾಫಿ ಎಲೆಯ ಫೋಟೋ ಆಯ್ಕೆಮಾಡಿ." : "Please select or capture a coffee leaf image first.");
        return;
      }

      btnAnalyze.disabled = true;
      btnAnalyze.innerHTML = `<i data-lucide="loader-2" class="spin"></i> ${currentLang === "kn" ? "ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ..." : "Analyzing..."}`;
      if (window.lucide) lucide.createIcons();

      const questionText = (document.getElementById("input-scan-question")?.value || "").trim();
      const formData = new FormData();
      formData.append("file", selectedScanFile);
      formData.append("language", currentLang);
      if (LocationManager.coords.allowed) {
        formData.append("latitude", LocationManager.coords.lat);
        formData.append("longitude", LocationManager.coords.lng);
      }
      if (questionText) {
        formData.append("user_question", questionText);
      }

      try {
        const res = await apiRequest("/api/predict", {
          method: "POST",
          body: formData
        });
        if (res.ok) {
          const data = await res.json();
          currentDiagnosisData = data;
          renderDiagnosisCard(data);
          saveScanToLocalStorage(data, previewImg.src);
        } else {
          alert("Diagnosis failed. Please check server connection.");
        }
      } catch (err) {
        console.error("Scan error:", err);
      } finally {
        btnAnalyze.disabled = false;
        btnAnalyze.innerHTML = `<i data-lucide="sparkles"></i> <span data-i18n="btnAnalyze">${t("btnAnalyze")}</span>`;
        if (window.lucide) lucide.createIcons();
      }
    };
  }

  if (btnClearScan) {
    btnClearScan.onclick = () => {
      selectedScanFile = null;
      fileInput.value = "";
      previewWrapper.classList.add("hidden");
      dropzone.classList.remove("hidden");
      diagnosisCard.classList.add("hidden");
      currentDiagnosisData = null;
      document.getElementById("input-scan-question").value = "";
    };
  }

  if (btnAskInChat) {
    btnAskInChat.onclick = () => {
      if (currentDiagnosisData) {
        sessionStorage.setItem("plantiq_handoff", JSON.stringify({
          disease: currentDiagnosisData.disease,
          confidence: currentDiagnosisData.confidence,
          advisory: currentDiagnosisData.advisory,
          imageName: currentDiagnosisData.filename || "Scanned Leaf",
          imageDataUrl: previewImg.src
        }));
        window.location.href = "/chat";
      }
    };
  }
}

function renderDiagnosisCard(data) {
  const card = document.getElementById("diagnosis-card");
  if (!card) return;

  const badgeEl = document.getElementById("diag-badge");
  const diseaseNameEl = document.getElementById("diag-disease-name");
  const confTextEl = document.getElementById("diag-confidence-text");
  const confFillEl = document.getElementById("diag-confidence-fill");
  const distGrid = document.getElementById("diag-distribution-grid");
  const advisoryEl = document.getElementById("diag-advisory-content");
  const blendedNotice = document.getElementById("diag-blended-notice");

  badgeEl.className = data.is_healthy ? "badge-healthy" : "badge-disease";
  badgeEl.textContent = data.is_healthy ? t("healthyLabel") : t("diseaseLabel");
  diseaseNameEl.textContent = data.disease;

  confTextEl.textContent = `${data.confidence.toFixed(1)}%`;
  confFillEl.style.width = `${Math.min(data.confidence, 100)}%`;

  if (distGrid && data.distribution) {
    distGrid.innerHTML = Object.entries(data.distribution)
      .map(([k, v]) => `<div class="distribution-item"><span>${k}</span><strong>${v.toFixed(1)}%</strong></div>`)
      .join("");
  }

  if (advisoryEl) advisoryEl.innerHTML = formatMarkdown(data.advisory);

  if (blendedNotice) {
    if (data.is_blended) blendedNotice.classList.remove("hidden");
    else blendedNotice.classList.add("hidden");
  }

  card.classList.remove("hidden");
  card.scrollIntoView({ behavior: "smooth" });
  if (window.lucide) lucide.createIcons();
}

function saveScanToLocalStorage(data, imgDataUrl) {
  const item = {
    id: Date.now(),
    date: new Date().toLocaleDateString(),
    disease: data.disease,
    confidence: data.confidence,
    is_healthy: data.is_healthy,
    distribution: data.distribution || {},
    env_data: data.env_data || null,
    advisory: data.advisory || "",
    sources: data.sources || [],
    is_blended: data.is_blended || false,
    image: imgDataUrl
  };
  let scans = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  scans.unshift(item);
  localStorage.setItem("plantiq_history", JSON.stringify(scans.slice(0, 50)));
}

function formatMarkdown(text) {
  if (!text) return "";
  return text
    .replace(/^### (.*$)/gim, '<strong>$1</strong>')
    .replace(/^## (.*$)/gim, '<h4 style="margin: 8px 0 4px 0;">$1</h4>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^\* (.*$)/gim, '• $1<br>')
    .replace(/^\- (.*$)/gim, '• $1<br>')
    .replace(/\n/g, '<br>');
}

document.addEventListener("DOMContentLoaded", () => initScanner());
