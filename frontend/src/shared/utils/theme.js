// ===== AI GENERATED: theme =====
// Purpose: Remember and apply the chosen colour theme (dark navy or light)
// Inputs: a storage object and the document root (injectable for tests)
// Returns: theme names and helper functions
// Flow:
// 1. The preference is optional convenience: storage errors never break the app
// 2. Applying sets data-theme on the root element so daisyUI switches palettes

export const DARK_THEME = 'bm-dark'
export const LIGHT_THEME = 'bm-light'
const STORAGE_KEY = 'bm-theme'

/**
 * @function nextTheme
 * @description The theme the toggle switches to.
 * @param {string} currentTheme Current theme name
 * @returns {string}
 */
export function nextTheme(currentTheme) {
  return currentTheme === LIGHT_THEME ? DARK_THEME : LIGHT_THEME
}

/**
 * @function readStoredTheme
 * @description Saved theme, defaulting to dark; never throws.
 * @param {Storage} [storage] Storage to read from
 * @returns {string}
 */
export function readStoredTheme(storage = globalThis.localStorage) {
  try {
    const saved = storage?.getItem(STORAGE_KEY)
    return saved === LIGHT_THEME ? LIGHT_THEME : DARK_THEME
  } catch {
    return DARK_THEME
  }
}

/**
 * @function storeTheme
 * @description Save the theme; ignored when storage is unavailable.
 * @param {string} themeName Theme to save
 * @param {Storage} [storage] Storage to write to
 * @returns {void}
 */
export function storeTheme(themeName, storage = globalThis.localStorage) {
  try {
    storage?.setItem(STORAGE_KEY, themeName)
  } catch {
    // The preference is a convenience only.
  }
}

/**
 * @function applyTheme
 * @description Set the theme on the document root.
 * @param {string} themeName Theme to apply
 * @param {{setAttribute: function(string, string): void}} [root] Element to update
 * @returns {void}
 */
export function applyTheme(themeName, root = globalThis.document?.documentElement) {
  root?.setAttribute('data-theme', themeName)
}
