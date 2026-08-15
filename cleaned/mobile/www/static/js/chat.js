// Multi-Turn Chatbot Module with Image Persistence & Full Scan Metadata Handoff
let currentSessionId = null;
let attachedImageContext = null;
let attachedImageDataUrl = null;
let attachedScanMetadata = null; // Full historical scan metadata object

function initChat() {
  const chatMessagesList = document.getElementById("chat-messages-list");
  const chatInput = document.getElementById("chat-text-input");
  const btnSend = document.getElementById("btn-chat-send");
  const threadSelect = document.getElementById("chat-thread-select");
  const btnNewChat = document.getElementById("btn-new-chat");
  const attachBar = document.getElementById("chat-attached-bar");
  const attachLabel = document.getElementById("chat-attach-label");
  const attachThumb = document.getElementById("chat-attach-thumb");
  const btnRemoveAttach = document.getElementById("btn-remove-attach");
  const btnAttachPicker = document.getElementById("btn-chat-attach-picker");
  const pickerModal = document.getElementById("chat-image-picker-modal");
  const closePickerBtn = document.getElementById("btn-close-picker-modal");
  const optUploadBtn = document.getElementById("btn-picker-upload-new");
  const hiddenFileInput = document.getElementById("chat-picker-file-input");
  const btnClearAttach = document.getElementById("btn-picker-clear-attach");

  // Check for Scan-to-Chat Handoff from Scanner
  const handoff = sessionStorage.getItem("plantiq_handoff");
  if (handoff) {
    try {
      const data = JSON.parse(handoff);
      attachedScanMetadata = data;
      setAttachedImage(data.imageName || data.disease || "Scanned Leaf", data.imageDataUrl || data.image);
      setTimeout(() => {
        sendChatMessage(`I just diagnosed ${data.disease} (${data.confidence ? Number(data.confidence).toFixed(1) : 95.0}%). What should be my spray timing and care protocol based on my estate conditions?`, data.disease);
      }, 300);
      sessionStorage.removeItem("plantiq_handoff");
    } catch(e){}
  }

  // Voice STT setup for Chat
  setupVoiceInput("btn-chat-mic", "chat-text-input");

  // Open Image Picker Modal
  if (btnAttachPicker) {
    btnAttachPicker.onclick = (e) => {
      e.preventDefault();
      openChatImagePicker();
    };
  }

  if (closePickerBtn && pickerModal) {
    closePickerBtn.onclick = () => pickerModal.classList.add("hidden");
  }

  if (optUploadBtn && hiddenFileInput) {
    optUploadBtn.onclick = () => hiddenFileInput.click();
    hiddenFileInput.onchange = (e) => {
      if (e.target.files && e.target.files[0]) {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = (ev) => {
          attachedScanMetadata = null; // Fresh upload
          setAttachedImage(file.name, ev.target.result);
          if (pickerModal) pickerModal.classList.add("hidden");
        };
        reader.readAsDataURL(file);
      }
      hiddenFileInput.value = "";
    };
  }

  if (btnClearAttach && pickerModal) {
    btnClearAttach.onclick = () => {
      clearAttachedImage();
      pickerModal.classList.add("hidden");
    };
  }

  if (btnRemoveAttach) {
    btnRemoveAttach.onclick = () => clearAttachedImage();
  }

  if (btnSend && chatInput) {
    btnSend.onclick = (e) => {
      e.preventDefault();
      handleSendAction();
    };

    chatInput.onkeydown = (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSendAction();
      }
    };
  }

  if (btnNewChat) {
    btnNewChat.onclick = () => {
      currentSessionId = null;
      if (threadSelect) threadSelect.value = "";
      renderWelcomeMessage();
    };
  }

  loadThreads();
}

function handleSendAction() {
  const chatInput = document.getElementById("chat-text-input");
  if (!chatInput) return;
  const msg = chatInput.value.trim();
  if (msg) {
    chatInput.value = "";
    sendChatMessage(msg);
  }
}

function openChatImagePicker() {
  const pickerModal = document.getElementById("chat-image-picker-modal");
  if (pickerModal) {
    renderPickerHistoryList();
    pickerModal.classList.remove("hidden");
    if (window.lucide) lucide.createIcons();
  }
}

window.openChatImagePicker = openChatImagePicker;

function setAttachedImage(name, dataUrl) {
  attachedImageContext = name;
  attachedImageDataUrl = dataUrl;
  const attachBar = document.getElementById("chat-attached-bar");
  const attachLabel = document.getElementById("chat-attach-label");
  const attachThumb = document.getElementById("chat-attach-thumb");

  if (attachBar && attachLabel) {
    attachLabel.textContent = `${t("attachedLeaf")}${name}`;
    if (attachThumb && dataUrl) {
      attachThumb.src = dataUrl;
      attachThumb.classList.remove("hidden");
    }
    attachBar.classList.remove("hidden");
  }
}

function clearAttachedImage() {
  attachedImageContext = null;
  attachedImageDataUrl = null;
  attachedScanMetadata = null;
  const attachBar = document.getElementById("chat-attached-bar");
  const attachThumb = document.getElementById("chat-attach-thumb");
  if (attachBar) attachBar.classList.add("hidden");
  if (attachThumb) attachThumb.classList.add("hidden");
}

function renderPickerHistoryList() {
  const container = document.getElementById("picker-history-container");
  if (!container) return;

  const history = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  if (history.length === 0) {
    container.innerHTML = `<div style="font-size:0.78rem; color:var(--text-muted); padding:10px 0;">${t("noScansFound")}</div>`;
    return;
  }

  container.innerHTML = `
    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:8px; max-height:220px; overflow-y:auto;">
      ${history.map(item => `
        <div class="card" style="padding:6px; cursor:pointer; text-align:center; border:1px solid var(--border-subtle); margin:0;" onclick="selectImageFromHistory('${item.id}')">
          <img src="${item.image}" style="width:100%; height:60px; object-fit:cover; border-radius:6px; margin-bottom:4px;">
          <div style="font-size:0.72rem; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${item.disease}</div>
          <div style="font-size:0.65rem; color:var(--text-muted);">${item.date}</div>
        </div>
      `).join('')}
    </div>
  `;
}

function selectImageFromHistory(scanId) {
  const history = JSON.parse(localStorage.getItem("plantiq_history") || "[]");
  const item = history.find(h => String(h.id) === String(scanId));
  if (item) {
    attachedScanMetadata = item; // Capture full metadata (env_data, advisory, confidence, etc.)
    setAttachedImage(`${item.disease} (${item.confidence ? Number(item.confidence).toFixed(0) : 95}%)`, item.image);
    const pickerModal = document.getElementById("chat-image-picker-modal");
    if (pickerModal) pickerModal.classList.add("hidden");
  }
}

window.selectImageFromHistory = selectImageFromHistory;

function renderWelcomeMessage() {
  const list = document.getElementById("chat-messages-list");
  if (!list) return;
  list.innerHTML = `
    <div class="msg-row assistant-msg">
      <div class="msg-bubble">
        <p>${t("chatWelcome")}</p>
      </div>
    </div>
  `;
}

async function loadThreads() {
  const threadSelect = document.getElementById("chat-thread-select");
  if (!threadSelect) return;

  try {
    const res = await apiRequest("/api/chat/threads");
    if (res.ok) {
      const threads = await res.json();
      threadSelect.innerHTML = `<option value="">${t("newConversation")}</option>` +
        threads.map(t => `<option value="${t.id}">${t.title}</option>`).join("");

      threadSelect.onchange = async () => {
        if (threadSelect.value) {
          currentSessionId = threadSelect.value;
          await loadThreadMessages(currentSessionId);
        } else {
          currentSessionId = null;
          renderWelcomeMessage();
        }
      };
    }
  } catch(e){}
}

async function loadThreadMessages(threadId) {
  const list = document.getElementById("chat-messages-list");
  if (!list) return;
  try {
    const res = await apiRequest(`/api/chat/threads/${threadId}/messages`);
    if (res.ok) {
      const messages = await res.json();
      list.innerHTML = "";
      messages.forEach(m => appendMessageToDOM(m.role, m.content, m.image_data_url));
      list.scrollTop = list.scrollHeight;
    }
  } catch(e){}
}

async function sendChatMessage(messageText, diseaseCtx = null) {
  const attachedImgToSend = attachedImageDataUrl;
  const attachedNameToSend = attachedImageContext;
  const metadataToSend = attachedScanMetadata;

  appendMessageToDOM("user", messageText, attachedImgToSend);

  const formData = new FormData();
  if (currentSessionId) formData.append("session_id", currentSessionId);
  formData.append("user_message", messageText);
  formData.append("language", currentLang);
  if (attachedNameToSend) formData.append("attached_image_name", attachedNameToSend);
  if (attachedImgToSend) formData.append("image_base64", attachedImgToSend);
  if (metadataToSend) formData.append("scan_metadata_json", JSON.stringify(metadataToSend));
  if (diseaseCtx) formData.append("disease_context", diseaseCtx);
  if (window.LocationManager && LocationManager.coords.allowed) {
    formData.append("latitude", LocationManager.coords.lat);
    formData.append("longitude", LocationManager.coords.lng);
  }

  // Placeholder typing bubble
  const list = document.getElementById("chat-messages-list");
  const typingDiv = document.createElement("div");
  typingDiv.className = "msg-row assistant-msg";
  typingDiv.innerHTML = `<div class="msg-bubble"><i data-lucide="loader-2" class="spin"></i> PlantIQ thinking...</div>`;
  list.appendChild(typingDiv);
  list.scrollTop = list.scrollHeight;
  if (window.lucide) lucide.createIcons();

  try {
    const res = await apiRequest("/api/chat/message", {
      method: "POST",
      body: formData
    });
    if (res.ok) {
      const data = await res.json();
      currentSessionId = data.session_id;
      typingDiv.remove();
      appendMessageToDOM("assistant", data.reply);
      loadThreads();
    } else {
      typingDiv.innerHTML = `<div class="msg-bubble" style="color:red;">Failed to get response.</div>`;
    }
  } catch (err) {
    typingDiv.innerHTML = `<div class="msg-bubble" style="color:red;">Error connecting to assistant.</div>`;
  }
}

function appendMessageToDOM(role, content, imgUrl = null) {
  const list = document.getElementById("chat-messages-list");
  if (!list) return;
  const row = document.createElement("div");
  row.className = `msg-row ${role === "user" ? "user-msg" : "assistant-msg"}`;
  
  let imgHtml = "";
  if (imgUrl) {
    imgHtml = `<img src="${imgUrl}" style="width:100%; max-height:160px; object-fit:cover; border-radius:8px; margin-bottom:6px; display:block; border:1px solid rgba(255,255,255,0.2);">`;
  }

  const formattedContent = typeof window.formatMarkdown === "function" ? window.formatMarkdown(content) : content;
  row.innerHTML = `<div class="msg-bubble">${imgHtml}<p>${formattedContent}</p></div>`;
  list.appendChild(row);
  list.scrollTop = list.scrollHeight;
  if (window.lucide) lucide.createIcons();
}

document.addEventListener("DOMContentLoaded", () => initChat());
