/**
 * app.js
 * ======
 * Client-Side Controller for PlantIQ Dual CNN Model Comparator.
 */

let selectedFile = null;
let selectedSampleFilename = null;

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    lucide.createIcons();
  }

  loadSampleLeaves();
  setupDropzone();
  setupButtons();
});

/**
 * Fetch and render 1-click sample leaf cards from server
 */
async function loadSampleLeaves() {
  const container = document.getElementById("sample-cards-list");
  try {
    const res = await fetch("/api/samples");
    const data = await res.json();
    
    if (data.samples && data.samples.length > 0) {
      container.innerHTML = "";
      data.samples.forEach(sample => {
        const card = document.createElement("div");
        card.className = "sample-card";
        card.innerHTML = `
          <img src="${sample.url}" alt="${sample.label}">
          <div class="sample-card-label">${sample.label}</div>
        `;
        card.onclick = () => selectSample(sample);
        container.appendChild(card);
      });
    } else {
      container.innerHTML = "<p style='color:#64748b; font-size:0.8rem;'>No sample images found.</p>";
    }
  } catch (err) {
    console.warn("Failed to load sample images:", err);
  }
}

/**
 * Select a preset sample leaf and run dual comparison
 */
function selectSample(sample) {
  selectedFile = null;
  selectedSampleFilename = sample.filename;

  // Show preview
  const dropzonePlaceholder = document.getElementById("dropzone-placeholder");
  const dropzonePreview = document.getElementById("dropzone-preview");
  const previewImg = document.getElementById("preview-image");

  previewImg.src = sample.url;
  dropzonePlaceholder.classList.add("hidden");
  dropzonePreview.classList.remove("hidden");

  // Automatically execute dual inference
  runDualComparison();
}

/**
 * Drag and Drop & File Input Setup
 */
function setupDropzone() {
  const dropzone = document.getElementById("leaf-dropzone");
  const fileInput = document.getElementById("file-input");
  const btnBrowse = document.getElementById("btn-browse");
  const btnChange = document.getElementById("btn-change-image");
  const dropzonePlaceholder = document.getElementById("dropzone-placeholder");
  const dropzonePreview = document.getElementById("dropzone-preview");
  const previewImg = document.getElementById("preview-image");

  btnBrowse.onclick = (e) => {
    e.stopPropagation();
    fileInput.click();
  };

  btnChange.onclick = (e) => {
    e.stopPropagation();
    selectedFile = null;
    selectedSampleFilename = null;
    dropzonePreview.classList.add("hidden");
    dropzonePlaceholder.classList.remove("hidden");
    document.getElementById("results-section").classList.add("hidden");
  };

  dropzone.onclick = () => {
    if (!selectedFile && !selectedSampleFilename) {
      fileInput.click();
    }
  };

  fileInput.onchange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  };

  // Drag over styling
  dropzone.ondragover = (e) => {
    e.preventDefault();
    dropzone.classList.add("drag-over");
  };

  dropzone.ondragleave = () => {
    dropzone.classList.remove("drag-over");
  };

  dropzone.ondrop = (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag-over");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };
}

function handleFileSelected(file) {
  selectedFile = file;
  selectedSampleFilename = null;

  const reader = new FileReader();
  reader.onload = (e) => {
    const previewImg = document.getElementById("preview-image");
    previewImg.src = e.target.result;
    document.getElementById("dropzone-placeholder").classList.add("hidden");
    document.getElementById("dropzone-preview").classList.remove("hidden");

    // Automatically trigger comparison
    runDualComparison();
  };
  reader.readAsDataURL(file);
}

function setupButtons() {
  const btnRun = document.getElementById("btn-run-dual");
  if (btnRun) {
    btnRun.onclick = (e) => {
      e.stopPropagation();
      runDualComparison();
    };
  }
}

/**
 * Execute Parallel Dual Model Comparison Inference
 */
async function runDualComparison() {
  if (!selectedFile && !selectedSampleFilename) {
    alert("Please upload an image or select a sample leaf.");
    return;
  }

  const loadingSec = document.getElementById("loading-section");
  const resultsSec = document.getElementById("results-section");

  resultsSec.classList.add("hidden");
  loadingSec.classList.remove("hidden");

  // Scroll to loading indicator
  loadingSec.scrollIntoView({ behavior: "smooth", block: "center" });

  try {
    const formData = new FormData();
    if (selectedFile) {
      formData.append("file", selectedFile);
    } else if (selectedSampleFilename) {
      formData.append("sample_filename", selectedSampleFilename);
    }

    const response = await fetch("/api/compare", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (data.error) {
      alert("Inference Error: " + data.error);
      loadingSec.classList.add("hidden");
      return;
    }

    renderComparisonResults(data);

    loadingSec.classList.add("hidden");
    resultsSec.classList.remove("hidden");
    resultsSec.scrollIntoView({ behavior: "smooth", block: "start" });

  } catch (err) {
    console.error("Comparison request failed:", err);
    alert("Failed to communicate with dual model backend.");
    loadingSec.classList.add("hidden");
  }
}

/**
 * Render Side-by-Side Comparison Metrics & Diagnostics
 */
function renderComparisonResults(data) {
  const oldModel = data.models.old_model;
  const newModel = data.models.new_model;
  const comp = data.comparison;

  // 1. Consensus Banner
  const banner = document.getElementById("consensus-banner");
  const bannerTitle = document.getElementById("consensus-title");
  const bannerDesc = document.getElementById("consensus-desc");
  const bannerIcon = document.getElementById("consensus-icon");

  banner.className = `consensus-banner ${comp.agreement_badge}`;
  bannerTitle.textContent = comp.agreement_status;
  bannerDesc.textContent = comp.analysis;

  if (comp.agreement_badge === "consensus_high") {
    bannerIcon.innerHTML = `<i data-lucide="check-circle-2"></i>`;
  } else if (comp.agreement_badge === "consensus_moderate") {
    bannerIcon.innerHTML = `<i data-lucide="alert-circle"></i>`;
  } else {
    bannerIcon.innerHTML = `<i data-lucide="alert-triangle"></i>`;
  }

  // 2. Model A Card (Old PyTorch ResNet-50)
  document.getElementById("old-pred-class").textContent = oldModel.predicted_class;
  document.getElementById("old-conf-val").textContent = `${oldModel.confidence.toFixed(1)}%`;
  document.getElementById("old-conf-bar").style.width = `${oldModel.confidence}%`;
  document.getElementById("old-latency").textContent = `${oldModel.latency_ms} ms`;
  document.getElementById("old-weights-src").textContent = oldModel.weights_source;

  // 3. Model B Card (New Custom Keras CNN)
  document.getElementById("new-pred-class").textContent = newModel.predicted_class;
  document.getElementById("new-conf-val").textContent = `${newModel.confidence.toFixed(1)}%`;
  document.getElementById("new-conf-bar").style.width = `${newModel.confidence}%`;
  document.getElementById("new-latency").textContent = `${newModel.latency_ms} ms`;
  document.getElementById("new-weights-src").textContent = newModel.weights_source;

  // 4. Probability Distribution Table
  const tbody = document.getElementById("distribution-tbody");
  tbody.innerHTML = "";

  comp.distribution_comparison.forEach(item => {
    const tr = document.createElement("tr");

    let diffClass = "diff-zero";
    let diffSign = "";
    if (item.diff > 0.05) {
      diffClass = "diff-pos";
      diffSign = "+";
    } else if (item.diff < -0.05) {
      diffClass = "diff-neg";
    }

    tr.innerHTML = `
      <td class="class-title-cell">${item.class_name}</td>
      <td class="prob-bar-cell">
        <div class="prob-bar-wrapper">
          <div class="mini-track">
            <div class="mini-fill-old" style="width: ${item.old_prob}%"></div>
          </div>
          <span class="prob-val-text" style="color: #6ee7b7;">${item.old_prob.toFixed(1)}%</span>
        </div>
      </td>
      <td class="prob-bar-cell">
        <div class="prob-bar-wrapper">
          <div class="mini-track">
            <div class="mini-fill-new" style="width: ${item.new_prob}%"></div>
          </div>
          <span class="prob-val-text" style="color: #93c5fd;">${item.new_prob.toFixed(1)}%</span>
        </div>
      </td>
      <td class="th-right">
        <span class="diff-pill ${diffClass}">${diffSign}${item.diff.toFixed(1)}%</span>
      </td>
    `;
    tbody.appendChild(tr);
  });

  // Re-render fresh Lucide icons
  if (window.lucide) {
    lucide.createIcons();
  }
}
