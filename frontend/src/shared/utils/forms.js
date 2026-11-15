// ===== AI GENERATED: compactPayload =====
// Purpose: Turn form values into an API payload without empty optional fields
// Inputs: a plain object of form values
// Returns: a new object without empty-string, null or undefined values
// Flow:
// 1. Trim strings
// 2. Drop values that are empty after trimming

/**
 * @function compactPayload
 * @description Remove empty optional values so the API receives only what was entered.
 * @param {Object} formValues Raw values read from a form
 * @returns {Object}
 */
export function compactPayload(formValues) {
  const compacted = {}
  for (const [fieldName, fieldValue] of Object.entries(formValues)) {
    const normalized = typeof fieldValue === 'string' ? fieldValue.trim() : fieldValue
    if (normalized !== '' && normalized !== null && normalized !== undefined) {
      compacted[fieldName] = normalized
    }
  }
  return compacted
}

/** Largest upload the backend accepts (5 MB). */
export const MAXIMUM_UPLOAD_BYTES = 5 * 1024 * 1024

/**
 * @function isUploadTooLarge
 * @description True when a chosen file is over the upload limit (the backend still enforces it).
 * @param {{size: number}} chosenFile File from an input
 * @returns {boolean}
 */
export function isUploadTooLarge(chosenFile) {
  return chosenFile.size > MAXIMUM_UPLOAD_BYTES
}

/**
 * @function toLocalInputValue
 * @description Format a date for a datetime-local input (local time, minutes precision).
 * @param {Date} moment Date to format
 * @returns {string}
 */
export function toLocalInputValue(moment) {
  const pad = (number) => String(number).padStart(2, '0')
  return (
    `${moment.getFullYear()}-${pad(moment.getMonth() + 1)}-${pad(moment.getDate())}` +
    `T${pad(moment.getHours())}:${pad(moment.getMinutes())}`
  )
}

/**
 * @function localInputToIso
 * @description Convert a datetime-local value to an ISO 8601 string with a UTC offset.
 * @param {string} localValue Value from a datetime-local input
 * @returns {string}
 */
export function localInputToIso(localValue) {
  return new Date(localValue).toISOString()
}
