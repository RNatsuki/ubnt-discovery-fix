// Background Service Worker (Manifest V3)
const NATIVE_HOST = "com.ubnt.discovery";

chrome.runtime.onInstalled.addListener(() => {
  console.log("Ubiquiti Device Discovery Tool instalada.");
});

// Listener para solicitudes desde popup.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "scan") {
    chrome.runtime.sendNativeMessage(
      NATIVE_HOST,
      { action: "scan", timeout: request.timeout || 2.5 },
      (response) => {
        if (chrome.runtime.lastError) {
          console.error("Error Native Host:", chrome.runtime.lastError.message);
          sendResponse({
            status: "error",
            error: chrome.runtime.lastError.message
          });
        } else {
          // Guardar ultimo resultado en storage
          if (response && response.devices) {
            chrome.storage.local.set({
              last_devices: response.devices,
              last_scan_time: Date.now()
            });
          }
          sendResponse(response);
        }
      }
    );
    return true; // Respuesta asincrona
  }

  if (request.action === "open_full_tab") {
    chrome.tabs.create({ url: chrome.runtime.getURL("popup.html?fullscreen=1") });
    sendResponse({ status: "ok" });
  }
});
