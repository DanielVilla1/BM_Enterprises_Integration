// ===== AI GENERATED: orService =====
// Purpose: API client for OR documents, receipt confirmation and correction
// Inputs: files, trip ids, idempotency keys
// Returns: plain objects from the backend
// Flow:
// 1. Upload as multipart; the browser sets the boundary header itself
// 2. Confirmation always carries an Idempotency-Key so retries are safe
// 3. Signed URLs are fetched on demand and are short-lived

import { apiClient } from '../shared/services/httpClient'

/**
 * @function uploadOrDocument
 * @description Upload a signed OR (or optional stamped copy) for a trip.
 * @param {string} tripIdentifier Trip id
 * @param {File} imageFile JPEG or PNG file chosen by the user
 * @param {string} documentKind SIGNED_OR or STAMPED_COPY
 * @returns {Promise<Object>}
 */
export async function uploadOrDocument(tripIdentifier, imageFile, documentKind) {
  const formPayload = new FormData()
  formPayload.append('file', imageFile)
  formPayload.append('kind', documentKind)
  const response = await apiClient.post(`/trips/${tripIdentifier}/or-documents`, formPayload)
  return response.data
}

/**
 * @function fetchOrDocumentUrl
 * @description Ask the backend for a short-lived signed URL to a stored document.
 * @param {string} tripIdentifier Trip id
 * @param {string} documentIdentifier Document id
 * @returns {Promise<{url: string, expires_in_seconds: number}>}
 */
export async function fetchOrDocumentUrl(tripIdentifier, documentIdentifier) {
  const response = await apiClient.get(
    `/trips/${tripIdentifier}/or-documents/${documentIdentifier}/url`,
  )
  // AI MODIFIED: Fictional local presentation images still require the caller's bearer token.
  if (/^\/api\/v1\/finance\/presentation-documents\/[0-9a-f-]{36}$/i.test(response.data.url)) {
    const imageResponse = await apiClient.get(response.data.url.slice('/api/v1'.length), {
      responseType: 'blob',
    })
    const imageUrl = URL.createObjectURL(imageResponse.data)
    setTimeout(() => URL.revokeObjectURL(imageUrl), response.data.expires_in_seconds * 1000)
    return { ...response.data, url: imageUrl }
  }
  return response.data
}

/**
 * @function confirmReceipt
 * @description The assigned driver confirms the steel company received the OR.
 * @param {string} tripIdentifier Trip id
 * @param {string} receivedAtIso Reported receipt time, ISO 8601 with offset
 * @param {string} idempotencyKey Stable key for this confirmation attempt
 * @returns {Promise<Object>}
 */
export async function confirmReceipt(tripIdentifier, receivedAtIso, idempotencyKey) {
  const response = await apiClient.post(
    `/trips/${tripIdentifier}/confirm-receipt`,
    { received_at: receivedAtIso },
    { headers: { 'Idempotency-Key': idempotencyKey } },
  )
  return response.data
}

/**
 * @function correctConfirmation
 * @description Owner reopens a mistaken confirmation.
 * @param {string} tripIdentifier Trip id
 * @param {string} correctionReason Why
 * @returns {Promise<Object>}
 */
export async function correctConfirmation(tripIdentifier, correctionReason) {
  const response = await apiClient.post(`/trips/${tripIdentifier}/receipt-correction`, {
    reason: correctionReason,
  })
  return response.data
}
