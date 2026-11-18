// ===== AI GENERATED: financeService =====
// Purpose: Authenticated finance queries and commands with caller-owned retry keys.
// Inputs: Section, bounded page, strict payload and idempotency key.
// Returns: Public API DTOs; server remains the authority for all amounts and grants.
// Flow: Route all network access through the existing authenticated HTTP adapter.

import { apiClient } from '../shared/services/httpClient'

/**
 * @param {string} section Workspace name.
 * @param {number} offset Record offset.
 * @param {AbortSignal} signal Cancellation signal.
 * @returns {Promise<Object>} Authorized workspace.
 */
export async function readFinanceWorkspace(section, offset, signal) {
  const response = await apiClient.get(`/finance/${section}`, {
    params: { limit: 50, offset },
    signal,
  })
  return response.data
}

/**
 * @param {string} path Relative financial command path.
 * @param {Object} payload Strict command fields.
 * @param {string} retryKey Stable key retained until a successful refresh.
 * @returns {Promise<Object>} Saved command result.
 */
export async function submitFinanceCommand(path, payload, retryKey) {
  const response = await apiClient.post(`/finance${path}`, payload, {
    headers: { 'Idempotency-Key': retryKey },
  })
  return response.data
}
