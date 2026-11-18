// ===== AI GENERATED: truckService =====
// Purpose: API client for /trucks and maintenance
// Inputs: plain objects matching the OpenAPI contract
// Returns: plain objects from the backend
// Flow:
// 1. Thin wrappers over apiClient; errors arrive normalized

import { apiClient } from '../shared/services/httpClient'

/**
 * @function listTrucks
 * @description Fetch trucks.
 * @returns {Promise<Array<Object>>}
 */
export async function listTrucks() {
  const response = await apiClient.get('/trucks', { params: { limit: 100 } })
  return response.data.items
}

/**
 * @function createTruck
 * @description Register a truck.
 * @param {{plate_number: string, description?: string, capacity_tons: number}} truckPayload
 * @returns {Promise<Object>}
 */
export async function createTruck(truckPayload) {
  const response = await apiClient.post('/trucks', truckPayload)
  return response.data
}

/**
 * @function updateTruck
 * @description Change a truck's plate, description, capacity or retire it.
 * @param {string} truckIdentifier Truck id
 * @param {Object} changes Fields to change
 * @returns {Promise<Object>}
 */
export async function updateTruck(truckIdentifier, changes) {
  const response = await apiClient.patch(`/trucks/${truckIdentifier}`, changes)
  return response.data
}

/**
 * @function listMaintenance
 * @description A truck's maintenance history, newest first.
 * @param {string} truckIdentifier Truck id
 * @returns {Promise<Array<Object>>}
 */
export async function listMaintenance(truckIdentifier) {
  const response = await apiClient.get(`/trucks/${truckIdentifier}/maintenance`)
  return response.data
}

/**
 * @function startMaintenance
 * @description Put an available truck into maintenance.
 * @param {string} truckIdentifier Truck id
 * @param {string} maintenanceReason Why
 * @returns {Promise<Object>}
 */
export async function startMaintenance(truckIdentifier, maintenanceReason) {
  const response = await apiClient.post(`/trucks/${truckIdentifier}/maintenance`, {
    reason: maintenanceReason,
  })
  return response.data
}

/**
 * @function completeMaintenance
 * @description Return a truck from maintenance to available.
 * @param {string} truckIdentifier Truck id
 * @returns {Promise<Object>}
 */
export async function completeMaintenance(truckIdentifier) {
  const response = await apiClient.post(`/trucks/${truckIdentifier}/maintenance/complete`)
  return response.data
}
