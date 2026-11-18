// ===== AI GENERATED: design_preview_fixtures =====
// Purpose: Fake sample data for designing every screen without a backend
// Inputs: none (all values are invented)
// Returns: records for every screen, roles with real capability names, load-state helpers
// Flow:
// 1. Records cover every status so each visual state can be seen
// 2. Role capabilities mirror the real permission matrix, so navigation matches production
// 3. loadStateView turns a chosen state into the props the panels expect

export const CLIENTS = [
  { client_id: 'client-1', name: 'Luzon Steel Corporation', address: 'Plant Road 1, Bulacan', contact_person: 'Ana Reyes', contact_phone: '0917 000 0001', is_active: true, created_at: '2026-10-01T08:00:00Z' },
  { client_id: 'client-2', name: 'Visayas Rebar Works', address: 'Port Area, Cebu', contact_person: 'Marco Dela Cruz', contact_phone: '0917 000 0002', is_active: true, created_at: '2026-10-05T08:00:00Z' },
  { client_id: 'client-3', name: 'Old Client Trading', address: null, contact_person: null, contact_phone: null, is_active: false, created_at: '2026-09-01T08:00:00Z' },
]

const orderBase = { client_reference: null, notes: null, cancellation_reason: null, created_at: '2026-11-10T08:00:00Z' }

export const ORDERS = [
  { ...orderBase, order_id: 'order-1', client_id: 'client-1', client_reference: 'PO-1042', pickup_location: 'Plant gate 4, Bulacan', delivery_location: 'Warehouse 7, Subic Freeport', scheduled_date: '2026-11-16', total_weight_tons: 60, status: 'PENDING' },
  { ...orderBase, order_id: 'order-2', client_id: 'client-1', pickup_location: 'Plant gate 2, Bulacan', delivery_location: 'Yard B, Batangas Port', scheduled_date: '2026-11-17', total_weight_tons: 48.5, status: 'PARTIALLY_ASSIGNED' },
  { ...orderBase, order_id: 'order-3', client_id: 'client-2', pickup_location: 'Mill 3, Cebu', delivery_location: 'Site 12, Mandaue', scheduled_date: '2026-11-18', total_weight_tons: 25, status: 'SCHEDULED' },
  { ...orderBase, order_id: 'order-4', client_id: 'client-2', pickup_location: 'Mill 3, Cebu', delivery_location: 'Site 4, Lapu-Lapu', scheduled_date: '2026-11-15', total_weight_tons: 40, status: 'IN_PROGRESS' },
  { ...orderBase, order_id: 'order-5', client_id: 'client-1', pickup_location: 'Plant gate 4, Bulacan', delivery_location: 'Warehouse 1, Manila', scheduled_date: '2026-11-12', total_weight_tons: 30, status: 'COMPLETED' },
  { ...orderBase, order_id: 'order-6', client_id: 'client-3', pickup_location: 'Plant gate 1, Bulacan', delivery_location: 'Warehouse 9, Manila', scheduled_date: '2026-11-14', total_weight_tons: 20, status: 'CANCELLED', cancellation_reason: 'Client withdrew the request' },
]

const truckBase = { created_at: '2026-09-01T08:00:00Z', is_active: true }

export const TRUCKS = [
  { ...truckBase, truck_id: 'truck-1', plate_number: 'ABC 1234', description: '10-wheeler', capacity_tons: 25, status: 'AVAILABLE' },
  { ...truckBase, truck_id: 'truck-2', plate_number: 'DEF 5678', description: '12-wheeler', capacity_tons: 30, status: 'ASSIGNED' },
  { ...truckBase, truck_id: 'truck-3', plate_number: 'GHI 9012', description: '10-wheeler', capacity_tons: 25, status: 'IN_TRANSIT' },
  { ...truckBase, truck_id: 'truck-4', plate_number: 'JKL 3456', description: 'Wing van', capacity_tons: 15, status: 'MAINTENANCE' },
  { ...truckBase, truck_id: 'truck-5', plate_number: 'MNO 7890', description: null, capacity_tons: 20, status: 'AVAILABLE', is_active: false },
]

const sampleDocument = (documentId, tripId, kind) => ({
  document_id: documentId,
  trip_id: tripId,
  kind,
  content_type: 'image/jpeg',
  size_bytes: 420000,
  uploaded_at: '2026-11-15T10:00:00Z',
  superseded: false,
})

const tripBase = {
  order_id: 'order-2',
  truck_id: 'truck-1',
  driver_id: 'driver-1',
  helper_ids: ['helper-1'],
  scheduled_date: '2026-11-17',
  pickup_location: 'Plant gate 2, Bulacan',
  delivery_location: 'Yard B, Batangas Port',
  load_tons: 20,
  accepted_at: null,
  cleared_at: null,
  departed_at: null,
  delivered_at: null,
  closed_reason: null,
  created_at: '2026-11-14T08:00:00Z',
  or_uploaded_at: null,
  receipt_confirmed_at: null,
  receipt_received_at: null,
  documents: [],
}

export const TRIPS = [
  { ...tripBase, trip_id: 'trip-1', status: 'SCHEDULED' },
  { ...tripBase, trip_id: 'trip-2', status: 'ACCEPTED', order_id: 'order-1', truck_id: 'truck-2', delivery_location: 'Warehouse 7, Subic Freeport', load_tons: 25 },
  { ...tripBase, trip_id: 'trip-3', status: 'CLEARED_FOR_DISPATCH', order_id: 'order-3', truck_id: 'truck-3', delivery_location: 'Site 12, Mandaue', load_tons: 25 },
  { ...tripBase, trip_id: 'trip-4', status: 'IN_TRANSIT', order_id: 'order-4', truck_id: 'truck-3', delivery_location: 'Site 4, Lapu-Lapu', load_tons: 20 },
  { ...tripBase, trip_id: 'trip-5', status: 'DELIVERED_OR_PENDING', order_id: 'order-5', delivery_location: 'Warehouse 1, Manila', load_tons: 30 },
  {
    ...tripBase,
    trip_id: 'trip-6',
    status: 'OR_UPLOADED',
    order_id: 'order-5',
    delivery_location: 'Warehouse 1, Manila',
    load_tons: 30,
    documents: [sampleDocument('doc-1', 'trip-6', 'SIGNED_OR')],
  },
  {
    ...tripBase,
    trip_id: 'trip-7',
    status: 'COMPLETED',
    order_id: 'order-5',
    delivery_location: 'Warehouse 1, Manila',
    load_tons: 30,
    documents: [sampleDocument('doc-2', 'trip-7', 'SIGNED_OR'), sampleDocument('doc-3', 'trip-7', 'STAMPED_COPY')],
  },
  { ...tripBase, trip_id: 'trip-8', status: 'SCHEDULED', driver_id: 'driver-9', helper_ids: ['driver-1'] },
]

export const RESOURCES = {
  trucks: [
    { resource_id: 'truck-1', name: 'ABC 1234', can_receive_assignment: true, reason: null, blocking_trip_id: null, capacity_tons: 25 },
    { resource_id: 'truck-2', name: 'DEF 5678', can_receive_assignment: false, reason: 'IN_PROGRESS_TRIP', blocking_trip_id: 'trip-2', capacity_tons: 30 },
    { resource_id: 'truck-3', name: 'GHI 9012', can_receive_assignment: false, reason: 'IN_PROGRESS_TRIP', blocking_trip_id: 'trip-4', capacity_tons: 25 },
    { resource_id: 'truck-4', name: 'JKL 3456', can_receive_assignment: false, reason: 'MAINTENANCE', blocking_trip_id: null, capacity_tons: 15 },
  ],
  drivers: [
    { resource_id: 'driver-1', name: 'Juan Santos', can_receive_assignment: true, reason: null, blocking_trip_id: null, capacity_tons: null },
    { resource_id: 'driver-2', name: 'Pedro Lim', can_receive_assignment: false, reason: 'LICENSE_EXPIRED', blocking_trip_id: null, capacity_tons: null },
    { resource_id: 'driver-9', name: 'Luis Tan', can_receive_assignment: true, reason: null, blocking_trip_id: null, capacity_tons: null },
  ],
  helpers: [
    { resource_id: 'helper-1', name: 'Mario Cruz', can_receive_assignment: true, reason: null, blocking_trip_id: null, capacity_tons: null },
    { resource_id: 'helper-2', name: 'Ramon Diaz', can_receive_assignment: true, reason: null, blocking_trip_id: null, capacity_tons: null },
  ],
}

export const EMPTY_RESOURCES = { trucks: [], drivers: [], helpers: [] }

export const EMPLOYEES = [
  { employee_id: 'owner-1', full_name: 'Olive Owner', email: 'olive@bm-demo.example', phone: '0917 100 0001', is_active: true, has_account: true, role_codes: ['OWNER'], created_at: '2026-09-01T08:00:00Z' },
  { employee_id: 'dispatcher-1', full_name: 'Dee Dispatcher', email: 'dee@bm-demo.example', phone: null, is_active: true, has_account: true, role_codes: ['DISPATCHER'], created_at: '2026-09-02T08:00:00Z' },
  { employee_id: 'driver-1', full_name: 'Juan Santos', email: 'juan@bm-demo.example', phone: '0917 100 0003', is_active: true, has_account: true, role_codes: ['DRIVER'], created_at: '2026-09-03T08:00:00Z' },
  { employee_id: 'driver-2', full_name: 'Pedro Lim', email: 'pedro@bm-demo.example', phone: null, is_active: true, has_account: true, role_codes: ['DRIVER'], created_at: '2026-09-03T08:00:00Z' },
  { employee_id: 'helper-1', full_name: 'Mario Cruz', email: 'mario@bm-demo.example', phone: null, is_active: true, has_account: false, role_codes: ['HELPER'], created_at: '2026-09-04T08:00:00Z' },
  { employee_id: 'new-1', full_name: 'Hana Hernandez', email: 'hana@bm-demo.example', phone: null, is_active: false, has_account: false, role_codes: [], created_at: '2026-11-13T08:00:00Z' },
]

export const AUDIT_RECORDS = [
  { audit_id: 'a1', occurred_at: '2026-11-15T09:42:00Z', actor_employee_id: 'driver-1-aaaa', action: 'trip.receipt_confirmed', entity_type: 'trip', entity_id: 'trip-7-1234', details: { stamped_copy: true }, trace_id: '4d1b8c0a77e25f31' },
  { audit_id: 'a2', occurred_at: '2026-11-15T09:10:00Z', actor_employee_id: 'driver-1-aaaa', action: 'or_document.uploaded', entity_type: 'trip', entity_id: 'trip-7-1234', details: { kind: 'SIGNED_OR' }, trace_id: '9f3c1a7e2b4d4e0f' },
  { audit_id: 'a3', occurred_at: '2026-11-15T08:30:00Z', actor_employee_id: 'dispatcher-1-bbbb', action: 'trip.dispatch_cleared', entity_type: 'trip', entity_id: 'trip-3-5678', details: {}, trace_id: '5a6b7c8d9e0f1a2b' },
  { audit_id: 'a4', occurred_at: '2026-11-14T16:05:00Z', actor_employee_id: 'owner-1-cccc', action: 'employee.roles_changed', entity_type: 'employee', entity_id: 'driver-2-9999', details: { before: ['HELPER'], after: ['DRIVER'] }, trace_id: '1a2b3c4d5e6f7a8b' },
  { audit_id: 'a5', occurred_at: '2026-11-14T11:20:00Z', actor_employee_id: 'dispatcher-1-bbbb', action: 'trip.created', entity_type: 'trip', entity_id: 'trip-1-2468', details: {}, trace_id: '8b7a6f5e4d3c2b1a' },
  { audit_id: 'a6', occurred_at: '2026-11-13T10:00:00Z', actor_employee_id: null, action: 'employee.identity_linked', entity_type: 'employee', entity_id: 'helper-1-1357', details: { source: 'clerk_webhook' }, trace_id: null },
]

export const MAINTENANCE_RECORDS = [
  { record_id: 'm1', truck_id: 'truck-4', reason: 'Brake pads worn', started_at: '2026-11-13T08:00:00Z', ended_at: null },
  { record_id: 'm2', truck_id: 'truck-4', reason: 'Oil change and filters', started_at: '2026-09-20T08:00:00Z', ended_at: '2026-09-21T15:00:00Z' },
]

/**
 * @function grantsFrom
 * @description Build permission-matrix grants from the role capability maps below.
 * @param {Object<string, {roleCode: string, capabilities: Object<string, string>}>} roles Preview roles
 * @returns {Array<{capability: string, role_code: string, access_level: string}>}
 */
function grantsFrom(roles) {
  return Object.values(roles).flatMap((role) =>
    Object.entries(role.capabilities).map(([capability, accessLevel]) => ({
      capability,
      role_code: role.roleCode,
      access_level: accessLevel,
    })),
  )
}

export const ROLES = {
  dispatcher: {
    label: 'Dispatcher',
    roleCode: 'DISPATCHER',
    employeeIdentifier: 'dispatcher-1',
    account: { employee_id: 'dispatcher-1', full_name: 'Dee Dispatcher', role_codes: ['DISPATCHER'] },
    capabilities: { 'dispatch.assign': 'FULL', 'delivery_order.manage': 'FULL', 'truck.manage': 'VIEW', 'driver_license.view': 'LTD', 'employee.manage': 'LTD', 'trip.assignment_view': 'VIEW', 'trip.progress': 'VIEW', 'or.upload': 'VIEW', 'or.view_files': 'VIEW', 'expense.enter': 'FULL', 'report.view': 'FULL', 'truck.replace': 'FULL', 'trip.cancel_or_fail': 'FULL' },
  },
  owner: {
    label: 'Owner / Manager',
    roleCode: 'OWNER',
    employeeIdentifier: 'owner-1',
    account: { employee_id: 'owner-1', full_name: 'Olive Owner', role_codes: ['OWNER'] },
    capabilities: { 'dispatch.assign': 'FULL', 'delivery_order.manage': 'VIEW', 'truck.manage': 'FULL', 'driver_license.view': 'FULL', 'employee.manage': 'FULL', 'employee.activate': 'FULL', 'trip.assignment_view': 'VIEW', 'or.view_files': 'VIEW', 'or.correct_confirmation': 'FULL', 'expense.enter': 'FULL', 'expense.approve': 'FULL', 'payroll.view_others': 'FULL', 'deduction.record': 'FULL', 'cash_advance.approve': 'FULL', 'billing.manage': 'VIEW', 'report.view': 'FULL', 'audit_user.manage': 'FULL', 'truck.replace': 'FULL', 'trip.cancel_or_fail': 'FULL' },
  },
  fleet: {
    label: 'Fleet Manager',
    roleCode: 'FLEET_MANAGER',
    employeeIdentifier: 'fleet-1',
    account: { employee_id: 'fleet-1', full_name: 'Fe Fleet', role_codes: ['FLEET_MANAGER'] },
    capabilities: { 'truck.manage': 'FULL', 'driver_license.view': 'FULL', 'employee.manage': 'LTD', 'report.view': 'FULL' },
  },
  driver: {
    label: 'Driver',
    roleCode: 'DRIVER',
    employeeIdentifier: 'driver-1',
    account: { employee_id: 'driver-1', full_name: 'Juan Santos', role_codes: ['DRIVER'] },
    capabilities: { 'trip.assignment_view': 'OWN', 'trip.progress': 'OWN', 'or.upload': 'OWN', 'or.confirm_receipt': 'OWN', 'or.view_files': 'OWN', 'expense.enter': 'OWN', 'payroll.view_own': 'OWN', 'cash_advance.request': 'OWN', 'report.view': 'OWN', 'employee.manage': 'OWN', 'driver_license.view': 'OWN' },
  },
  helper: {
    label: 'Helper',
    roleCode: 'HELPER',
    employeeIdentifier: 'helper-1',
    account: { employee_id: 'helper-1', full_name: 'Mario Cruz', role_codes: ['HELPER'] },
    capabilities: { 'trip.assignment_view': 'OWN', 'payroll.view_own': 'OWN', 'cash_advance.request': 'OWN', 'report.view': 'OWN', 'employee.manage': 'OWN' },
  },
  hr: {
    label: 'HR & Payroll',
    roleCode: 'HR_PAYROLL',
    employeeIdentifier: 'hr-1',
    account: { employee_id: 'hr-1', full_name: 'Hana Hernandez', role_codes: ['HR_PAYROLL'] },
    capabilities: { 'employee.manage': 'FULL', 'driver_license.view': 'VIEW', 'payroll.view_others': 'FULL', 'deduction.record': 'FULL', 'payroll_adjustment.prepare': 'FULL', 'cash_advance.request': 'FULL', 'cash_advance.release_repay': 'FULL', 'payroll_payment.record': 'FULL', 'report.view': 'FULL' },
  },
  accounting: {
    label: 'Accounting',
    roleCode: 'ACCOUNTING',
    employeeIdentifier: 'accounting-1',
    account: { employee_id: 'accounting-1', full_name: 'Alma Accounting', role_codes: ['ACCOUNTING'] },
    capabilities: { 'delivery_order.manage': 'VIEW', 'or.view_files': 'VIEW', 'expense.approve': 'FULL', 'charge.finalize': 'FULL', 'client_rate.view': 'FULL', 'billing.manage': 'FULL', 'report.view': 'FULL' },
  },
}

export const PERMISSION_GRANTS = grantsFrom(ROLES)

export const LOAD_STATES = [
  { key: 'ready', label: 'Normal' },
  { key: 'loading', label: 'Loading' },
  { key: 'load-error', label: 'Load error' },
  { key: 'action-error', label: 'Action error' },
  { key: 'empty', label: 'Empty' },
]

const LOAD_FAILURE = {
  status: 503,
  code: 'DATABASE_UNAVAILABLE',
  title: 'Service unavailable',
  detail: 'The service is temporarily unavailable. Try again shortly.',
  traceIdentifier: '9f3c1a7e2b4d4e0f',
  fieldErrors: [],
}

const ACTION_FAILURE = {
  status: 409,
  code: 'DISPATCH_BLOCKED',
  title: 'Conflict',
  detail: "Dispatch blocked: The previous trip's OR has not yet been marked as received by the steel company.",
  traceIdentifier: '4d1b8c0a77e25f31',
  fieldErrors: [{ field: 'body.load_tons', message: 'Input should be greater than 0' }],
}

/**
 * @function loadStateView
 * @description Turn a chosen preview state into the props the panels expect.
 * @param {string} stateKey One of the LOAD_STATES keys
 * @returns {{loadState: string, failure: Object|null, actionFailure: Object|null, isEmpty: boolean}}
 */
export function loadStateView(stateKey) {
  return {
    loadState: stateKey === 'loading' ? 'loading' : stateKey === 'load-error' ? 'failed' : 'ready',
    failure: stateKey === 'load-error' ? LOAD_FAILURE : null,
    actionFailure: stateKey === 'action-error' ? ACTION_FAILURE : null,
    isEmpty: stateKey === 'empty' || stateKey === 'loading',
  }
}

/**
 * @function previewAction
 * @description A stand-in callback that logs the call and reports success.
 * @param {string} actionName Name shown in the console
 * @returns {function(...Object): Promise<boolean>}
 */
export function previewAction(actionName) {
  return async (...callArguments) => {
    console.info(`[design preview] ${actionName}`, ...callArguments)
    return true
  }
}

/**
 * @function previewLoadLicense
 * @description A stand-in license loader returning a valid sample license.
 * @param {string} employeeIdentifier Employee id
 * @returns {Promise<{license: Object, failure: null}>}
 */
export async function previewLoadLicense(employeeIdentifier) {
  return {
    license: { employee_id: employeeIdentifier, license_number: 'N01-12-345678', expiry_date: '2027-03-01', validity: 'VALID' },
    failure: null,
  }
}

/**
 * @function previewLoadMaintenance
 * @description A stand-in maintenance history loader.
 * @returns {Promise<{records: Array<Object>, failure: null}>}
 */
export async function previewLoadMaintenance() {
  return { records: MAINTENANCE_RECORDS, failure: null }
}
