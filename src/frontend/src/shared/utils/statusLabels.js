// ===== AI GENERATED: statusLabels =====
// Purpose: Human labels and colour tones for every status shown in the UI
// Inputs: a status kind (order, trip, truck, license, employee) and a status code
// Returns: { label, tone } with tone one of neutral, info, primary, success, warning, error, accent
// Flow:
// 1. One lookup table per kind keeps wording and colours consistent across screens
// 2. Unknown codes fall back to a readable version of the code

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

/** @type {Object<string, Object<string, [string, string]>>} */
const STATUS_TABLE = {
  order: {
    PENDING: ['Pending', 'warning'],
    PARTIALLY_ASSIGNED: ['Partly assigned', 'info'],
    SCHEDULED: ['Scheduled', 'info'],
    IN_PROGRESS: ['In progress', 'primary'],
    COMPLETED: ['Completed', 'success'],
    CANCELLED: ['Cancelled', 'neutral'],
  },
  trip: {
    SCHEDULED: ['Scheduled', 'neutral'],
    ACCEPTED: ['Accepted', 'info'],
    CLEARED_FOR_DISPATCH: ['Cleared', 'info'],
    IN_TRANSIT: ['In transit', 'primary'],
    DELIVERED_OR_PENDING: ['Delivered · OR pending', 'warning'],
    OR_UPLOADED: ['OR uploaded · awaiting receipt', 'accent'],
    COMPLETED: ['Completed', 'success'],
    FAILED: ['Failed', 'error'],
    CANCELLED: ['Cancelled', 'neutral'],
  },
  truck: {
    AVAILABLE: ['Available', 'success'],
    ASSIGNED: ['Assigned', 'info'],
    IN_TRANSIT: ['On the road', 'primary'],
    MAINTENANCE: ['In maintenance', 'warning'],
  },
  license: {
    VALID: ['Valid', 'success'],
    EXPIRING_SOON: ['Expiring soon', 'warning'],
    EXPIRED: ['Expired', 'error'],
  },
  employee: {
    ACTIVE: ['Active', 'success'],
    INACTIVE: ['Inactive', 'neutral'],
  },
  expense: {
    ENTERING: ['Being entered', 'neutral'],
    AWAITING_REVIEW: ['Awaiting review', 'warning'],
    FINALIZED: ['Finalized', 'success'],
    ZERO_CONFIRMED: ['Zero expenses confirmed', 'info'],
  },
  payroll: {
    PENDING_CALCULATION: ['Pending calculation', 'warning'],
    CALCULATED: ['Calculated', 'info'],
    FINALIZED: ['Finalized', 'accent'],
    PAID: ['Paid', 'success'],
  },
  advance: {
    REQUESTED: ['Requested', 'warning'],
    APPROVED: ['Approved', 'info'],
    RELEASED: ['Released', 'primary'],
    REPAYING: ['Repaying', 'accent'],
    SETTLED: ['Settled', 'success'],
  },
  invoice: {
    DRAFT: ['Draft', 'neutral'],
    ISSUED: ['Issued', 'info'],
    PARTIALLY_PAID: ['Partly paid', 'warning'],
    PAID: ['Paid', 'success'],
    VOID: ['Void', 'error'],
  },
}

/** Trip statuses in the order a normal trip moves through them. */
export const TRIP_STEPS = [
  { status: 'SCHEDULED', label: 'Scheduled' },
  { status: 'ACCEPTED', label: 'Accepted' },
  { status: 'CLEARED_FOR_DISPATCH', label: 'Cleared' },
  { status: 'IN_TRANSIT', label: 'On the road' },
  { status: 'DELIVERED_OR_PENDING', label: 'Delivered' },
  { status: 'OR_UPLOADED', label: 'OR sent' },
  { status: 'COMPLETED', label: 'Done' },
]

/**
 * @function humanizeCode
 * @description Turn SOME_CODE into "Some code".
 * @param {string} code Machine-readable code
 * @returns {string}
 */
export function humanizeCode(code) {
  const words = String(code ?? '')
    .replaceAll('_', ' ')
    .replaceAll('.', ' ')
    .trim()
    .toLowerCase()
  return words.charAt(0).toUpperCase() + words.slice(1)
}

/**
 * @function describeStatus
 * @description Label and colour tone for a status.
 * @param {string} statusKind order, trip, truck, license or employee
 * @param {string} statusCode Status code from the API
 * @returns {{label: string, tone: string}}
 */
export function describeStatus(statusKind, statusCode) {
  const entry = STATUS_TABLE[statusKind]?.[statusCode]
  if (!entry) return { label: humanizeCode(statusCode), tone: 'neutral' }
  return { label: entry[0], tone: entry[1] }
}

/**
 * @function tripStepIndex
 * @description Position of a trip status in the normal flow, or -1 for failed and cancelled trips.
 * @param {string} statusCode Trip status
 * @returns {number}
 */
export function tripStepIndex(statusCode) {
  return TRIP_STEPS.findIndex((step) => step.status === statusCode)
}
