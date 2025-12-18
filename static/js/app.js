// Basic front-end logic for Voice AI Studio
// - Handles status polling
// - Voice file upload (drag & drop + click)
// - Text + advanced settings form
// - Generate request
// - History listing, playback, and download

(function () {
  const $ = (sel) => document.querySelector(sel);

  const statusDot = $("#status-dot");
  const statusText = $("#status-text");
  const textInput = $("#text-input");
  const charCountEl = $("#char-count");
  const clearTextBtn = $("#clear-text-btn");
  const generateBtn = $("#generate-btn");
  const tempSlider = $("#temperature-slider");
  const tempValue = $("#temperature-value");
  const speedSlider = $("#speed-slider");
  const speedValue = $("#speed-value");
  const emotionSelect = $("#emotion-select");
  const voiceDropzone = $("#voice-dropzone");
  const voiceFileInput = $("#voice-file-input");
  const voiceInfo = $("#voice-info");
  const globalLoading = $("#global-loading");
  const toastContainer = $("#toast-container");
  const audioPlayer = $("#audio-player");
  const waveformPlaceholder = $("#waveform-placeholder");
  const downloadBtn = $("#download-btn");
  const historyList = $("#history-list");
  const refreshHistoryBtn = $("#refresh-history-btn");

  let currentVoiceId = null;
  let currentFilename = null;
  let statusPollTimer = null;

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  function setStatus(state, message) {
    statusDot.classList.remove("online", "error");
    if (state === "online") {
      statusDot.classList.add("online");
    } else if (state === "error") {
      statusDot.classList.add("error");
    }
    if (message) {
      statusText.textContent = message;
    }
  }

  function showToast(message, type = "info", timeout = 3500) {
    const toast = document.createElement("div");
    toast.className = "toast";
    if (type === "success") toast.classList.add("toast-success");
    if (type === "error") toast.classList.add("toast-error");

    const msg = document.createElement("div");
    msg.className = "toast-message";
    msg.textContent = message;
    toast.appendChild(msg);

    const closeBtn = document.createElement("div");
    closeBtn.className = "toast-close";
    closeBtn.textContent = "✕";
    closeBtn.addEventListener("click", () => {
      toastContainer.removeChild(toast);
    });
    toast.appendChild(closeBtn);

    toastContainer.appendChild(toast);

    if (timeout > 0) {
      setTimeout(() => {
        if (toast.parentNode === toastContainer) {
          toastContainer.removeChild(toast);
        }
      }, timeout);
    }
  }

  function setGlobalLoading(isLoading) {
    if (isLoading) {
      globalLoading.classList.remove("hidden");
      generateBtn.disabled = true;
    } else {
      globalLoading.classList.add("hidden");
      generateBtn.disabled = false;
    }
  }

  function updateCharCount() {
    const len = textInput.value.length;
    charCountEl.textContent = len.toString();
  }

  function resetOutput() {
    currentFilename = null;
    downloadBtn.disabled = true;
    audioPlayer.pause();
    audioPlayer.src = "";
    audioPlayer.style.display = "none";
    waveformPlaceholder.style.display = "flex";
    waveformPlaceholder.textContent = "No generation yet";
  }

  // ---------------------------------------------------------------------------
  // Status polling
  // ---------------------------------------------------------------------------

  async function pollStatusOnce() {
    try {
      const res = await fetch("/status");
      if (!res.ok) throw new Error("Status HTTP " + res.status);
      const data = await res.json();
      setStatus("online", "Ready • " + (data.model_name || "Model"));
    } catch (err) {
      console.error("Status error:", err);
      setStatus("error", "Backend offline");
    }
  }

  function startStatusPolling() {
    pollStatusOnce();
    statusPollTimer = setInterval(pollStatusOnce, 8000);
  }

  // ---------------------------------------------------------------------------
  // Voice upload
  // ---------------------------------------------------------------------------

  function handleVoiceFiles(files) {
    const file = files && files[0];
    if (!file) return;

    const allowed = ["audio/wav", "audio/x-wav", "audio/mpeg", "audio/flac", "audio/ogg"];
    if (!allowed.includes(file.type)) {
      showToast("Unsupported audio type. Use WAV/MP3/FLAC/OGG.", "error");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    voiceInfo.textContent = "Uploading…";

    fetch("/upload-voice", {
      method: "POST",
      body: formData,
    })
      .then(async (res) => {
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || "Upload failed");
        }
        return res.json();
      })
      .then((data) => {
        currentVoiceId = data.voice_id;
        voiceInfo.textContent = `Voice sample loaded: ${file.name}`;
        showToast("Voice sample uploaded.", "success");
      })
      .catch((err) => {
        console.error(err);
        currentVoiceId = null;
        voiceInfo.textContent = "";
        showToast(err.message || "Failed to upload voice", "error");
      });
  }

  function setupDropzone() {
    voiceDropzone.addEventListener("click", () => {
      voiceFileInput.click();
    });

    voiceFileInput.addEventListener("change", (e) => {
      handleVoiceFiles(e.target.files);
    });

    ["dragenter", "dragover"].forEach((evtName) => {
      voiceDropzone.addEventListener(evtName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        voiceDropzone.classList.add("dragover");
      });
    });

    ["dragleave", "drop"].forEach((evtName) => {
      voiceDropzone.addEventListener(evtName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        voiceDropzone.classList.remove("dragover");
      });
    });

    voiceDropzone.addEventListener("drop", (e) => {
      const dt = e.dataTransfer;
      if (dt && dt.files && dt.files.length > 0) {
        handleVoiceFiles(dt.files);
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Generate
  // ---------------------------------------------------------------------------

  async function doGenerate() {
    const text = textInput.value.trim();
    if (!text) {
      showToast("Please enter some text first.", "error");
      return;
    }
    if (text.length > 5000) {
      showToast("Text is too long. Limit is 5000 characters.", "error");
      return;
    }

    const formData = new FormData();
    formData.append("text", text);
    if (currentVoiceId) {
      formData.append("voice_id", currentVoiceId);
    }
    formData.append("temperature", tempSlider.value);
    formData.append("speed", speedSlider.value);
    formData.append("emotion", emotionSelect.value);

    setGlobalLoading(true);
    resetOutput();

    try {
      const res = await fetch("/generate", {
        method: "POST",
        body: formData,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Generation failed");
      }

      currentFilename = data.filename;
      const url = data.download_url || `/download/${encodeURIComponent(currentFilename)}`;
      audioPlayer.src = url;
      audioPlayer.style.display = "block";
      waveformPlaceholder.style.display = "none";
      downloadBtn.disabled = false;
      showToast("Generation completed.", "success");
      await loadHistory();
    } catch (err) {
      console.error(err);
      showToast(err.message || "Generation failed", "error");
    } finally {
      setGlobalLoading(false);
    }
  }

  // ---------------------------------------------------------------------------
  // History
  // ---------------------------------------------------------------------------

  async function loadHistory() {
    try {
      const res = await fetch("/history");
      if (!res.ok) throw new Error("Failed to load history");
      const data = await res.json();
      const items = data.items || [];

      historyList.innerHTML = "";
      if (items.length === 0) {
        const empty = document.createElement("div");
        empty.textContent = "No generations yet.";
        empty.style.fontSize = "12px";
        empty.style.color = "#888";
        historyList.appendChild(empty);
        return;
      }

      items.forEach((item) => {
        const el = document.createElement("div");
        el.className = "history-item";

        const meta = document.createElement("div");
        meta.className = "history-meta";

        const text = document.createElement("div");
        text.className = "history-text";
        text.textContent = item.text_preview || "(no preview)";

        const ts = document.createElement("div");
        ts.className = "history-timestamp";
        ts.textContent = item.timestamp || "";

        meta.appendChild(text);
        meta.appendChild(ts);

        const actions = document.createElement("div");
        actions.className = "history-actions";

        const playBtn = document.createElement("button");
        playBtn.className = "btn btn-ghost-small";
        playBtn.textContent = "Play";
        playBtn.addEventListener("click", () => {
          const url = `/download/${encodeURIComponent(item.filename)}`;
          audioPlayer.src = url;
          audioPlayer.style.display = "block";
          waveformPlaceholder.style.display = "none";
          downloadBtn.disabled = false;
          currentFilename = item.filename;
          audioPlayer.play().catch(() => {});
        });

        const dlBtn = document.createElement("button");
        dlBtn.className = "btn btn-ghost-small";
        dlBtn.textContent = "Download";
        dlBtn.addEventListener("click", () => {
          const url = `/download/${encodeURIComponent(item.filename)}`;
          window.open(url, "_blank");
        });

        actions.appendChild(playBtn);
        actions.appendChild(dlBtn);

        el.appendChild(meta);
        el.appendChild(actions);

        historyList.appendChild(el);
      });
    } catch (err) {
      console.error(err);
      showToast("Error loading history", "error");
    }
  }

  // ---------------------------------------------------------------------------
  // Event wiring
  // ---------------------------------------------------------------------------

  function setupEvents() {
    textInput.addEventListener("input", updateCharCount);
    updateCharCount();

    clearTextBtn.addEventListener("click", () => {
      textInput.value = "";
      updateCharCount();
    });

    generateBtn.addEventListener("click", () => {
      doGenerate();
    });

    downloadBtn.addEventListener("click", () => {
      if (!currentFilename) return;
      const url = `/download/${encodeURIComponent(currentFilename)}`;
      window.open(url, "_blank");
    });

    refreshHistoryBtn.addEventListener("click", () => {
      loadHistory();
    });

    tempSlider.addEventListener("input", () => {
      tempValue.textContent = tempSlider.value;
    });

    speedSlider.addEventListener("input", () => {
      speedValue.textContent = speedSlider.value;
    });

    // Keyboard shortcuts
    document.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        doGenerate();
      }
      if (e.key === "Escape") {
        // placeholder for future "cancel" support
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Init
  // ---------------------------------------------------------------------------

  window.addEventListener("DOMContentLoaded", () => {
    setupEvents();
    setupDropzone();
    startStatusPolling();
    loadHistory();
  });
})();


