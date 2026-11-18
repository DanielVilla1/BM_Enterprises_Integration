// ===== AI GENERATED: people =====
// Purpose: Filters and labels for the People screen and the audit log
// Inputs: employees from the API, audit records, search text
// Returns: filtered lists and readable action names
// Flow:
// 1. Employees: status tabs and a search over name, email and roles
// 2. Audit: turn action codes into sentences people can read

import { matchesQuery } from './operations'
import { humanizeCode } from './statusLabels'
import { roleLabel } from './permissionMatrix'

/** Status tabs for the People screen. */
export const EMPLOYEE_TABS = [
  { key: 'all', label: 'Everyone' },
  { key: 'active', label: 'Active' },
  { key: 'inactive', label: 'Inactive' },
]

const AUDIT_ACTIONS = {
  'employee.created': 'Employee added',
  'employee.updated': 'Employee details changed',
  'employee.activated': 'Employee activated',
  'employee.deactivated': 'Employee deactivated',
  'employee.roles_changed': 'Roles changed',
  'employee.identity_linked': 'Sign-in account linked',
  'employee.bootstrap_owner': 'First Owner created',
  'driver_license.saved': 'Driver license saved',
  'client.created': 'Client added',
  'client.updated': 'Client changed',
  'truck.created': 'Truck registered',
  'truck.updated': 'Truck changed',
  'truck.maintenance_started': 'Maintenance started',
  'truck.maintenance_completed': 'Maintenance completed',
  'delivery_order.created': 'Order recorded',
  'delivery_order.updated': 'Order changed',
  'delivery_order.cancelled': 'Order cancelled',
  'trip.created': 'Trip assigned',
  'trip.accepted': 'Trip accepted by driver',
  'trip.dispatch_cleared': 'Trip cleared for dispatch',
  'trip.departed': 'Trip departed',
  'trip.delivered': 'Delivery recorded',
  'trip.cancelled': 'Trip cancelled',
  'trip.failed': 'Trip marked failed',
  'trip.crew_changed': 'Crew changed',
  'trip.truck_replaced': 'Truck replaced',
  'trip.receipt_confirmed': 'Receipt confirmed, trip completed',
  'trip.receipt_correction': 'Receipt confirmation corrected',
  'or_document.uploaded': 'OR document uploaded',
  'or_document.url_issued': 'OR document opened',
  'webhook.clerk.link_conflict': 'Sign-in link conflict',
}

/**
 * @function describeAuditAction
 * @description A readable sentence for an audit action code.
 * @param {string} actionCode Code such as trip.created
 * @returns {string}
 */
export function describeAuditAction(actionCode) {
  return AUDIT_ACTIONS[actionCode] ?? humanizeCode(actionCode)
}

/**
 * @function filterEmployees
 * @description Employees for a status tab and a search text.
 * @param {Array<Object>} employees Employees from the API
 * @param {string} tabKey One of EMPLOYEE_TABS keys
 * @param {string} query Search text
 * @returns {Array<Object>}
 */
export function filterEmployees(employees, tabKey, query) {
  return employees.filter((employeeRecord) => {
    if (tabKey === 'active' && !employeeRecord.is_active) return false
    if (tabKey === 'inactive' && employeeRecord.is_active) return false
    return matchesQuery(
      [employeeRecord.full_name, employeeRecord.email, ...employeeRecord.role_codes.map(roleLabel)],
      query,
    )
  })
}

/**
 * @function filterAuditRecords
 * @description Audit records matching a search over the readable action, entity type and trace id.
 * @param {Array<Object>} records Audit records
 * @param {string} query Search text
 * @returns {Array<Object>}
 */
export function filterAuditRecords(records, query) {
  return records.filter((record) =>
    matchesQuery([describeAuditAction(record.action), record.action, record.entity_type, record.trace_id], query),
  )
}
