// ===== AI GENERATED: dispatch utilities =====
// Purpose: Pure helpers that decide which UI actions to offer for orders and trips
// Inputs: orders, trips, the signed-in employee id
// Returns: filtered lists, action descriptors, readable reasons
// Flow:
// 1. These only choose which buttons to show; the backend enforces every rule
// 2. Block reasons map backend codes to plain language

// AI MODIFIED: Combine crew membership with backend-confirmed capabilities.

/** Order statuses that can still receive trips. */
const CLOSED_ORDER_STATUSES = ['CANCELLED', 'COMPLETED']

/** Trip statuses before the truck departs. */
const PRE_DEPARTURE_TRIP_STATUSES = ['SCHEDULED', 'ACCEPTED', 'CLEARED_FOR_DISPATCH']

/** Trip statuses after departure where a failure can be recorded. */
const FAILABLE_TRIP_STATUSES = ['IN_TRANSIT', 'DELIVERED_OR_PENDING']

const BLOCK_REASON_TEXT = {
  ACCOUNT_NOT_LINKED: 'sign-in account not linked',
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
  if (tripRecord.status === 'CLEARED_FOR_DISPATCH')
    return { name: 'depart', label: 'Record departure' }
  if (tripRecord.status === 'IN_TRANSIT') return { name: 'deliver', label: 'Record delivery' }
  return null
}

/**
 * @function dispatcherActions
 * @description Dispatcher buttons that make sense for a trip's current status.
 * @param {{status: string}} tripRecord Trip
 * @returns {{canClear: boolean, canCancel: boolean, canFail: boolean, canChangeCrew: boolean, canReplaceTruck: boolean}}
 */
export function dispatcherActions(tripRecord) {
  return {
    canClear: tripRecord.status === 'ACCEPTED',
    canCancel: PRE_DEPARTURE_TRIP_STATUSES.includes(tripRecord.status),
    canFail: FAILABLE_TRIP_STATUSES.includes(tripRecord.status),
    canChangeCrew: PRE_DEPARTURE_TRIP_STATUSES.includes(tripRecord.status),
    canReplaceTruck:
      PRE_DEPARTURE_TRIP_STATUSES.includes(tripRecord.status) || tripRecord.status === 'IN_TRANSIT',
  }
}

/**
 * @function isCrewMember
 * @description True when the employee is the trip's driver or one of its helpers.
 * @param {{driver_id: string, helper_ids: Array<string>}} tripRecord Trip
 * @param {string} employeeIdentifier Signed-in employee id
 * @returns {boolean}
 */
export function isCrewMember(tripRecord, employeeIdentifier) {
  return (
    tripRecord.driver_id === employeeIdentifier ||
    tripRecord.helper_ids.includes(employeeIdentifier)
  )
}

/**
 * @function canUploadSignedOr
 * @description Crew may upload (or replace) the signed OR after delivery, until receipt is confirmed.
 * @param {Object} tripRecord Trip
 * @param {string} employeeIdentifier Signed-in employee id
 * @returns {boolean}
 */
export function canUploadSignedOr(tripRecord, employeeIdentifier) {
  return (
    isCrewMember(tripRecord, employeeIdentifier) &&
    ['DELIVERED_OR_PENDING', 'OR_UPLOADED'].includes(tripRecord.status)
  )
}

/**
 * @function canUploadStampedCopy
 * @description The optional stamped copy can follow the signed OR.
 * @param {Object} tripRecord Trip
 * @param {string} employeeIdentifier Signed-in employee id
 * @returns {boolean}
 */
export function canUploadStampedCopy(tripRecord, employeeIdentifier) {
  return (
    isCrewMember(tripRecord, employeeIdentifier) &&
    ['OR_UPLOADED', 'COMPLETED'].includes(tripRecord.status)
  )
}

/**
 * @function canConfirmReceipt
 * @description Only the assigned driver confirms receipt, once the signed OR is stored.
 * @param {Object} tripRecord Trip
 * @param {string} employeeIdentifier Signed-in employee id
 * @returns {boolean}
 */
export function canConfirmReceipt(tripRecord, employeeIdentifier) {
  return tripRecord.driver_id === employeeIdentifier && tripRecord.status === 'OR_UPLOADED'
}

/**
 * @function canCorrectConfirmation
 * @description A completed trip's confirmation can be reopened by the Owner.
 * @param {{status: string}} tripRecord Trip
 * @returns {boolean}
 */
export function canCorrectConfirmation(tripRecord) {
  return tripRecord.status === 'COMPLETED'
}

/**
 * @function describeDocumentKind
 * @description Readable name for an OR document kind.
 * @param {string} documentKind SIGNED_OR or STAMPED_COPY
 * @returns {string}
 */
export function describeDocumentKind(documentKind) {
  return documentKind === 'STAMPED_COPY' ? 'stamped copy' : 'signed OR'
}

/**
 * @function crewTripActions
 * @description Derive UI actions from ownership, trip state and current backend grants.
 * @param {{status: string, driver_id: string, helper_ids: Array<string>}} tripRecord Trip
 * @param {string} employeeIdentifier Signed-in employee
 * @param {Object<string, string>} capabilities Backend-confirmed grants
 * @returns {{progress: TripAction|null, uploadSigned: boolean, uploadStamped: boolean, confirmReceipt: boolean, viewDocuments: boolean}}
 */
export function crewTripActions(tripRecord, employeeIdentifier, capabilities) {
  const canUpload = capabilities['or.upload'] === 'OWN'
  return {
    progress:
      capabilities['trip.progress'] === 'OWN'
        ? crewProgressAction(tripRecord, employeeIdentifier)
        : null,
    uploadSigned: canUpload && canUploadSignedOr(tripRecord, employeeIdentifier),
    uploadStamped: canUpload && canUploadStampedCopy(tripRecord, employeeIdentifier),
    confirmReceipt:
      capabilities['or.confirm_receipt'] === 'OWN' &&
      canConfirmReceipt(tripRecord, employeeIdentifier),
    viewDocuments:
      capabilities['or.view_files'] !== undefined && isCrewMember(tripRecord, employeeIdentifier),
  }
}
