// ===== AI GENERATED: tripService =====
// Purpose: API client for dispatch: trips, progress and resources
// Inputs: plain objects matching the OpenAPI contract
// Returns: plain objects from the backend
// Flow:
// 1. Thin wrappers over apiClient; errors arrive normalized

import { apiClient } from '../shared/services/httpClient'

/**
 * @function listTrips
 * @description All trips (Owner and Dispatcher).
 * @returns {Promise<Array<Object>>}
 */
export async function listTrips() {
  const response = await apiClient.get('/trips', { params: { limit: 100 } })
  return response.data.items
}

/**
 * @function listAssignedTrips
 * @description Trips where the signed-in employee is crew.
 * @returns {Promise<Array<Object>>}
 */
export async function listAssignedTrips() {
  const response = await apiClient.get('/trips/assigned', { params: { limit: 100 } })
  return response.data.items
}

/**
 * @function fetchDispatchResources
 * @description Trucks and crew with availability and the reason when unavailable.
 * @returns {Promise<{trucks: Array<Object>, drivers: Array<Object>, helpers: Array<Object>}>}
 */
export async function fetchDispatchResources() {
  const response = await apiClient.get('/dispatch/resources')
  return response.data
}

/**
 * @function assignTrip
 * @description Assign a truck and crew to an order.
 * @param {string} orderIdentifier Order id
 * @param {{truck_id: string, driver_id: string, helper_ids: Array<string>, load_tons: number}} assignment
 * @returns {Promise<Object>}
 */
export async function assignTrip(orderIdentifier, assignment) {
  const response = await apiClient.post(`/delivery-orders/${orderIdentifier}/trips`, assignment)
  return response.data
}

/**
 * @function runTripAction
 * @description Run a trip action that needs no body: accept, clear-dispatch, depart, deliver.
 * @param {string} tripIdentifier Trip id
 * @param {string} actionName One of accept, clear-dispatch, depart, deliver
 * @returns {Promise<Object>}
 */
export async function runTripAction(tripIdentifier, actionName) {
  const response = await apiClient.post(`/trips/${tripIdentifier}/${actionName}`)
  return response.data
}

/**
 * @function closeTrip
 * @description Cancel (before departure) or fail (after departure) a trip.
 * @param {string} tripIdentifier Trip id
 * @param {string} closeAction Either cancel or fail
 * @param {string} closeReason Why
 * @returns {Promise<Object>}
 */
export async function closeTrip(tripIdentifier, closeAction, closeReason) {
  const response = await apiClient.post(`/trips/${tripIdentifier}/${closeAction}`, {
    reason: closeReason,
  })
  return response.data
}
