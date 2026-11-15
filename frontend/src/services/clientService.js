// ===== AI GENERATED: clientService =====
// Purpose: API client for /clients
// Inputs: plain objects matching the OpenAPI contract
// Returns: plain objects from the backend
// Flow:
// 1. Thin wrappers over apiClient; errors arrive normalized

import { apiClient } from '../shared/services/httpClient'

/**
 * @function listClients
 * @description Fetch clients.
 * @returns {Promise<Array<Object>>}
 */
export async function listClients() {
  const response = await apiClient.get('/clients', { params: { limit: 100 } })
  return response.data.items
}

/**
 * @function createClient
 * @description Create a client.
 * @param {{name: string, address?: string, contact_person?: string, contact_phone?: string}} clientPayload
 * @returns {Promise<Object>}
 */
export async function createClient(clientPayload) {
  const response = await apiClient.post('/clients', clientPayload)
  return response.data
}

/**
 * @function updateClient
 * @description Change a client's details or activate/deactivate it.
 * @param {string} clientIdentifier Client id
 * @param {Object} changes Fields to change
 * @returns {Promise<Object>}
 */
export async function updateClient(clientIdentifier, changes) {
  const response = await apiClient.patch(`/clients/${clientIdentifier}`, changes)
  return response.data
}
