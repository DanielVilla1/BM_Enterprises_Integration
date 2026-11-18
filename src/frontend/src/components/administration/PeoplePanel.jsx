// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: PeoplePanel =====
// Purpose: People: employees, roles, sign-in links, activation and driver licenses
// Inputs: employees, the viewer's permissions and callbacks (props only)
// Returns: page markup
// Flow:
// 1. Searchable, filterable list with role badges, status and sign-in link state
// 2. Row menu offers only what the viewer's role may do (the backend still decides)
// 3. Roles dialog explains forbidden pairs; the Owner can give a reason to override

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { useEffect, useState } from 'react'
import { useToast } from '../../hooks/useToast'
import { buildChanges, compactPayload } from '../../shared/utils/forms'
import { formatDate, initialsOf } from '../../shared/utils/formatting'
import { ROLE_ORDER, roleLabel } from '../../shared/utils/permissionMatrix'
import { EMPLOYEE_TABS, filterEmployees } from '../../shared/utils/people'
import { EmptyState } from '../../shared/components/EmptyState'
import { ErrorNotice } from '../../shared/components/ErrorNotice'
import { FilterTabs } from '../../shared/components/FilterTabs'
import { FormField } from '../../shared/components/FormField'
import { Icon } from '../../shared/components/Icon'
import { ListSkeleton } from '../../shared/components/ListSkeleton'
import { ModalDialog } from '../../shared/components/ModalDialog'
import { PageHeader } from '../../shared/components/PageHeader'
import { RowMenu } from '../../shared/components/RowMenu'
import { SearchField } from '../../shared/components/SearchField'
import { StatusBadge } from '../../shared/components/StatusBadge'
import { Toast } from '../../shared/components/Toast'

/**
 * @function DialogActions
 * @description Back and submit buttons for dialog forms.
 * @param {{label: string, isBusy: boolean, onClose: function(): void}} componentProps
 * @returns {import('react').ReactElement}
 */
function DialogActions({ label, isBusy, onClose }) {
  return (
    <div className="modal-action">
      <button type="button" className="btn btn-ghost" onClick={onClose}>
        Back
      </button>
      <button type="submit" className="btn btn-primary" disabled={isBusy}>
        {label}
      </button>
    </div>
  )
}

/**
 * @function EmployeeForm
 * @description Add or edit an employee's details.
 * @param {Object} componentProps Props: employee, isBusy, failure, onSubmit, onClose
 * @returns {import('react').ReactElement}
 */
function EmployeeForm({ employee, isBusy, failure, onSubmit, onClose }) {
  return (
    <form
      className="grid gap-x-4 sm:grid-cols-2"
      onSubmit={async (event) => {
        event.preventDefault()
        await onSubmit(Object.fromEntries(new FormData(event.currentTarget)))
      }}
    >
      <FormField label="Full name" className="sm:col-span-2">
        <input
          name="full_name"
          required
          maxLength={120}
          defaultValue={employee?.full_name}
          className="input w-full"
        />
      </FormField>
      <FormField label="Email" hint="Used to link their sign-in account automatically">
        <input
          name="email"
          type="email"
          required
          maxLength={254}
          defaultValue={employee?.email}
          className="input w-full"
        />
      </FormField>
      <FormField label="Phone (optional)">
        <input
          name="phone"
          maxLength={32}
          defaultValue={employee?.phone ?? ''}
          className="input w-full"
        />
      </FormField>
      <div className="sm:col-span-2">
        <ErrorNotice failure={failure} />
      </div>
      <div className="sm:col-span-2">
        <DialogActions
          label={employee ? 'Save changes' : 'Add employee'}
          isBusy={isBusy}
          onClose={onClose}
        />
      </div>
    </form>
  )
}

/**
 * @function RolesForm
 * @description Choose an employee's roles, with an optional Owner reason for forbidden pairs.
 * @param {Object} componentProps Props: employee, isBusy, failure, onSubmit, onClose
 * @returns {import('react').ReactElement}
 */
function RolesForm({ employee, isBusy, failure, onSubmit, onClose }) {
  return (
    <form
      className="space-y-4"
      onSubmit={async (event) => {
        event.preventDefault()
        const formData = new FormData(event.currentTarget)
        await onSubmit(formData.getAll('role'), String(formData.get('reason') ?? '').trim())
      }}
    >
      <div className="grid gap-2 sm:grid-cols-2">
        {ROLE_ORDER.map((roleCode) => (
          <label
            key={roleCode}
            className="label cursor-pointer justify-start gap-3 rounded-field border border-base-300 p-3"
          >
            <input
              type="checkbox"
              name="role"
              value={roleCode}
              defaultChecked={employee.role_codes.includes(roleCode)}
              className="checkbox checkbox-primary"
            />
            <span>{roleLabel(roleCode)}</span>
          </label>
        ))}
      </div>
      <p className="text-xs text-base-content/60">
        Some combinations are not allowed (for example HR with Accounting, or a driver with an
        office role). Owners can still allow one by giving a reason, which is recorded in the audit
        log.
      </p>
      <FormField label="Reason for an exception (only if needed)">
        <textarea
          name="reason"
          minLength={10}
          maxLength={500}
          rows={2}
          className="textarea w-full"
        />
      </FormField>
      <ErrorNotice failure={failure} />
      <DialogActions label="Save roles" isBusy={isBusy} onClose={onClose} />
    </form>
  )
}

/**
 * @function IdentityForm
 * @description Link an employee to a Clerk sign-in account.
 * @param {Object} componentProps Props: isBusy, failure, onSubmit, onClose
 * @returns {import('react').ReactElement}
 */
function IdentityForm({ isBusy, failure, onSubmit, onClose }) {
  return (
    <form
      className="space-y-4"
      onSubmit={async (event) => {
        event.preventDefault()
        await onSubmit(String(new FormData(event.currentTarget).get('clerk_user_id')).trim())
      }}
    >
      <p className="text-sm text-base-content/70">
        Normally this happens automatically when the person signs up with the email on their record.
        Use this only if that did not work.
      </p>
      <FormField label="Clerk user ID" hint="Looks like user_2abc… (from the Clerk dashboard)">
        <input
          name="clerk_user_id"
          required
          minLength={5}
          maxLength={64}
          pattern="[A-Za-z0-9_]+"
          className="input w-full font-mono"
        />
      </FormField>
      <ErrorNotice failure={failure} />
      <DialogActions label="Link account" isBusy={isBusy} onClose={onClose} />
    </form>
  )
}

/**
 * @function LicenseContent
 * @description Shows a driver's license status and, for editors, a form to save it.
 * @param {Object} componentProps Props: employee, canEdit, isBusy, failure, onLoad, onSave, onSaved, onClose
 * @returns {import('react').ReactElement}
 */
function LicenseContent({ employee, canEdit, isBusy, failure, onLoad, onSave, onSaved, onClose }) {
  const [result, setResult] = useState(null)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    let cancelled = false
    onLoad(employee.employee_id).then((loaded) => {
      if (!cancelled) setResult(loaded)
    })
    return () => {
      cancelled = true
    }
  }, [onLoad, employee.employee_id, reloadKey])

  if (result === null)
    return <span className="loading loading-spinner" role="status" aria-label="Loading" />
  const license = result.license
  const noneOnRecord = result.failure?.code === 'LICENSE_NOT_FOUND'
  return (
    <div className="space-y-4">
      {result.failure && !noneOnRecord ? <ErrorNotice failure={result.failure} /> : null}
      {noneOnRecord ? (
        <p className="text-sm text-base-content/70">No license on record yet.</p>
      ) : null}
      {license ? (
        <dl className="grid grid-cols-[auto_1fr] items-center gap-x-4 gap-y-2 text-sm">
          <dt className="text-base-content/60">Status</dt>
          <dd>
            <StatusBadge kind="license" status={license.validity} />
          </dd>
          {license.license_number ? (
            <>
              <dt className="text-base-content/60">License number</dt>
              <dd className="font-mono">{license.license_number}</dd>
              <dt className="text-base-content/60">Expires</dt>
              <dd>{formatDate(license.expiry_date)}</dd>
            </>
          ) : null}
        </dl>
      ) : null}
      {canEdit ? (
        <form
          className="grid gap-x-4 sm:grid-cols-2"
          onSubmit={async (event) => {
            event.preventDefault()
            const values = Object.fromEntries(new FormData(event.currentTarget))
            if (
              await onSave(employee.employee_id, {
                license_number: values.license_number.trim(),
                expiry_date: values.expiry_date,
              })
            ) {
              onSaved()
              setReloadKey((previous) => previous + 1)
            }
          }}
        >
          <FormField label="License number">
            <input
              name="license_number"
              required
              minLength={5}
              maxLength={32}
              pattern="[A-Za-z0-9\-]+"
              defaultValue={license?.license_number ?? ''}
              className="input w-full font-mono uppercase"
              placeholder="N01-12-345678"
            />
          </FormField>
          <FormField label="Expiry date">
            <input
              name="expiry_date"
              type="date"
              required
              defaultValue={license?.expiry_date ?? ''}
              className="input w-full"
            />
          </FormField>
          <div className="sm:col-span-2">
            <ErrorNotice failure={failure} />
          </div>
          <div className="sm:col-span-2">
            <DialogActions label="Save license" isBusy={isBusy} onClose={onClose} />
          </div>
        </form>
      ) : (
        <div className="modal-action">
          <button type="button" className="btn" onClick={onClose}>
            Close
          </button>
        </div>
      )}
    </div>
  )
}

/**
 * @function PeoplePanel
 * @description Pure UI for people management.
 * @param {Object} componentProps Props: loadState, employees, failure, actionFailure, isBusy, permissions, handlers
 * @returns {import('react').ReactElement}
 */
export function PeoplePanel({
  loadState,
  employees,
  failure,
  actionFailure,
  isBusy,
  permissions,
  handlers,
}) {
  const [tabKey, setTabKey] = useState('all')
  const [query, setQuery] = useState('')
  const [dialog, setDialog] = useState(null)
  const { toast, showToast } = useToast()
  const visibleEmployees = filterEmployees(employees, tabKey, query)
  const counts = {
    all: employees.length,
    active: employees.filter((entry) => entry.is_active).length,
    inactive: employees.filter((entry) => !entry.is_active).length,
  }
  const closeDialog = () => setDialog(null)

  const finish = (succeeded, message) => {
    if (succeeded) {
      closeDialog()
      showToast(message)
    }
    return succeeded
  }

  const menuFor = (employeeRecord) => {
    const items = []
    if (permissions.canEdit)
      items.push({
        label: 'Edit details',
        onSelect: () => setDialog({ kind: 'edit', employee: employeeRecord }),
      })
    if (permissions.canManageAccounts) {
      items.push({
        label: 'Roles',
        onSelect: () => setDialog({ kind: 'roles', employee: employeeRecord }),
      })
      items.push({
        label: 'Link sign-in account',
        onSelect: () => setDialog({ kind: 'identity', employee: employeeRecord }),
      })
    }
    if (
      (employeeRecord.role_codes === undefined || employeeRecord.role_codes.includes('DRIVER')) &&
      permissions.canViewLicense
    ) {
      items.push({
        label: permissions.canEditLicense ? 'Driver license' : 'License status',
        onSelect: () => setDialog({ kind: 'license', employee: employeeRecord }),
      })
    }
    if (!employeeRecord.is_active && permissions.canActivate) {
      items.push({
        label: 'Activate',
        onSelect: async () => {
          if (await handlers.onSetActive(employeeRecord.employee_id, true))
            showToast('Employee activated')
        },
      })
    }
    if (employeeRecord.is_active && permissions.canManageAccounts) {
      items.push({
        label: 'Deactivate',
        danger: true,
        onSelect: async () => {
          if (await handlers.onSetActive(employeeRecord.employee_id, false))
            showToast('Employee deactivated')
        },
      })
    }
    return items
  }

  return (
    <section className="space-y-5">
      <PageHeader
        title="People"
        subtitle="Employees, their roles and sign-in accounts"
        actions={
          permissions.canEdit ? (
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setDialog({ kind: 'create' })}
            >
              <Icon name="plus" className="h-4 w-4" /> Add employee
            </button>
          ) : null
        }
      />
      <ErrorNotice failure={failure} />
      {dialog === null ? <ErrorNotice failure={actionFailure} /> : null}

      <div className="flex flex-wrap items-center justify-between gap-3">
        <FilterTabs
          tabs={EMPLOYEE_TABS}
          activeKey={tabKey}
          counts={counts}
          onChange={setTabKey}
          label="Employee status"
        />
        <SearchField value={query} onChange={setQuery} placeholder="Search name, email or role" />
      </div>

      {loadState === 'loading' && employees.length === 0 ? <ListSkeleton /> : null}
      {loadState !== 'loading' && visibleEmployees.length === 0 ? (
        <EmptyState
          icon="users"
          title={employees.length === 0 ? 'No employees yet' : 'No one matches'}
          description={
            employees.length === 0
              ? 'Add drivers, helpers and office staff. New employees start inactive until the Owner activates them.'
              : 'Try another tab or clear the search.'
          }
        />
      ) : null}

      {visibleEmployees.length > 0 ? (
        <ul className="list card card-border bg-base-100">
          {visibleEmployees.map((employeeRecord) => (
            <li key={employeeRecord.employee_id} className="list-row items-center">
              <div className="avatar avatar-placeholder">
                <div className="w-11 rounded-full bg-secondary/20 text-secondary">
                  <span className="font-bold">{initialsOf(employeeRecord.full_name)}</span>
                </div>
              </div>
              <div className="min-w-0">
                <p className="font-semibold">{employeeRecord.full_name}</p>
                <p className="truncate text-sm text-base-content/70">{employeeRecord.email}</p>
                <div className="mt-1 flex flex-wrap gap-1">
                  {employeeRecord.role_codes?.length === 0 ? (
                    <span className="badge badge-ghost badge-sm">No role yet</span>
                  ) : (
                    employeeRecord.role_codes?.map((roleCode) => (
                      <span key={roleCode} className="badge badge-primary badge-soft badge-sm">
                        {roleLabel(roleCode)}
                      </span>
                    ))
                  )}
                </div>
              </div>
              <div className="flex flex-col items-end gap-1">
                <StatusBadge
                  kind="employee"
                  status={employeeRecord.is_active ? 'ACTIVE' : 'INACTIVE'}
                />
                {employeeRecord.has_account !== undefined ? (
                  <span
                    className={`text-xs ${employeeRecord.has_account ? 'text-success' : 'text-warning'}`}
                  >
                    {employeeRecord.has_account ? 'Sign-in linked' : 'No sign-in yet'}
                  </span>
                ) : null}
              </div>
              <RowMenu
                label={`Actions for ${employeeRecord.full_name}`}
                items={menuFor(employeeRecord)}
              />
            </li>
          ))}
        </ul>
      ) : null}

      <ModalDialog
        title={dialog?.kind === 'edit' ? 'Edit employee' : 'Add an employee'}
        isOpen={dialog?.kind === 'create' || dialog?.kind === 'edit'}
        onClose={closeDialog}
        wide
      >
        {dialog?.kind === 'create' || dialog?.kind === 'edit' ? (
          <EmployeeForm
            employee={dialog.employee ?? null}
            isBusy={isBusy}
            failure={actionFailure}
            onClose={closeDialog}
            onSubmit={async (values) => {
              if (dialog.employee) {
                const changes = buildChanges(dialog.employee, values, [
                  'full_name',
                  'email',
                  'phone',
                ])
                finish(
                  Object.keys(changes).length === 0
                    ? true
                    : await handlers.onUpdate(dialog.employee.employee_id, changes),
                  'Employee updated',
                )
              } else {
                finish(
                  await handlers.onCreate(compactPayload(values)),
                  'Employee added. Assign a role and activate them next.',
                )
              }
            }}
          />
        ) : null}
      </ModalDialog>
      <ModalDialog
        title={dialog?.employee ? `Roles · ${dialog.employee.full_name}` : ''}
        isOpen={dialog?.kind === 'roles'}
        onClose={closeDialog}
        wide
      >
        {dialog?.kind === 'roles' ? (
          <RolesForm
            employee={dialog.employee}
            isBusy={isBusy}
            failure={actionFailure}
            onClose={closeDialog}
            onSubmit={async (roleCodes, reason) =>
              finish(
                await handlers.onAssignRoles(
                  dialog.employee.employee_id,
                  roleCodes,
                  reason || undefined,
                ),
                'Roles updated',
              )
            }
          />
        ) : null}
      </ModalDialog>
      <ModalDialog
        title={dialog?.employee ? `Sign-in account · ${dialog.employee.full_name}` : ''}
        isOpen={dialog?.kind === 'identity'}
        onClose={closeDialog}
      >
        {dialog?.kind === 'identity' ? (
          <IdentityForm
            isBusy={isBusy}
            failure={actionFailure}
            onClose={closeDialog}
            onSubmit={async (clerkUserIdentifier) =>
              finish(
                await handlers.onLinkIdentity(dialog.employee.employee_id, clerkUserIdentifier),
                'Sign-in account linked',
              )
            }
          />
        ) : null}
      </ModalDialog>
      <ModalDialog
        title={dialog?.employee ? `Driver license · ${dialog.employee.full_name}` : ''}
        isOpen={dialog?.kind === 'license'}
        onClose={closeDialog}
      >
        {dialog?.kind === 'license' ? (
          <LicenseContent
            employee={dialog.employee}
            canEdit={permissions.canEditLicense}
            isBusy={isBusy}
            failure={actionFailure}
            onLoad={handlers.onLoadLicense}
            onSave={handlers.onSaveLicense}
            onSaved={() => showToast('License saved')}
            onClose={closeDialog}
          />
        ) : null}
      </ModalDialog>
      <Toast toast={toast} />
    </section>
  )
}
