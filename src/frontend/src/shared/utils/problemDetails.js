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
  if (responseStatus === undefined) {
    const timedOut = ['ECONNABORTED', 'ETIMEDOUT'].includes(requestError?.code)
    return {
      status: 0,
      code: timedOut ? 'REQUEST_TIMEOUT' : 'NETWORK_ERROR',
      title: timedOut ? 'Connection timed out' : 'Service unreachable',
      detail: timedOut
        ? 'The service took too long to respond. Please try again.'
        : 'A connection to the service could not be established. Please try again.',
      traceIdentifier: '',
      fieldErrors: [],
    }
  }
  if (responseBody === null || typeof responseBody !== 'object' || Array.isArray(responseBody)) {
    const temporarilyUnavailable = [502, 503, 504].includes(responseStatus)
    return {
      status: responseStatus,
      code: responseStatus >= 400 ? 'HTTP_ERROR' : 'UNEXPECTED_RESPONSE',
      title: temporarilyUnavailable
        ? 'Service temporarily unavailable'
        : 'Unexpected server response',
      detail: temporarilyUnavailable
        ? 'The service is temporarily unavailable. Please try again shortly.'
        : 'The service returned an unexpected response. Please try again.',
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
