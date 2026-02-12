let selectedFormat = "best";

function formatDuration(seconds) {
  if (!seconds) return "Unknown";
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  }
  return `${minutes}m ${secs}s`;
}

function showStatus(message, type = "loading") {
  const status = document.getElementById("status");
  status.textContent = message;
  status.className = `status active ${type}`;
}

function hideStatus() {
  document.getElementById("status").classList.remove("active");
}

function formatFileSize(bytes) {
  if (!bytes) return "Unknown size";
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

async function fetchVideoInfo() {
  const url = document.getElementById("videoUrl").value;

  if (!url) {
    showStatus("Please enter a valid Facebook URL", "error");
    return;
  }

  const fetchBtn = document.getElementById("fetchBtn");
  fetchBtn.disabled = true;
  showStatus("Fetching video information...", "loading");

  try {
    const response = await fetch("/get-info", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url }),
    });

    const data = await response.json();

    if (data.error) {
      showStatus(data.error, "error");
      fetchBtn.disabled = false;
      return;
    }

    document.getElementById("videoTitle").textContent = data.title;
    document.getElementById("videoDuration").textContent =
      `Duration: ${formatDuration(data.duration)}`;

    if (data.thumbnail) {
      document.getElementById("thumbnail").src = data.thumbnail;
    }

    const formatOptions = document.getElementById("formatOptions");
    formatOptions.innerHTML = "";

    if (data.formats && data.formats.length > 0) {
      data.formats.forEach((format, index) => {
        const isSelected = index === 0;
        const option = document.createElement("div");
        option.className = `format-option ${isSelected ? "selected" : ""}`;
        option.innerHTML = `
                            <input 
                                type="radio" 
                                id="format_${index}" 
                                name="format" 
                                value="${format.format_id}"
                                ${isSelected ? "checked" : ""}
                                onchange="selectFormat('${format.format_id}', this.parentElement)"
                            >
                            <label for="format_${index}">${format.description}</label>
                        `;
        option.onclick = () => {
          document.getElementById(`format_${index}`).checked = true;
          selectFormat(format.format_id, option);
        };
        formatOptions.appendChild(option);
      });

      selectedFormat = data.formats[0].format_id;
    }

    document.getElementById("infoSection").classList.add("active");
    hideStatus();
  } catch (error) {
    showStatus(`Error: ${error.message}`, "error");
  } finally {
    fetchBtn.disabled = false;
  }
}

function selectFormat(formatId, element) {
  selectedFormat = formatId;
  document.querySelectorAll(".format-option").forEach((opt) => {
    opt.classList.remove("selected");
  });
  element.classList.add("selected");
}

async function downloadVideo() {
  const url = document.getElementById("videoUrl").value;

  if (!url) {
    showStatus("Please enter a valid Facebook URL", "error");
    return;
  }

  const downloadBtn = document.getElementById("downloadBtn");
  downloadBtn.disabled = true;
  showStatus("Downloading video... This may take a few minutes.", "loading");

  try {
    const response = await fetch("/download", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url,
        format_id: selectedFormat,
      }),
    });

    const data = await response.json();

    if (data.error) {
      showStatus(data.error, "error");
    } else {
      showStatus("✓ " + data.message, "success");
      await loadDownloadsList();
      setTimeout(() => hideStatus(), 3000);
    }
  } catch (error) {
    showStatus(`Error: ${error.message}`, "error");
  } finally {
    downloadBtn.disabled = false;
  }
}

async function loadDownloadsList() {
  try {
    const response = await fetch("/downloads");
    const downloads = await response.json();

    const list = document.getElementById("downloadsList");

    if (downloads.length === 0) {
      list.innerHTML =
        '<li style="color: #999; padding: 20px; text-align: center;">No downloads yet</li>';
      return;
    }

    list.innerHTML = downloads
      .map(
        (file) => `
                    <li class="download-item">
                        <div class="download-item-info">
                            <div class="download-item-name">📹 ${file.name}</div>
                            <div class="download-item-size">${file.size.toFixed(1)} MB</div>
                        </div>
                    </li>
                `,
      )
      .join("");
  } catch (error) {
    console.error("Error loading downloads:", error);
  }
}

// Load downloads list on page load
window.addEventListener("load", loadDownloadsList);

// Allow Enter key to fetch info
document.getElementById("videoUrl").addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    fetchVideoInfo();
  }
});
