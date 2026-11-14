// ===== AI GENERATED: dispatch utilities =====
// Purpose: Pure helpers that decide which UI actions to offer for orders and trips
// Inputs: orders, trips, the signed-in employee id
// Returns: filtered lists, action descriptors, readable reasons
// Flow:
// 1. These only choose which buttons to show; the backend enforces every rule
// 2. Block reasons map backend codes to plain language

/** Order statuses that can still receive trips. */
const CLOSED_ORDER_STATUSES = ['CANCELLED', 'COMPLETED']

/** Trip statuses before the truck departs. */
const PRE_DEPARTURE_TRIP_STATUSES = ['SCHEDULED', 'ACCEPTED', 'CLEARED_FOR_DISPATCH']

/** Trip statuses after departure where a failure can be recorded. */
const FAILABLE_TRIP_STATUSES = ['IN_TRANSIT', 'DELIVERED_OR_PENDING']

const BLOCK_REASON_TEXT = {
  MAINTENANCE: 'in maintenance',
  IN_PROGRESS_TRIP: 'already on a trip',
  LICENSE_EXPIRED: 'license expired',
  LICENSE_MISSING: 'no license on record',
}

/**
 * @function assignableOrders
 * @description Orders that are neither cancelled nor completed.
 * @param {Array<{status: string}>} orders Delivery orders
 * @returns {Array<Object>}
 */
export function assignableOrders(orders) {
  return orders.filter((orderRecord) => !CLOSED_ORDER_STATUSES.includes(orderRecord.status))
}

/**
 * @function describeBlockReason
 * @description Plain-language text for a backend availability reason code.
 * @param {string|null} reasonCode Reason from /dispatch/resources
 * @returns {string}
 */
export function describeBlockReason(reasonCode) {
  if (!reasonCode) return ''
  return BLOCK_REASON_TEXT[reasonCode] ?? 'unavailable'
}

/**
 * @typedef {Object} TripAction
 * @property {string} name API action name
 * @property {string} label Button text
 */

/**
 * @function crewProgressAction
 * @description The next step the assigned driver can take, or null.
 * @param {{status: string, driver_id: string}} tripRecord Trip
 * @param {string} employeeIdentifier Signed-in employee id
 * @returns {TripAction|null}
 */
export function crewProgressAction(tripRecord, employeeIdentifier) {
  if (tripRecord.driver_id !== employeeIdentifier) return null
  if (tripRecord.status === 'SCHEDULED') return { name: 'accept', label: 'Accept trip' }
  if (tripRecord.status === 'CLEARED_FOR_DISPATCH') return { name: 'depart', label: 'Record departure' }
  if (tripRecord.status === 'IN_TRANSIT') return { name: 'deliver', label: 'Record delivery' }
  return null
}

/**
 * @function dispatcherActions
 * @description Dispatcher buttons that make sense for a trip's current status.
 * @param {{status: string}} tripRecord Trip
 * @returns {{canClear: boolean, canCancel: boolean, canFail: boolean}}
 */
export function dispatcherActions(tripRecord) {
  return {
    canClear: tripRecord.status === 'ACCEPTED',
    canCancel: PRE_DEPARTURE_TRIP_STATUSES.includes(tripRecord.status),
    canFail: FAILABLE_TRIP_STATUSES.includes(tripRecord.status),
  }
}
