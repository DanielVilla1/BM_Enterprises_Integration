// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: PreviewApp =====
// Purpose: Render the real shell and every screen with sample data so they can be designed without a backend
// Inputs: none (role and state are chosen in the toolbar; resize the window to test phones)
// Returns: the same components the app uses, wired to fake data and no-op actions
// Flow:
// 1. Pick a role: navigation shows only that role's pages, as in production
// 2. Pick a state: normal, loading, load error, action error, empty
// 3. Use the shell's theme toggle to compare the dark and light themes

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { useState } from 'react'
import { AccountSummary } from '../src/components/account/AccountSummary'
import { AdvancesPreview } from '../src/components/finance/AdvancesPreview'
import { AppShell } from '../src/shared/components/AppShell'
import { AuditPanel } from '../src/components/administration/AuditPanel'
import { BillingPreview } from '../src/components/finance/BillingPreview'
import { ClientsPanel } from '../src/components/clients/ClientsPanel'
import { DashboardPanel } from '../src/components/dashboard/DashboardPanel'
import { DeliveryOrdersPanel } from '../src/components/orders/DeliveryOrdersPanel'
import { DispatchPanel } from '../src/components/dispatch/DispatchPanel'
import { ExpensesPreview } from '../src/components/finance/ExpensesPreview'
import { FleetPanel } from '../src/components/fleet/FleetPanel'
import { MyTripsPanel } from '../src/components/trips/MyTripsPanel'
import { PayrollPreview } from '../src/components/finance/PayrollPreview'
import { PeoplePanel } from '../src/components/administration/PeoplePanel'
import { PermissionsPanel } from '../src/components/administration/PermissionsPanel'
import { ReportsPreview } from '../src/components/reports/ReportsPreview'
import { useTheme } from '../src/hooks/useTheme'
import {
  hasWriteAccess,
  resolveActivePage,
  visibleNavigation,
} from '../src/shared/utils/navigation'
import { roleLabel } from '../src/shared/utils/permissionMatrix'
import {
  AUDIT_RECORDS,
  CLIENTS,
  EMPLOYEES,
  EMPTY_RESOURCES,
  LOAD_STATES,
  ORDERS,
  PERMISSION_GRANTS,
  RESOURCES,
  ROLES,
  TRIPS,
  TRUCKS,
  loadStateView,
  previewAction,
  previewLoadLicense,
  previewLoadMaintenance,
} from './fixtures'

/**
 * @function PreviewToolbar
 * @description The role and state pickers above the app.
 * @param {Object} componentProps Props: roleKey, stateKey, onRoleChange, onStateChange
 * @returns {import('react').ReactElement}
 */
function PreviewToolbar({ roleKey, stateKey, onRoleChange, onStateChange }) {
  return (
    <div className="border-b border-warning/40 bg-warning/10 px-4 py-2 text-sm">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-6 gap-y-2">
        <strong>Design preview</strong>
        <span className="text-base-content/70">
          Sample data · not connected to Clerk or the backend · resize the window to test phones
        </span>
        <label className="flex items-center gap-2">
          Role
          <select
            value={roleKey}
            onChange={(event) => onRoleChange(event.target.value)}
            className="select select-sm"
          >
            {Object.entries(ROLES).map(([key, roleOption]) => (
              <option key={key} value={key}>
                {roleOption.label}
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-2">
          State
          <select
            value={stateKey}
            onChange={(event) => onStateChange(event.target.value)}
            className="select select-sm"
          >
            {LOAD_STATES.map((stateOption) => (
              <option key={stateOption.key} value={stateOption.key}>
                {stateOption.label}
              </option>
            ))}
          </select>
        </label>
      </div>
    </div>
  )
}

/**
 * @function PreviewApp
 * @description Design preview shell.
 * @returns {import('react').ReactElement}
 */
export function PreviewApp() {
  const [roleKey, setRoleKey] = useState('dispatcher')
  const [stateKey, setStateKey] = useState('ready')
  const [activePage, setActivePage] = useState(null)
  const { theme, toggleTheme } = useTheme()

  const role = ROLES[roleKey]
  const capabilities = role.capabilities
  const pages = visibleNavigation(capabilities)
  const shownPage = resolveActivePage(pages, activePage)
  const view = loadStateView(stateKey)
  const listOf = (records) => (view.isEmpty ? [] : records)
  const shared = {
    loadState: view.loadState,
    failure: view.failure,
    actionFailure: view.actionFailure,
    isBusy: false,
  }
  const resources = view.isEmpty ? EMPTY_RESOURCES : RESOURCES
  const account = { ...role.account, capabilities }

  const screens = {
    dashboard: (
      <DashboardPanel
        loadState={view.loadState}
        failure={view.failure}
        userName={role.account.full_name}
        onOpenPage={setActivePage}
        snapshot={{
          orders: listOf(ORDERS),
          trips: listOf(TRIPS),
          trucks: listOf(TRUCKS),
          resources,
        }}
      />
    ),
    dispatch: (
      <DispatchPanel
        {...shared}
        trips={listOf(TRIPS)}
        orders={listOf(ORDERS)}
        clients={CLIENTS}
        resources={resources}
        canWrite={hasWriteAccess(capabilities, 'dispatch.assign')}
        canCorrect={hasWriteAccess(capabilities, 'or.correct_confirmation')}
        onAssign={previewAction('assign trip')}
        onClear={previewAction('clear dispatch')}
        onClose={previewAction('cancel or fail trip')}
        onChangeCrew={previewAction('change crew')}
        onReplaceTruck={previewAction('replace truck')}
        onCorrect={previewAction('correct receipt confirmation')}
        onOpenDocument={previewAction('open document')}
      />
    ),
    orders: (
      <DeliveryOrdersPanel
        {...shared}
        orders={listOf(ORDERS)}
        clients={CLIENTS}
        canWrite={hasWriteAccess(capabilities, 'delivery_order.manage')}
        onCreate={previewAction('create order')}
        onUpdate={previewAction('update order')}
        onCancel={previewAction('cancel order')}
      />
    ),
    clients: (
      <ClientsPanel
        {...shared}
        clients={listOf(CLIENTS)}
        canWrite={hasWriteAccess(capabilities, 'delivery_order.manage')}
        onCreate={previewAction('create client')}
        onUpdate={previewAction('update client')}
      />
    ),
    fleet: (
      <FleetPanel
        {...shared}
        trucks={listOf(TRUCKS)}
        canWrite={hasWriteAccess(capabilities, 'truck.manage')}
        onCreate={previewAction('register truck')}
        onUpdate={previewAction('update truck')}
        onLoadMaintenance={previewLoadMaintenance}
        onStartMaintenance={previewAction('start maintenance')}
        onCompleteMaintenance={previewAction('complete maintenance')}
      />
    ),
    trips: (
      <MyTripsPanel
        {...shared}
        trips={listOf(TRIPS)}
        employeeIdentifier={role.employeeIdentifier}
        capabilities={capabilities}
        onProgress={previewAction('trip progress')}
        onUpload={previewAction('upload OR')}
        onConfirm={previewAction('confirm receipt')}
        onOpenDocument={previewAction('open document')}
      />
    ),
    people: (
      <PeoplePanel
        {...shared}
        employees={listOf(EMPLOYEES)}
        permissions={{
          canEdit: hasWriteAccess(capabilities, 'employee.manage'),
          canManageAccounts: hasWriteAccess(capabilities, 'audit_user.manage'),
          canActivate: hasWriteAccess(capabilities, 'employee.activate'),
          canViewLicense: capabilities['driver_license.view'] !== undefined,
          canEditLicense: hasWriteAccess(capabilities, 'driver_license.view'),
        }}
        handlers={{
          onCreate: previewAction('create employee'),
          onUpdate: previewAction('update employee'),
          onSetActive: previewAction('activate or deactivate'),
          onAssignRoles: previewAction('assign roles'),
          onLinkIdentity: previewAction('link sign-in account'),
          onLoadLicense: previewLoadLicense,
          onSaveLicense: previewAction('save license'),
        }}
      />
    ),
    audit: (
      <AuditPanel
        loadState={view.loadState}
        records={listOf(AUDIT_RECORDS)}
        hasMore={!view.isEmpty}
        failure={view.failure}
        onLoadMore={previewAction('load more')}
      />
    ),
    permissions: (
      <PermissionsPanel
        loadState={view.loadState}
        grants={listOf(PERMISSION_GRANTS)}
        failure={view.failure}
      />
    ),
    expenses: <ExpensesPreview />,
    payroll: <PayrollPreview isOwnView={capabilities['payroll.view_others'] === undefined} />,
    advances: <AdvancesPreview />,
    billing: <BillingPreview />,
    reports: <ReportsPreview />,
    account: <AccountSummary loadState={view.loadState} account={account} failure={view.failure} />,
  }

  return (
    <div>
      <PreviewToolbar
        roleKey={roleKey}
        stateKey={stateKey}
        onRoleChange={setRoleKey}
        onStateChange={setStateKey}
      />
      <AppShell
        pages={pages}
        activePage={shownPage}
        onSelect={setActivePage}
        userName={role.account.full_name}
        roleLabel={role.account.role_codes.map(roleLabel).join(' · ')}
        userSlot={null}
        theme={theme}
        onToggleTheme={toggleTheme}
      >
        {screens[shownPage]}
      </AppShell>
    </div>
  )
}
