// ===== AI GENERATED: orderService =====
// Purpose: API client for /delivery-orders
// Inputs: plain objects matching the OpenAPI contract
// Returns: plain objects from the backend
// Flow:
// 1. Thin wrappers over apiClient; errors arrive normalized

import { apiClient } from '../shared/services/httpClient'

/**
 * @function listOrders
 * @description Fetch delivery orders, newest schedule first.
 * @returns {Promise<Array<Object>>}
 */
export async function listOrders() {
  const response = await apiClient.get('/delivery-orders', { params: { limit: 100 } })
  return response.data.items
}

/**
 * @function createOrder
 * @description Encode a new delivery order.
 * @param {Object} orderPayload Fields of DeliveryOrderCreateRequest
 * @returns {Promise<Object>}
 */
export async function createOrder(orderPayload) {
  const response = await apiClient.post('/delivery-orders', orderPayload)
  return response.data
}

/**
 * @function cancelOrder
 * @description Cancel a pending delivery order.
 * @param {string} orderIdentifier Order id
 * @param {string} cancelReason Why it is cancelled
 * @returns {Promise<Object>}
 */
export async function cancelOrder(orderIdentifier, cancelReason) {
  const response = await apiClient.post(`/delivery-orders/${orderIdentifier}/cancel`, {
    reason: cancelReason,
  })
  return response.data
}
