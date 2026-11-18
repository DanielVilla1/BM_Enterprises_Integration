// ===== AI GENERATED: employeeService =====
// Purpose: API client for employees, roles, sign-in links and driver licenses
// Inputs: plain objects matching the OpenAPI contract
// Returns: plain objects from the backend
// Flow:
// 1. Thin wrappers over apiClient; errors arrive normalized

import { apiClient } from '../shared/services/httpClient'

/**
 * @function listEmployees
 * @description Fetch employees (detail fields for Owner and HR).
 * @returns {Promise<Array<Object>>}
 */
export async function listEmployees() {
  const response = await apiClient.get('/employees', { params: { limit: 100 } })
  return response.data.items
}

/**
 * @function createEmployee
 * @description Add an employee record (starts inactive).
 * @param {{full_name: string, email: string, phone?: string}} employeePayload
 * @returns {Promise<Object>}
 */
export async function createEmployee(employeePayload) {
  const response = await apiClient.post('/employees', employeePayload)
  return response.data
}

/**
 * @function updateEmployee
 * @description Change name, email or phone.
 * @param {string} employeeIdentifier Employee id
 * @param {Object} changes Fields to change
 * @returns {Promise<Object>}
 */
export async function updateEmployee(employeeIdentifier, changes) {
  const response = await apiClient.patch(`/employees/${employeeIdentifier}`, changes)
  return response.data
}

/**
 * @function setEmployeeActive
 * @description Activate (Owner) or deactivate (Owner) an employee.
 * @param {string} employeeIdentifier Employee id
 * @param {boolean} shouldBeActive True to activate, false to deactivate
 * @returns {Promise<Object>}
 */
export async function setEmployeeActive(employeeIdentifier, shouldBeActive) {
  const action = shouldBeActive ? 'activate' : 'deactivate'
  const response = await apiClient.post(`/employees/${employeeIdentifier}/${action}`)
  return response.data
}

/**
 * @function assignEmployeeRoles
 * @description Replace an employee's roles; a reason lets the Owner override a forbidden pair.
 * @param {string} employeeIdentifier Employee id
 * @param {Array<string>} roleCodes Role codes
 * @param {string} [exceptionReason] Owner's reason for a forbidden combination
 * @returns {Promise<Object>}
 */
export async function assignEmployeeRoles(employeeIdentifier, roleCodes, exceptionReason) {
  const body = { role_codes: roleCodes }
  if (exceptionReason) body.exception_reason = exceptionReason
  const response = await apiClient.put(`/employees/${employeeIdentifier}/roles`, body)
  return response.data
}

/**
 * @function linkEmployeeIdentity
 * @description Link the employee to a Clerk sign-in account.
 * @param {string} employeeIdentifier Employee id
 * @param {string} clerkUserIdentifier Clerk user id
 * @returns {Promise<Object>}
 */
export async function linkEmployeeIdentity(employeeIdentifier, clerkUserIdentifier) {
  const response = await apiClient.put(`/employees/${employeeIdentifier}/identity`, {
    clerk_user_id: clerkUserIdentifier,
  })
  return response.data
}

/**
 * @function fetchDriverLicense
 * @description Read a driver license (full or validity-only depending on the caller's level).
 * @param {string} employeeIdentifier Employee id
 * @returns {Promise<Object>}
 */
export async function fetchDriverLicense(employeeIdentifier) {
  const response = await apiClient.get(`/employees/${employeeIdentifier}/driver-license`)
  return response.data
}

/**
 * @function saveDriverLicense
 * @description Save a driver's license number and expiry date.
 * @param {string} employeeIdentifier Employee id
 * @param {{license_number: string, expiry_date: string}} licensePayload
 * @returns {Promise<Object>}
 */
export async function saveDriverLicense(employeeIdentifier, licensePayload) {
  const response = await apiClient.put(`/employees/${employeeIdentifier}/driver-license`, licensePayload)
  return response.data
}
