// ===== AI GENERATED: normalizeApiError =====
// Purpose: Turn any request failure into one predictable error shape
// Inputs: an axios-style error (response may carry problem+json)
// Returns: plain object { status, code, title, detail, traceIdentifier, fieldErrors }
// Flow:
// 1. Read the RFC 9457 body when the server sent one
// 2. Fall back to a generic network failure shape

/**
 * @typedef {Object} ApiFailure
 * @property {number} status HTTP status, 0 when the server was unreachable
 * @property {string} code Stable machine-readable error code
 * @property {string} title Short human title
 * @property {string} detail Human explanation (never internal details)
 * @property {string} traceIdentifier Server trace id for support
 * @property {Array<{field: string, message: string}>} fieldErrors Validation errors
 */

/**
 * @function normalizeApiError
 * @description Convert a thrown request error into an ApiFailure.
 * @param {Object} requestError
 * @returns {ApiFailure}
 */
export function normalizeApiError(requestError) {
  const responseBody = requestError?.response?.data
  const responseStatus = requestError?.response?.status
  if (responseStatus === undefined || responseBody === null || typeof responseBody !== 'object') {
    return {
      status: responseStatus ?? 0,
      code: 'NETWORK_ERROR',
      title: 'Service unreachable',
      detail: 'The server could not be reached. Check your connection and try again.',
      traceIdentifier: '',
      fieldErrors: [],
    }
  }
  return {
    status: responseStatus,
    code: String(responseBody.code ?? 'UNKNOWN_ERROR'),
    title: String(responseBody.title ?? 'Request failed'),
    detail: String(responseBody.detail ?? 'The request failed.'),
    traceIdentifier: String(responseBody.trace_id ?? ''),
    fieldErrors: Array.isArray(responseBody.errors) ? responseBody.errors : [],
  }
}
