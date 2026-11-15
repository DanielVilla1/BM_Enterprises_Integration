// ===== AI GENERATED: App =====
// Purpose: Application shell: sign-in, capability-based navigation, pages
// Inputs: none
// Returns: gated workspace
// Flow:
// 1. Signed-out visitors get the Clerk sign-in form
// 2. Signed-in users load /me; navigation shows only granted pages
// 3. Each page container joins one hook with one presentational panel

import { AccountSummary } from './components/AccountSummary'
import { ClientsPanel } from './components/ClientsPanel'
import { DeliveryOrdersPanel } from './components/DeliveryOrdersPanel'
import { DispatchPanel } from './components/DispatchPanel'
import { FleetPanel } from './components/FleetPanel'
import { MyTripsPanel } from './components/MyTripsPanel'
import { NavigationBar } from './components/NavigationBar'
import { useClients } from './hooks/useClients'
import { useCurrentAccount } from './hooks/useCurrentAccount'
import { useDispatch } from './hooks/useDispatch'
import { useMyTrips } from './hooks/useMyTrips'
import { useOrders } from './hooks/useOrders'
import { useTrucks } from './hooks/useTrucks'
import { CLERK_PUBLISHABLE_KEY } from './shared/services/clerkConfig'
import {
  SessionTokenBridge,
  SignedInGate,
  SignedOutGate,
} from './shared/services/clerkSessionService'
import { hasWriteAccess, visibleNavigation } from './shared/utils/navigation'
import { useNavigationStore } from './store/navigationStore'

/**
 * @function OrdersPage
 * @description Orders screen container.
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
      onCancel={orderState.submitCancel}
    />
  )
}

/**
 * @function ClientsPage
 * @description Clients screen container.
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
    />
  )
}

/**
 * @function FleetPage
 * @description Fleet screen container.
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
      onStartMaintenance={truckState.submitMaintenanceStart}
      onCompleteMaintenance={truckState.submitMaintenanceComplete}
    />
  )
}

/**
 * @function DispatchPage
 * @description Dispatch screen container.
 * @param {{capabilities: Object<string, string>}} componentProps
 * @returns {import('react').ReactElement}
 */
function DispatchPage({ capabilities }) {
  const dispatchState = useDispatch()
  const orderState = useOrders()
  return (
    <DispatchPanel
      loadState={dispatchState.loadState}
      trips={dispatchState.trips}
      orders={orderState.orders}
      resources={dispatchState.resources}
      failure={dispatchState.failure}
      actionFailure={dispatchState.actionFailure}
      isBusy={dispatchState.isBusy}
      canWrite={hasWriteAccess(capabilities, 'dispatch.assign')}
      canCorrect={hasWriteAccess(capabilities, 'or.correct_confirmation')}
      onAssign={dispatchState.submitAssignment}
      onClear={dispatchState.submitClearance}
      onClose={dispatchState.submitClose}
      onCorrect={dispatchState.submitCorrection}
      onOpenDocument={dispatchState.openDocument}
    />
  )
}

/**
 * @function MyTripsPage
 * @description Crew trips screen container.
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
 * @function Workspace
 * @description Signed-in area: account load, navigation and the active page.
 * @returns {import('react').ReactElement}
 */
function Workspace() {
  const { loadState, account, failure } = useCurrentAccount()
  const activePage = useNavigationStore((state) => state.activePage)
  const openPage = useNavigationStore((state) => state.openPage)
  if (loadState !== 'ready') {
    return <AccountSummary loadState={loadState} account={account} failure={failure} />
  }
  const pages = visibleNavigation(account.capabilities)
  const shownPage = pages.some((page) => page.key === activePage) ? activePage : 'account'
  return (
    <div className="space-y-4">
      <NavigationBar items={pages} activePage={shownPage} onSelect={openPage} />
      {shownPage === 'dispatch' ? <DispatchPage capabilities={account.capabilities} /> : null}
      {shownPage === 'trips' ? <MyTripsPage employeeIdentifier={account.employee_id} /> : null}
      {shownPage === 'orders' ? <OrdersPage capabilities={account.capabilities} /> : null}
      {shownPage === 'clients' ? <ClientsPage capabilities={account.capabilities} /> : null}
      {shownPage === 'fleet' ? <FleetPage capabilities={account.capabilities} /> : null}
      {shownPage === 'account' ? (
        <AccountSummary loadState={loadState} account={account} failure={failure} />
      ) : null}
    </div>
  )
}

/**
 * @function App
 * @description Root component.
 * @returns {import('react').ReactElement}
 */
function App() {
  if (!CLERK_PUBLISHABLE_KEY) {
    return (
      <main className="mx-auto max-w-xl p-6">
        <p role="alert">
          Sign-in is not configured. Set VITE_CLERK_PUBLISHABLE_KEY in the environment.
        </p>
      </main>
    )
  }
  return (
    <main className="mx-auto max-w-3xl space-y-6 p-6">
      <h1 className="text-2xl font-bold">BM Enterprises Hauling</h1>
      <SignedOutGate />
      <SignedInGate>
        <SessionTokenBridge />
        <Workspace />
      </SignedInGate>
    </main>
  )
}

export default App
