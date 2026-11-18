// ===== AI GENERATED: accountService =====
// Purpose: API client for the signed-in employee (/me)
// Inputs: none (bearer token added by httpClient)
// Returns: plain account object confirmed by the backend
// Flow:
// 1. GET /me
// 2. Return the body; failures arrive already normalized

import { apiClient, waitForApiStartup } from '../shared/services/httpClient'

/**
 * @typedef {Object} CurrentAccount
 * @property {string} employee_id
 * @property {string} full_name
 * @property {Array<string>} role_codes
 * @property {Object<string, string>} capabilities Capability name to access level
 */

/**
 * @function fetchCurrentAccount
 * @description Load the signed-in employee, roles and capability levels.
 * @returns {Promise<CurrentAccount>}
 */
export async function fetchCurrentAccount() {
  await waitForApiStartup()
  const response = await apiClient.get('/me')
  return response.data
}
