// ===== AI GENERATED: administrationService =====
// Purpose: API client for the Owner's audit log and permission matrix views
// Inputs: page bounds
// Returns: plain objects from the backend
// Flow:
// 1. Thin wrappers over apiClient; errors arrive normalized

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { apiClient } from '../shared/services/httpClient'

export const AUDIT_PAGE_SIZE = 50

/**
 * @function fetchAuditPage
 * @description One page of audit records, newest first.
 * @param {number} offset Records to skip
 * @returns {Promise<Array<Object>>}
 */
export async function fetchAuditPage(offset) {
  const response = await apiClient.get('/audit-logs', {
    params: { limit: AUDIT_PAGE_SIZE, offset },
  })
  return response.data.items
}

/**
 * @function fetchPermissionGrants
 * @description Every cell of the permission matrix.
 * @returns {Promise<Array<Object>>}
 */
export async function fetchPermissionGrants() {
  const response = await apiClient.get('/permission-matrix')
  return response.data.grants
}
