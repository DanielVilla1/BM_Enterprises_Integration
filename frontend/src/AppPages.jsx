// ===== AI GENERATED: AppPages =====
// Purpose: Page containers: each joins data hooks to one presentational screen
// Inputs: the page key and the signed-in account
// Returns: the screen for that page
// Flow:
// 1. Live screens call hooks that load data and run actions
// 2. Design-preview screens (finance, reports) use sample data only
// 3. Permissions come from the backend-confirmed capabilities; the UI only hides buttons

import { AccountSummary } from './components/AccountSummary'
import { AdvancesPreview } from './components/AdvancesPreview'
import { AuditPanel } from './components/AuditPanel'
import { BillingPreview } from './components/BillingPreview'
import { ClientsPanel } from './components/ClientsPanel'
import { DashboardPanel } from './components/DashboardPanel'
import { DeliveryOrdersPanel } from './components/DeliveryOrdersPanel'
import { DispatchPanel } from './components/DispatchPanel'
import { ExpensesPreview } from './components/ExpensesPreview'
import { FleetPanel } from './components/FleetPanel'
import { MyTripsPanel } from './components/MyTripsPanel'
import { PayrollPreview } from './components/PayrollPreview'
import { PeoplePanel } from './components/PeoplePanel'
import { PermissionsPanel } from './components/PermissionsPanel'
import { ReportsPreview } from './components/ReportsPreview'
import { useAuditLog } from './hooks/useAuditLog'
import { useClients } from './hooks/useClients'
import { useDashboard } from './hooks/useDashboard'
import { useDispatch } from './hooks/useDispatch'
import { useEmployees } from './hooks/useEmployees'
import { useMyTrips } from './hooks/useMyTrips'
import { useOrders } from './hooks/useOrders'
import { usePermissionMatrix } from './hooks/usePermissionMatrix'
import { useTrucks } from './hooks/useTrucks'
import { hasWriteAccess } from './shared/utils/navigation'

/**
 * @function DashboardPage
 * @description Dashboard container.
 * @param {{account: Object, openPage: function(string): void}} componentProps
 * @returns {import('react').ReactElement}
 */
function DashboardPage({ account, openPage }) {
  const dashboardState = useDashboard()
  return (
    <DashboardPanel
      loadState={dashboardState.loadState}
      snapshot={dashboardState.snapshot}
      failure={dashboardState.failure}
      userName={account.full_name}
      onOpenPage={openPage}
    />
  )
}

/**
 * @function DispatchPage
 * @description Dispatch board container.
 * @param {{capabilities: Object<string, string>}} componentProps
 * @returns {import('react').ReactElement}
 */
function DispatchPage({ capabilities }) {
  const dispatchState = useDispatch()
  const orderState = useOrders()
  const clientState = useClients()
  return (
    <DispatchPanel
      loadState={dispatchState.loadState}
      trips={dispatchState.trips}
      orders={orderState.orders}
      clients={clientState.clients}
      resources={dispatchState.resources}
      failure={dispatchState.failure}
      actionFailure={dispatchState.actionFailure}
      isBusy={dispatchState.isBusy}
      canWrite={hasWriteAccess(capabilities, 'dispatch.assign')}
      canCorrect={hasWriteAccess(capabilities, 'or.correct_confirmation')}
      onAssign={dispatchState.submitAssignment}
      onClear={dispatchState.submitClearance}
      onClose={dispatchState.submitClose}
      onChangeCrew={dispatchState.submitCrewChange}
      onReplaceTruck={dispatchState.submitTruckReplacement}
      onCorrect={dispatchState.submitCorrection}
      onOpenDocument={dispatchState.openDocument}
    />
  )
}

/**
 * @function OrdersPage
 * @description Orders container.
 * @param {{capabilities: Object<string, string>}} componentProps
 * @returns {import('react').ReactElement}
 */
function OrdersPage({ capabilities }) {
  const orderState = useOrders()
  const clientState = useClients()
  return (
    <DeliveryOrdersPanel
      loadState={orderState.loadState}
      orders={orderState.orders}
      clients={clientState.clients}
      failure={orderState.failure}
      actionFailure={orderState.actionFailure}
      isBusy={orderState.isBusy}
      canWrite={hasWriteAccess(capabilities, 'delivery_order.manage')}
      onCreate={orderState.submitOrder}
      onUpdate={orderState.submitUpdate}
      onCancel={orderState.submitCancel}
    />
  )
}

/**
 * @function ClientsPage
 * @description Clients container.
 * @param {{capabilities: Object<string, string>}} componentProps
 * @returns {import('react').ReactElement}
 */
function ClientsPage({ capabilities }) {
  const clientState = useClients()
  return (
    <ClientsPanel
      loadState={clientState.loadState}
      clients={clientState.clients}
      failure={clientState.failure}
      actionFailure={clientState.actionFailure}
      isBusy={clientState.isBusy}
      canWrite={hasWriteAccess(capabilities, 'delivery_order.manage')}
      onCreate={clientState.submitClient}
      onUpdate={clientState.submitUpdate}
    />
  )
}

/**
 * @function FleetPage
 * @description Fleet container.
 * @param {{capabilities: Object<string, string>}} componentProps
 * @returns {import('react').ReactElement}
 */
function FleetPage({ capabilities }) {
  const truckState = useTrucks()
  return (
    <FleetPanel
      loadState={truckState.loadState}
      trucks={truckState.trucks}
      failure={truckState.failure}
      actionFailure={truckState.actionFailure}
      isBusy={truckState.isBusy}
      canWrite={hasWriteAccess(capabilities, 'truck.manage')}
      onCreate={truckState.submitTruck}
      onUpdate={truckState.submitUpdate}
      onLoadMaintenance={truckState.loadMaintenance}
      onStartMaintenance={truckState.submitMaintenanceStart}
      onCompleteMaintenance={truckState.submitMaintenanceComplete}
    />
  )
}

/**
 * @function MyTripsPage
 * @description Crew trips container.
 * @param {{employeeIdentifier: string}} componentProps
 * @returns {import('react').ReactElement}
 */
function MyTripsPage({ employeeIdentifier }) {
  const tripState = useMyTrips()
  return (
    <MyTripsPanel
      loadState={tripState.loadState}
      trips={tripState.trips}
      employeeIdentifier={employeeIdentifier}
      failure={tripState.failure}
      actionFailure={tripState.actionFailure}
      isBusy={tripState.isBusy}
      onProgress={tripState.submitProgress}
      onUpload={tripState.submitUpload}
      onConfirm={tripState.submitConfirmation}
      onOpenDocument={tripState.openDocument}
    />
  )
}

/**
 * @function PeoplePage
 * @description People container.
 * @param {{capabilities: Object<string, string>}} componentProps
 * @returns {import('react').ReactElement}
 */
function PeoplePage({ capabilities }) {
  const employeeState = useEmployees()
  return (
    <PeoplePanel
      loadState={employeeState.loadState}
      employees={employeeState.employees}
      failure={employeeState.failure}
      actionFailure={employeeState.actionFailure}
      isBusy={employeeState.isBusy}
      permissions={{
        canEdit: hasWriteAccess(capabilities, 'employee.manage'),
        canManageAccounts: hasWriteAccess(capabilities, 'audit_user.manage'),
        canActivate: hasWriteAccess(capabilities, 'employee.activate'),
        canViewLicense: capabilities['driver_license.view'] !== undefined,
        canEditLicense: hasWriteAccess(capabilities, 'driver_license.view'),
      }}
      handlers={{
        onCreate: employeeState.submitCreate,
        onUpdate: employeeState.submitUpdate,
        onSetActive: employeeState.submitActive,
        onAssignRoles: employeeState.submitRoles,
        onLinkIdentity: employeeState.submitIdentity,
        onLoadLicense: employeeState.loadLicense,
        onSaveLicense: employeeState.submitLicense,
      }}
    />
  )
}

/**
 * @function AuditPage
 * @description Audit log container.
 * @returns {import('react').ReactElement}
 */
function AuditPage() {
  const auditState = useAuditLog()
  return (
    <AuditPanel
      loadState={auditState.loadState}
      records={auditState.records}
      hasMore={auditState.hasMore}
      failure={auditState.failure}
      onLoadMore={auditState.loadMore}
    />
  )
}

/**
 * @function PermissionsPage
 * @description Permission matrix container.
 * @returns {import('react').ReactElement}
 */
function PermissionsPage() {
  const matrixState = usePermissionMatrix()
  return <PermissionsPanel loadState={matrixState.loadState} grants={matrixState.grants} failure={matrixState.failure} />
}

/**
 * @function PageContent
 * @description The screen for a page key.
 * @param {{pageKey: string, account: Object, openPage: function(string): void}} componentProps
 * @returns {import('react').ReactElement}
 */
export function PageContent({ pageKey, account, openPage }) {
  const { capabilities } = account
  switch (pageKey) {
    case 'dashboard':
      return <DashboardPage account={account} openPage={openPage} />
    case 'dispatch':
      return <DispatchPage capabilities={capabilities} />
    case 'orders':
      return <OrdersPage capabilities={capabilities} />
    case 'clients':
      return <ClientsPage capabilities={capabilities} />
    case 'fleet':
      return <FleetPage capabilities={capabilities} />
    case 'trips':
      return <MyTripsPage employeeIdentifier={account.employee_id} />
    case 'people':
      return <PeoplePage capabilities={capabilities} />
    case 'audit':
      return <AuditPage />
    case 'permissions':
      return <PermissionsPage />
    case 'expenses':
      return <ExpensesPreview />
    case 'payroll':
      return <PayrollPreview isOwnView={capabilities['payroll.view_others'] === undefined} />
    case 'advances':
      return <AdvancesPreview />
    case 'billing':
      return <BillingPreview />
    case 'reports':
      return <ReportsPreview />
    default:
      return <AccountSummary loadState="ready" account={account} failure={null} />
  }
}
