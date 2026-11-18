// ===== AI GENERATED: finance_ui_rules =====
// Purpose: Pure financial UI permissions, field serialization and display helpers.
// Inputs: Backend-confirmed capabilities and form strings.
// Returns: UI hints and payloads; no money is calculated in the browser.
// Flow: Keep money as strings; give each action the minimal strict API payload.

/** @param {Object<string,string>} capabilities Grants from /me. @returns {Object<string,boolean>} UI hints. */
export function financePermissions(capabilities) {
  const full = (name) => capabilities[name] === 'FULL'
  return {
    enter: ['FULL', 'OWN'].includes(capabilities['expense.enter']),
    review: full('expense.approve'),
    charge: full('charge.finalize'),
    calculate: full('earnings.calculate'),
    rates: full('earning_percentage.set'),
    prepare: full('payroll.prepare'),
    reverse: full('payroll.reverse'),
    adjust: full('deduction.record'),
    creditAdjustment: full('payroll_adjustment.prepare'),
    approveAdjustment: full('deduction.approve'),
    pay: full('payroll_payment.record'),
    request: ['FULL', 'OWN'].includes(capabilities['cash_advance.request']),
    approveAdvance: full('cash_advance.approval_action'),
    release: full('cash_advance.release_repay'),
    delegate: full('cash_advance.approve'),
    bill: full('billing.manage'),
    voidInvoice: full('invoice.void_approve'),
  }
}

/** @param {string} employeeId Signed-in employee. @param {Array<string|null>} excluded Involved people. @returns {boolean} Independent UI hint. */
export function independentReviewer(employeeId, excluded) {
  return !excluded.includes(employeeId)
}

/** @param {Object<string,string>} fields Form values. @param {Array<string>} names Monetary field names. @returns {Object} String-preserving values. */
export function financialPayload(fields, names = ['amount']) {
  const payload = { ...fields }
  for (const name of names) if (name in payload) payload[name] = String(payload[name]).trim()
  return payload
}

/** @param {string} identifier UUID. @returns {string} Short display reference. */
export function financeReference(identifier) {
  return identifier ? identifier.slice(0, 8).toUpperCase() : '—'
}

/** @returns {string} Current Manila business date. */
export function financialToday() {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Manila',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date())
}

/** @param {Object} fields Submitted expense-line strings. @param {Array<Object>} sheets Current expense sheets. @returns {Object} Validated API shape without UI identifiers. */
export function expenseLinePayload(fields, sheets) {
  const { trip_id: tripId, reason, ...line } = fields
  const previous = sheets.find((sheet) => sheet.trip_id === tripId)
  return { lines: [...(previous?.lines ?? []), line], declared_zero: false, reason }
}

/** @param {Array<Object>} people Authorized name list. @param {string} employeeId Employee id. @returns {string} Safe display label. */
export function financialPerson(people, employeeId) {
  return (
    people.find((person) => person.record_id === employeeId)?.name ?? financeReference(employeeId)
  )
}
