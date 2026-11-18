// ===== AI GENERATED: formatting =====
// Purpose: Consistent date, weight, money and name formatting for every screen
// Inputs: ISO dates, numbers, names
// Returns: display strings
// Flow:
// 1. Dates are shown in the Philippine style; date-only values never shift by timezone
// 2. Money is Philippine pesos; weights are metric tons

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

const DATE_FORMAT = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
})
const DATE_TIME_FORMAT = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
})
const PESO_FORMAT = new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' })

/**
 * @function parseDateOnly
 * @description Parse YYYY-MM-DD as a local date (no timezone shift).
 * @param {string} isoDate Date string
 * @returns {Date}
 */
function parseDateOnly(isoDate) {
  const [year, month, day] = isoDate.split('-').map(Number)
  return new Date(year, month - 1, day)
}

/**
 * @function formatDate
 * @description Format a date-only value such as 2026-11-16.
 * @param {string|null} isoDate Date string
 * @returns {string}
 */
export function formatDate(isoDate) {
  return isoDate ? DATE_FORMAT.format(parseDateOnly(isoDate)) : '—'
}

/**
 * @function formatDateTime
 * @description Format an ISO timestamp in the viewer's timezone.
 * @param {string|null} isoTimestamp Timestamp string
 * @returns {string}
 */
export function formatDateTime(isoTimestamp) {
  return isoTimestamp ? DATE_TIME_FORMAT.format(new Date(isoTimestamp)) : '—'
}

/**
 * @function dateBlock
 * @description Month and day parts for a calendar tile.
 * @param {string} isoDate Date string
 * @returns {{month: string, day: string}}
 */
export function dateBlock(isoDate) {
  const parsed = parseDateOnly(isoDate)
  return {
    month: parsed.toLocaleString('en-US', { month: 'short' }).toUpperCase(),
    day: String(parsed.getDate()),
  }
}

/**
 * @function formatTons
 * @description Format a weight in metric tons.
 * @param {number|string} tons Weight
 * @returns {string}
 */
export function formatTons(tons) {
  return `${Number(tons).toLocaleString('en-US', { maximumFractionDigits: 3 })} t`
}

/**
 * @function formatPeso
 * @description Format an amount in Philippine pesos.
 * @param {number} amount Amount
 * @returns {string}
 */
export function formatPeso(amount) {
  return PESO_FORMAT.format(amount)
}

/**
 * @function initialsOf
 * @description Up to two initials for an avatar.
 * @param {string} fullName Person's name
 * @returns {string}
 */
export function initialsOf(fullName) {
  const parts = String(fullName ?? '')
    .trim()
    .split(/\s+/)
    .filter(Boolean)
  if (parts.length === 0) return '?'
  const first = parts[0].charAt(0)
  const last = parts.length > 1 ? parts[parts.length - 1].charAt(0) : ''
  return (first + last).toUpperCase()
}

/**
 * @function shortIdentifier
 * @description First characters of an id, for compact display.
 * @param {string|null} identifier Full id
 * @returns {string}
 */
export function shortIdentifier(identifier) {
  return identifier ? String(identifier).slice(0, 8) : '—'
}

/**
 * @function greetingFor
 * @description A time-of-day greeting.
 * @param {number} hour Hour of the day, 0 to 23
 * @returns {string}
 */
export function greetingFor(hour) {
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
}

/**
 * @function firstNameOf
 * @description The first word of a full name.
 * @param {string} fullName Person's name
 * @returns {string}
 */
export function firstNameOf(fullName) {
  return (
    String(fullName ?? '')
      .trim()
      .split(/\s+/)[0] ?? ''
  )
}
