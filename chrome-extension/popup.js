// Ubiquiti Device Discovery Tool - UI Controller

let currentDevices = [];
let isScanning = false;

// DOM Elements
const btnScan = document.getElementById("btn-scan");
const scanIcon = document.getElementById("scan-icon");
const scanText = document.getElementById("scan-text");
const scanStatus = document.getElementById("scan-status");
const deviceCount = document.getElementById("device-count");
const searchInput = document.getElementById("search-input");
const btnClearSearch = document.getElementById("btn-clear-search");
const tbody = document.getElementById("devices-tbody");
const emptyState = document.getElementById("empty-state");
const errorBanner = document.getElementById("error-banner");
const btnFullscreen = document.getElementById("btn-fullscreen");
const btnExport = document.getElementById("btn-export");
const modalDetails = document.getElementById("modal-details");
const modalContent = document.getElementById("modal-content");
const btnCloseModal = document.getElementById("btn-close-modal");
const footerTimestamp = document.getElementById("footer-timestamp");

// Detect if running in full tab
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get("fullscreen") === "1" || window.innerWidth > 900) {
  document.body.classList.add("fullscreen");
  btnFullscreen.classList.add("hidden");
}

function formatUptime(seconds) {
  if (!seconds || seconds <= 0) return "-";
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m ${seconds % 60}s`;
}

function renderDevices() {
  const query = searchInput.value.trim().toLowerCase();
  const filtered = currentDevices.filter((dev) => {
    if (!query) return true;
    return (
      (dev.hostname && dev.hostname.toLowerCase().includes(query)) ||
      (dev.ip && dev.ip.toLowerCase().includes(query)) ||
      (dev.mac && dev.mac.toLowerCase().includes(query)) ||
      (dev.model && dev.model.toLowerCase().includes(query)) ||
      (dev.essid && dev.essid.toLowerCase().includes(query)) ||
      (dev.firmware && dev.firmware.toLowerCase().includes(query))
    );
  });

  tbody.innerHTML = "";
  deviceCount.textContent = `${filtered.length} dispositivo${filtered.length === 1 ? "" : "s"}`;

  if (filtered.length === 0) {
    emptyState.classList.remove("hidden");
    return;
  }

  emptyState.classList.add("hidden");

  filtered.forEach((dev) => {
    const tr = document.createElement("tr");

    // Dot online
    const tdStatus = document.createElement("td");
    tdStatus.className = "col-status";
    tdStatus.innerHTML = `<span class="status-dot" title="Online (Respondio UDP)"></span>`;
    tr.appendChild(tdStatus);

    // Hostname
    const tdHost = document.createElement("td");
    tdHost.innerHTML = `
      <div class="device-name">${dev.hostname || "UBNT"}</div>
      ${dev.essid ? `<div class="device-sub">SSID: ${dev.essid}</div>` : ""}
    `;
    tr.appendChild(tdHost);

    // Model
    const tdModel = document.createElement("td");
    tdModel.innerHTML = `<span class="badge-model">${dev.model || dev.platform || "Ubiquiti"}</span>`;
    tr.appendChild(tdModel);

    // IP
    const tdIp = document.createElement("td");
    tdIp.className = "device-ip";
    tdIp.innerHTML = `<a href="http://${dev.ip}" target="_blank" rel="noopener">${dev.ip}</a>`;
    tr.appendChild(tdIp);

    // MAC
    const tdMac = document.createElement("td");
    tdMac.className = "device-mac";
    tdMac.textContent = dev.mac || "-";
    tr.appendChild(tdMac);

    // Firmware
    const tdFw = document.createElement("td");
    tdFw.className = "device-sub";
    tdFw.textContent = dev.firmware || "-";
    tr.appendChild(tdFw);

    // Uptime
    const tdUptime = document.createElement("td");
    tdUptime.textContent = formatUptime(dev.uptime);
    tr.appendChild(tdUptime);

    // Actions
    const tdActions = document.createElement("td");
    tdActions.className = "row-actions";

    // Web UI button
    const btnWeb = document.createElement("button");
    btnWeb.className = "btn-icon";
    btnWeb.title = "Abrir interfaz web";
    btnWeb.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/></svg>`;
    btnWeb.addEventListener("click", () => window.open(`http://${dev.ip}`, "_blank"));
    tdActions.appendChild(btnWeb);

    // Copy IP button
    const btnCopyIp = document.createElement("button");
    btnCopyIp.className = "btn-icon";
    btnCopyIp.title = "Copiar IP";
    btnCopyIp.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
    btnCopyIp.addEventListener("click", () => {
      navigator.clipboard.writeText(dev.ip);
      btnCopyIp.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`;
      setTimeout(() => {
        btnCopyIp.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`;
      }, 1500);
    });
    tdActions.appendChild(btnCopyIp);

    // Details button
    const btnInfo = document.createElement("button");
    btnInfo.className = "btn-icon";
    btnInfo.title = "Ver detalles";
    btnInfo.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`;
    btnInfo.addEventListener("click", () => showDeviceDetails(dev));
    tdActions.appendChild(btnInfo);

    tr.appendChild(tdActions);
    tbody.appendChild(tr);
  });
}

function showDeviceDetails(dev) {
  let ifaceHtml = "";
  if (dev.interfaces && dev.interfaces.length > 0) {
    ifaceHtml = dev.interfaces
      .map((i) => `<code>${i.ip}</code> (${i.mac})`)
      .join("<br>");
  } else {
    ifaceHtml = `<code>${dev.ip}</code> (${dev.mac})`;
  }

  modalContent.innerHTML = `
    <div class="detail-grid">
      <div class="detail-label">Dispositivo:</div>
      <div class="detail-val"><strong>${dev.hostname || "UBNT"}</strong></div>

      <div class="detail-label">Modelo / Producto:</div>
      <div class="detail-val">${dev.model || dev.platform || "Ubiquiti"}</div>

      <div class="detail-label">Plataforma:</div>
      <div class="detail-val">${dev.platform || "-"}</div>

      <div class="detail-label">Dirección IP principal:</div>
      <div class="detail-val"><a href="http://${dev.ip}" target="_blank" style="color:var(--accent-cyan);">${dev.ip}</a></div>

      <div class="detail-label">Dirección MAC:</div>
      <div class="detail-val"><code>${dev.mac}</code></div>

      <div class="detail-label">Interfaces de red:</div>
      <div class="detail-val">${ifaceHtml}</div>

      <div class="detail-label">Firmware:</div>
      <div class="detail-val">${dev.firmware || "-"}</div>

      <div class="detail-label">ESSID inalámbrico:</div>
      <div class="detail-val">${dev.essid || "No aplica / Modo Ethernet"}</div>

      <div class="detail-label">Tiempo activo (Uptime):</div>
      <div class="detail-val">${formatUptime(dev.uptime)} (${dev.uptime || 0} segundos)</div>

      <div class="detail-label">Valores por defecto:</div>
      <div class="detail-val">${dev.is_default ? "Sí (Factory Default)" : "No"}</div>
    </div>
  `;
  modalDetails.classList.remove("hidden");
}

function startScan() {
  if (isScanning) return;
  isScanning = true;
  scanIcon.classList.add("rotating");
  scanText.textContent = "Buscando...";
  scanStatus.textContent = "Transmitiendo broadcast UDP 10001...";
  errorBanner.classList.add("hidden");

  chrome.runtime.sendMessage({ action: "scan", timeout: 2.8 }, (response) => {
    isScanning = false;
    scanIcon.classList.remove("rotating");
    scanText.textContent = "Escanear";
    scanStatus.textContent = "Completado";

    if (chrome.runtime.lastError || !response || response.status === "error") {
      const err = (response && response.error) || (chrome.runtime.lastError && chrome.runtime.lastError.message) || "Error al conectar con el host nativo";
      console.error("Scan error:", err);
      errorBanner.classList.remove("hidden");
      scanStatus.textContent = "Error de conexión";
      return;
    }

    if (response.devices) {
      currentDevices = response.devices;
      renderDevices();
      footerTimestamp.textContent = `Último escaneo: ${new Date().toLocaleTimeString()}`;
    }
  });
}

// Export CSV / JSON
function exportData() {
  if (currentDevices.length === 0) {
    alert("No hay dispositivos para exportar.");
    return;
  }
  const jsonStr = JSON.stringify(currentDevices, null, 2);
  const blob = new Blob([jsonStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `ubiquiti-devices-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

// Event Listeners
btnScan.addEventListener("click", startScan);

searchInput.addEventListener("input", () => {
  if (searchInput.value) {
    btnClearSearch.classList.remove("hidden");
  } else {
    btnClearSearch.classList.add("hidden");
  }
  renderDevices();
});

btnClearSearch.addEventListener("click", () => {
  searchInput.value = "";
  btnClearSearch.classList.add("hidden");
  renderDevices();
});

btnFullscreen.addEventListener("click", () => {
  chrome.runtime.sendMessage({ action: "open_full_tab" });
});

btnExport.addEventListener("click", exportData);

btnCloseModal.addEventListener("click", () => modalDetails.classList.add("hidden"));
modalDetails.addEventListener("click", (e) => {
  if (e.target === modalDetails) modalDetails.classList.add("hidden");
});

// Load cached devices from storage if any
chrome.storage.local.get(["last_devices", "last_scan_time"], (res) => {
  if (res.last_devices && res.last_devices.length > 0) {
    currentDevices = res.last_devices;
    renderDevices();
    if (res.last_scan_time) {
      footerTimestamp.textContent = `Último escaneo: ${new Date(res.last_scan_time).toLocaleTimeString()}`;
    }
  }
  // Auto-scan on open
  startScan();
});
