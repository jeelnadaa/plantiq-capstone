// MediaRecorder Speech-to-Text & Language Prompt Modal
let mediaRecorder = null;
let audioChunks = [];
let activeRecordingBtn = null;
let currentTargetInput = null;

function setupVoiceInput(triggerBtnId, inputTargetId) {
  const triggerBtn = document.getElementById(triggerBtnId);
  const inputTarget = document.getElementById(inputTargetId);
  const voiceModal = document.getElementById("voice-lang-modal");

  if (!triggerBtn || !inputTarget) return;

  triggerBtn.onclick = () => {
    if (triggerBtn.classList.contains("recording")) {
      stopVoiceRecording();
      return;
    }

    currentTargetInput = inputTarget;
    activeRecordingBtn = triggerBtn;

    // Show Voice Language Modal Prompt
    if (voiceModal) {
      voiceModal.classList.remove("hidden");
    } else {
      startVoiceCapture(currentLang === "kn" ? "kn" : "en");
    }
  };
}

async function startVoiceCapture(selectedLanguage) {
  const voiceModal = document.getElementById("voice-lang-modal");
  if (voiceModal) voiceModal.classList.add("hidden");

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(track => track.stop());
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      await sendVoiceToBackend(audioBlob, selectedLanguage);
    };

    mediaRecorder.start();
    if (activeRecordingBtn) {
      activeRecordingBtn.classList.add("recording");
      activeRecordingBtn.innerHTML = '<i data-lucide="square"></i>';
      if (window.lucide) lucide.createIcons();
    }
  } catch (err) {
    alert("Microphone permission denied or unavailable. Please enable microphone permissions in your browser.");
  }
}

function stopVoiceRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
  }
  if (activeRecordingBtn) {
    activeRecordingBtn.classList.remove("recording");
    activeRecordingBtn.innerHTML = '<i data-lucide="mic"></i>';
    if (window.lucide) lucide.createIcons();
  }
}

async function sendVoiceToBackend(audioBlob, selectedLanguage) {
  if (!currentTargetInput) return;
  const originalPlaceholder = currentTargetInput.placeholder;
  currentTargetInput.placeholder = currentLang === "kn" ? "ಧ್ವನಿ ಪರಿವರ್ತಿಸಲಾಗುತ್ತಿದೆ..." : "Transcribing speech...";

  const formData = new FormData();
  formData.append("file", audioBlob, "voice_note.webm");
  formData.append("target_language", selectedLanguage);

  try {
    const res = await apiRequest("/api/voice/transcribe", {
      method: "POST",
      body: formData
    });
    if (res.ok) {
      const data = await res.json();
      if (data.text) {
        currentTargetInput.value = data.text;
      }
    }
  } catch (e) {
    console.error("Voice STT error:", e);
  } finally {
    currentTargetInput.placeholder = originalPlaceholder;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const btnKn = document.getElementById("btn-voice-opt-kn");
  const btnEn = document.getElementById("btn-voice-opt-en");
  const btnCancel = document.getElementById("btn-voice-opt-cancel");
  const voiceModal = document.getElementById("voice-lang-modal");

  if (btnKn) btnKn.onclick = () => startVoiceCapture("kn");
  if (btnEn) btnEn.onclick = () => startVoiceCapture("en");
  if (btnCancel && voiceModal) btnCancel.onclick = () => voiceModal.classList.add("hidden");
});
