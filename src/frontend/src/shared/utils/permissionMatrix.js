// ===== AI GENERATED: permissionMatrix =====
// Purpose: Turn permission data from the API into table rows and readable groups
// Inputs: grants from /permission-matrix, or the capability map from /me
// Returns: matrix rows for the Owner's table, grouped capabilities for the account page
// Flow:
// 1. Roles keep the specification's order
// 2. Capabilities are grouped by their domain (the part before the dot)
// 3. Names are humanized for display

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { humanizeCode } from './statusLabels'

export const ROLE_ORDER = [
  'OWNER',
  'DISPATCHER',
  'FLEET_MANAGER',
  'DRIVER',
  'HELPER',
  'HR_PAYROLL',
  'ACCOUNTING',
]

const ROLE_LABELS = {
  OWNER: 'Owner / Manager',
  DISPATCHER: 'Dispatcher',
  FLEET_MANAGER: 'Fleet Manager',
  DRIVER: 'Driver',
  HELPER: 'Helper',
  HR_PAYROLL: 'HR & Payroll',
  ACCOUNTING: 'Accounting',
}

const DOMAIN_LABELS = {
  delivery_order: 'Orders',
  dispatch: 'Dispatch',
  truck: 'Fleet',
  driver_license: 'Licenses',
  employee: 'People',
  trip: 'Trips',
  or: 'OR documents',
  expense: 'Expenses',
  charge: 'Billing',
  client_rate: 'Billing',
  invoice: 'Billing',
  billing: 'Billing',
  earning_percentage: 'Payroll',
  payroll: 'Payroll',
  payroll_adjustment: 'Payroll',
  payroll_payment: 'Payroll',
  deduction: 'Payroll',
  cash_advance: 'Cash advances',
  report: 'Reports',
  audit_user: 'Administration',
}

/**
 * @function roleLabel
 * @description Readable name for a role code.
 * @param {string} roleCode Role code such as HR_PAYROLL
 * @returns {string}
 */
export function roleLabel(roleCode) {
  return ROLE_LABELS[roleCode] ?? humanizeCode(roleCode)
}

/**
 * @function domainOf
 * @description The part of a capability name before the dot.
 * @param {string} capabilityName Capability such as truck.manage
 * @returns {string}
 */
function domainOf(capabilityName) {
  return capabilityName.split('.')[0]
}

/**
 * @function domainLabel
 * @description Readable group name for a capability.
 * @param {string} capabilityName Capability such as truck.manage
 * @returns {string}
 */
export function domainLabel(capabilityName) {
  const domain = domainOf(capabilityName)
  return DOMAIN_LABELS[domain] ?? humanizeCode(domain)
}

/**
 * @function capabilityLabel
 * @description Readable capability name, for example "Truck manage".
 * @param {string} capabilityName Capability such as truck.manage
 * @returns {string}
 */
export function capabilityLabel(capabilityName) {
  return humanizeCode(capabilityName)
}

/**
 * @function buildMatrix
 * @description Pivot grants into one row per capability with a cell per role.
 * @param {Array<{capability: string, role_code: string, access_level: string}>} grants API grants
 * @returns {{roles: Array<string>, rows: Array<{capability: string, group: string, label: string, cells: Object<string, string|null>}>}}
 */
export function buildMatrix(grants) {
  const byCapability = new Map()
  for (const grant of grants) {
    if (!byCapability.has(grant.capability)) byCapability.set(grant.capability, {})
    byCapability.get(grant.capability)[grant.role_code] = grant.access_level
  }
  const rows = [...byCapability.entries()]
    .map(([capability, granted]) => ({
      capability,
      group: domainLabel(capability),
      label: capabilityLabel(capability),
      cells: Object.fromEntries(
        ROLE_ORDER.map((roleCode) => [roleCode, granted[roleCode] ?? null]),
      ),
    }))
    .sort(
      (left, right) =>
        left.group.localeCompare(right.group) || left.capability.localeCompare(right.capability),
    )
  return { roles: ROLE_ORDER, rows }
}

/**
 * @function groupCapabilities
 * @description Group a user's capability map by domain for display.
 * @param {Object<string, string>} capabilities Capability name to access level
 * @returns {Array<{group: string, entries: Array<{capability: string, label: string, level: string}>}>}
 */
export function groupCapabilities(capabilities) {
  const groups = new Map()
  for (const [capability, level] of Object.entries(capabilities)) {
    const group = domainLabel(capability)
    if (!groups.has(group)) groups.set(group, [])
    groups.get(group).push({ capability, label: capabilityLabel(capability), level })
  }
  return [...groups.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([group, entries]) => ({
      group,
      entries: entries.sort((left, right) => left.capability.localeCompare(right.capability)),
    }))
}
