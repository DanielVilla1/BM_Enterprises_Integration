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
