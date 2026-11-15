// ===== AI GENERATED: navigation =====
// Purpose: Central, pure navigation and write-permission rules for the UI
// Inputs: backend-confirmed capability levels from /me
// Returns: visible pages (grouped for the sidebar) and write hints
// Flow:
// 1. Each page names the capability (or any of several) it needs, and optional levels
// 2. Pages marked preview are design mockups; their backend arrives in later sprints
// 3. UI only hides links; the backend still enforces every request

/**
 * @typedef {Object} NavigationItem
 * @property {string} key Stable page identifier
 * @property {string} label Text shown to the user
 * @property {string} group Sidebar section
 * @property {string} icon Icon name (see components/Icon)
 * @property {string|null} capability Capability required to see the page (null = everyone)
 * @property {Array<string>} [anyCapability] Alternative: any one of these capabilities
 * @property {Array<string>} [levels] Access levels that may see the page
 * @property {boolean} [preview] True when the page is a design mockup
 */

/** @type {Array<NavigationItem>} */
export const NAVIGATION_ITEMS = [
  { key: 'dashboard', label: 'Dashboard', group: 'Operations', icon: 'home', capability: 'dispatch.assign' },
  { key: 'dispatch', label: 'Dispatch', group: 'Operations', icon: 'route', capability: 'dispatch.assign' },
  { key: 'orders', label: 'Delivery orders', group: 'Operations', icon: 'clipboard', capability: 'delivery_order.manage' },
  { key: 'clients', label: 'Clients', group: 'Operations', icon: 'building', capability: 'delivery_order.manage' },
  { key: 'fleet', label: 'Fleet', group: 'Operations', icon: 'truck', capability: 'truck.manage' },
  { key: 'trips', label: 'My trips', group: 'Operations', icon: 'route', capability: 'trip.assignment_view', levels: ['OWN'] },
  { key: 'expenses', label: 'Trip expenses', group: 'Finance', icon: 'receipt', capability: null, anyCapability: ['expense.enter', 'expense.approve'], preview: true },
  { key: 'payroll', label: 'Payroll', group: 'Finance', icon: 'wallet', capability: null, anyCapability: ['payroll.view_others', 'payroll.view_own'], preview: true },
  { key: 'advances', label: 'Cash advances', group: 'Finance', icon: 'cash', capability: null, anyCapability: ['cash_advance.request', 'cash_advance.approve', 'cash_advance.release_repay'], preview: true },
  { key: 'billing', label: 'Billing', group: 'Finance', icon: 'invoice', capability: 'billing.manage', preview: true },
  { key: 'reports', label: 'Reports', group: 'Insights', icon: 'chart', capability: 'report.view', levels: ['FULL', 'VIEW'], preview: true },
  { key: 'people', label: 'People', group: 'Administration', icon: 'users', capability: 'employee.manage', levels: ['FULL'] },
  { key: 'audit', label: 'Audit log', group: 'Administration', icon: 'shield', capability: 'audit_user.manage' },
  { key: 'permissions', label: 'Permissions', group: 'Administration', icon: 'key', capability: 'audit_user.manage' },
  { key: 'account', label: 'My account', group: 'Account', icon: 'user', capability: null },
]

/**
 * @function isVisible
 * @description Decide whether one navigation item is allowed for the granted capabilities.
 * @param {NavigationItem} navigationItem Item to check
 * @param {Object<string, string>} capabilities Capability name to access level
 * @returns {boolean}
 */
function isVisible(navigationItem, capabilities) {
  const candidates = navigationItem.anyCapability ?? (navigationItem.capability ? [navigationItem.capability] : [])
  if (candidates.length === 0) return true
  return candidates.some((capabilityName) => {
    const grantedLevel = capabilities[capabilityName]
    if (grantedLevel === undefined) return false
    return !navigationItem.levels || navigationItem.levels.includes(grantedLevel)
  })
}

/**
 * @function visibleNavigation
 * @description Filter navigation by the capabilities the backend granted.
 * @param {Object<string, string>} capabilities Capability name to access level
 * @returns {Array<NavigationItem>}
 */
export function visibleNavigation(capabilities) {
  return NAVIGATION_ITEMS.filter((navigationItem) => isVisible(navigationItem, capabilities))
}

/**
 * @function groupNavigation
 * @description Group visible items by sidebar section, keeping their order.
 * @param {Array<NavigationItem>} items Visible navigation items
 * @returns {Array<{group: string, items: Array<NavigationItem>}>}
 */
export function groupNavigation(items) {
  const groups = []
  for (const navigationItem of items) {
    const existing = groups.find((entry) => entry.group === navigationItem.group)
    if (existing) existing.items.push(navigationItem)
    else groups.push({ group: navigationItem.group, items: [navigationItem] })
  }
  return groups
}

/**
 * @function resolveActivePage
 * @description The requested page when allowed, otherwise the user's first page.
 * @param {Array<NavigationItem>} items Visible navigation items
 * @param {string|null} requestedKey Page the user asked for
 * @returns {string}
 */
export function resolveActivePage(items, requestedKey) {
  return items.some((navigationItem) => navigationItem.key === requestedKey) ? requestedKey : items[0].key
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
