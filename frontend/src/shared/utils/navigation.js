// ===== AI GENERATED: navigation =====
// Purpose: Central, pure navigation and write-permission rules for the UI
// Inputs: backend-confirmed capability levels from /me
// Returns: visible navigation items and write hints
// Flow:
// 1. Each item names the capability it needs (null = any signed-in user)
// 2. UI only hides links; the backend still enforces every request

/**
 * @typedef {Object} NavigationItem
 * @property {string} key Stable page identifier
 * @property {string} label Text shown to the user
 * @property {string|null} capability Capability required to see the page
 */

/** @type {Array<NavigationItem>} */
export const NAVIGATION_ITEMS = [
  { key: 'orders', label: 'Delivery orders', capability: 'delivery_order.manage' },
  { key: 'clients', label: 'Clients', capability: 'delivery_order.manage' },
  { key: 'fleet', label: 'Fleet', capability: 'truck.manage' },
  { key: 'account', label: 'My account', capability: null },
]

/**
 * @function visibleNavigation
 * @description Filter navigation by the capabilities the backend granted.
 * @param {Object<string, string>} capabilities Capability name to access level
 * @returns {Array<NavigationItem>}
 */
export function visibleNavigation(capabilities) {
  return NAVIGATION_ITEMS.filter(
    (navigationItem) =>
      navigationItem.capability === null || capabilities[navigationItem.capability] !== undefined,
  )
}

/**
 * @function hasWriteAccess
 * @description True when the backend granted the FULL level for a capability.
 * @param {Object<string, string>} capabilities Capability name to access level
 * @param {string} capabilityName Capability to check
 * @returns {boolean}
 */
export function hasWriteAccess(capabilities, capabilityName) {
  return capabilities[capabilityName] === 'FULL'
}
