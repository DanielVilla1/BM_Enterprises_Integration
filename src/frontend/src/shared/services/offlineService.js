// ===== AI GENERATED: registerOfflineSupport =====
// Purpose: Register the production-only public connection-help worker.
// Inputs: Browser service-worker support and Vite production mode.
// Returns: No account data is persisted in browser caches.
// Flow: Defer registration until page load and keep development hot reload unaffected.

/** @returns {void} */
export function registerOfflineSupport() {
  if (!import.meta.env.PROD || !('serviceWorker' in navigator)) return
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js').catch(() => {
      // Connectivity helpers do not block the live operational workspace.
    })
  })
}
