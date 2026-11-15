// ===== AI GENERATED: FleetPanel =====
// Purpose: The fleet: stats, filters, truck cards, register, edit, maintenance and its history
// Inputs: list state, permissions and callbacks (props only)
// Returns: page markup
// Flow:
// 1. Stat cards and tabs summarise availability; each truck is a card
// 2. Maintenance start asks for a reason; the backend decides which transitions are legal
// 3. History loads on demand inside a dialog

import { useEffect, useState } from 'react'
import { useToast } from '../hooks/useToast'
import { buildChanges } from '../shared/utils/forms'
import { formatDateTime, formatTons } from '../shared/utils/formatting'
import { TRUCK_TABS, countTrucksByTab, filterTrucks, summarizeTrucks } from '../shared/utils/operations'
import { EmptyState } from './EmptyState'
import { ErrorNotice } from './ErrorNotice'
import { FilterTabs } from './FilterTabs'
import { FormField } from './FormField'
import { Icon } from './Icon'
import { ListSkeleton } from './ListSkeleton'
import { ModalDialog } from './ModalDialog'
import { PageHeader } from './PageHeader'
import { ReasonDialog } from './ReasonDialog'
import { RowMenu } from './RowMenu'
import { SearchField } from './SearchField'
import { StatCard } from './StatCard'
import { StatusBadge } from './StatusBadge'
import { Toast } from './Toast'

/**
 * @function TruckForm
 * @description Register or edit form for a truck.
 * @param {Object} componentProps Props: truck, isBusy, failure, onSubmit, onClose
 * @returns {import('react').ReactElement}
 */
function TruckForm({ truck, isBusy, failure, onSubmit, onClose }) {
  return (
    <form
      className="grid gap-x-4 sm:grid-cols-2"
      onSubmit={async (event) => {
        event.preventDefault()
        const formData = new FormData(event.currentTarget)
        await onSubmit({ ...Object.fromEntries(formData), is_active: formData.has('is_active') })
      }}
    >
      <FormField label="Plate number">
        <input name="plate_number" required minLength={2} maxLength={16} defaultValue={truck?.plate_number} className="input w-full uppercase" placeholder="ABC 1234" />
      </FormField>
      <FormField label="Capacity (metric tons)">
        <input name="capacity_tons" type="number" required min="0.001" max="100" step="0.001" defaultValue={truck?.capacity_tons} className="input w-full" />
      </FormField>
      <FormField label="Description (optional)" className="sm:col-span-2">
        <input name="description" maxLength={120} defaultValue={truck?.description ?? ''} className="input w-full" placeholder="10-wheeler, wing van…" />
      </FormField>
      {truck ? (
        <label className="label cursor-pointer justify-start gap-3 sm:col-span-2">
          <input type="checkbox" name="is_active" defaultChecked={truck.is_active} className="toggle toggle-primary" />
          <span>Active in the fleet (switch off to retire this truck)</span>
        </label>
      ) : null}
      <div className="sm:col-span-2">
        <ErrorNotice failure={failure} />
      </div>
      <div className="modal-action sm:col-span-2">
        <button type="button" className="btn btn-ghost" onClick={onClose}>
          Back
        </button>
        <button type="submit" className="btn btn-primary" disabled={isBusy}>
          {truck ? 'Save changes' : 'Register truck'}
        </button>
      </div>
    </form>
  )
}

/**
 * @function MaintenanceHistory
 * @description Loads and lists a truck's maintenance records.
 * @param {{truck: Object, onLoad: function(string): Promise<{records: Array<Object>, failure: Object|null}>}} componentProps
 * @returns {import('react').ReactElement}
 */
function MaintenanceHistory({ truck, onLoad }) {
  const [result, setResult] = useState(null)

  useEffect(() => {
    let cancelled = false
    onLoad(truck.truck_id).then((loaded) => {
      if (!cancelled) setResult(loaded)
    })
    return () => {
      cancelled = true
    }
  }, [onLoad, truck.truck_id])

  if (result === null) return <span className="loading loading-spinner" role="status" aria-label="Loading" />
  if (result.failure) return <ErrorNotice failure={result.failure} />
  if (result.records.length === 0) return <p className="text-sm text-base-content/70">No maintenance recorded for this truck.</p>
  return (
    <ul className="timeline timeline-vertical timeline-compact timeline-snap-icon">
      {result.records.map((record, position) => (
        <li key={record.record_id}>
          {position > 0 ? <hr /> : null}
          <div className="timeline-middle text-warning">
            <Icon name="wrench" className="h-4 w-4" />
          </div>
          <div className="timeline-end timeline-box mb-3 text-sm">
            <p className="font-semibold">{record.reason}</p>
            <p className="text-xs text-base-content/60">
              {formatDateTime(record.started_at)} → {record.ended_at ? formatDateTime(record.ended_at) : 'ongoing'}
            </p>
          </div>
          <hr />
        </li>
      ))}
    </ul>
  )
}

/**
 * @function FleetPanel
 * @description Pure UI for the fleet.
 * @param {Object} componentProps Props: loadState, trucks, failure, actionFailure, isBusy, canWrite, onCreate, onUpdate, onLoadMaintenance, onStartMaintenance, onCompleteMaintenance
 * @returns {import('react').ReactElement}
 */
export function FleetPanel({
  loadState,
  trucks,
  failure,
  actionFailure,
  isBusy,
  canWrite,
  onCreate,
  onUpdate,
  onLoadMaintenance,
  onStartMaintenance,
  onCompleteMaintenance,
}) {
  const [tabKey, setTabKey] = useState('all')
  const [query, setQuery] = useState('')
  const [formState, setFormState] = useState(null)
  const [historyTruck, setHistoryTruck] = useState(null)
  const [reasonRequest, setReasonRequest] = useState(null)
  const { toast, showToast } = useToast()
  const summary = summarizeTrucks(trucks)
  const visibleTrucks = filterTrucks(trucks, tabKey, query)
  const modalIsOpen = formState !== null || reasonRequest !== null

  const submitForm = async (values) => {
    const editing = formState.truck
    let succeeded
    if (editing) {
      const changes = buildChanges(editing, values, ['plate_number', 'description', 'capacity_tons'], ['capacity_tons'])
      if (values.is_active !== editing.is_active) changes.is_active = values.is_active
      succeeded = Object.keys(changes).length === 0 ? true : await onUpdate(editing.truck_id, changes)
    } else {
      const payload = { plate_number: values.plate_number, capacity_tons: Number(values.capacity_tons) }
      if (values.description?.trim()) payload.description = values.description.trim()
      succeeded = await onCreate(payload)
    }
    if (succeeded) {
      setFormState(null)
      showToast(editing ? 'Truck updated' : 'Truck registered')
    }
  }

  return (
    <section className="space-y-5">
      <PageHeader
        title="Fleet"
        subtitle="Trucks, capacity and maintenance"
        actions={
          canWrite ? (
            <button type="button" className="btn btn-primary" onClick={() => setFormState({ truck: null })}>
              <Icon name="plus" className="h-4 w-4" /> Register truck
            </button>
          ) : null
        }
      />
      <ErrorNotice failure={failure} />
      {!modalIsOpen ? <ErrorNotice failure={actionFailure} /> : null}

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Active trucks" value={summary.total} icon="truck" tone="neutral" />
        <StatCard label="Available" value={summary.available} icon="check" tone="success" hint="Ready for a new trip" />
        <StatCard label="On a trip" value={summary.working} icon="route" tone="primary" />
        <StatCard label="In maintenance" value={summary.maintenance} icon="wrench" tone="warning" />
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <FilterTabs tabs={TRUCK_TABS} activeKey={tabKey} counts={countTrucksByTab(trucks)} onChange={setTabKey} label="Truck status" />
        <SearchField value={query} onChange={setQuery} placeholder="Search plate or description" />
      </div>

      {loadState === 'loading' && trucks.length === 0 ? <ListSkeleton /> : null}
      {loadState !== 'loading' && visibleTrucks.length === 0 ? (
        <EmptyState
          icon="truck"
          title={trucks.length === 0 ? 'No trucks registered' : 'No trucks match'}
          description={trucks.length === 0 ? 'Register the first truck with its capacity so it can be assigned to trips.' : 'Try another tab or clear the search.'}
        />
      ) : null}

      {visibleTrucks.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {visibleTrucks.map((truckRecord) => (
            <article key={truckRecord.truck_id} className="card card-border bg-base-100">
              <div className="card-body gap-3 p-5">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h2 className="text-xl font-extrabold tracking-wider">{truckRecord.plate_number}</h2>
                    <p className="text-sm text-base-content/70">{truckRecord.description ?? 'No description'}</p>
                  </div>
                  <div className="flex items-center gap-1">
                    {truckRecord.is_active ? (
                      <StatusBadge kind="truck" status={truckRecord.status} />
                    ) : (
                      <span className="badge badge-outline border-base-content/40 text-base-content/70">Retired</span>
                    )}
                    <RowMenu
                      label="Truck actions"
                      items={[
                        ...(canWrite ? [{ label: 'Edit truck', onSelect: () => setFormState({ truck: truckRecord }) }] : []),
                        { label: 'Maintenance history', onSelect: () => setHistoryTruck(truckRecord) },
                      ]}
                    />
                  </div>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Icon name="truck" className="h-4 w-4 text-base-content/50" />
                  <span className="font-semibold tabular-nums">{formatTons(truckRecord.capacity_tons)}</span>
                  <span className="text-base-content/60">capacity</span>
                </div>
                {canWrite && truckRecord.is_active && truckRecord.status === 'AVAILABLE' ? (
                  <button
                    type="button"
                    className="btn btn-outline btn-warning btn-sm"
                    disabled={isBusy}
                    onClick={() =>
                      setReasonRequest({
                        title: `Start maintenance on ${truckRecord.plate_number}`,
                        description: 'The truck cannot be assigned until maintenance is completed.',
                        confirmLabel: 'Start maintenance',
                        onConfirm: async (reason) => {
                          const succeeded = await onStartMaintenance(truckRecord.truck_id, reason)
                          if (succeeded) showToast('Truck is in maintenance')
                          return succeeded
                        },
                      })
                    }
                  >
                    <Icon name="wrench" className="h-4 w-4" /> Start maintenance
                  </button>
                ) : null}
                {canWrite && truckRecord.status === 'MAINTENANCE' ? (
                  <button
                    type="button"
                    className="btn btn-success btn-sm"
                    disabled={isBusy}
                    onClick={async () => {
                      if (await onCompleteMaintenance(truckRecord.truck_id)) showToast('Truck is available again')
                    }}
                  >
                    <Icon name="check" className="h-4 w-4" /> Complete maintenance
                  </button>
                ) : null}
              </div>
            </article>
          ))}
        </div>
      ) : null}

      <ModalDialog title={formState?.truck ? 'Edit truck' : 'Register a truck'} isOpen={formState !== null} onClose={() => setFormState(null)}>
        <TruckForm
          truck={formState?.truck ?? null}
          isBusy={isBusy}
          failure={actionFailure}
          onSubmit={submitForm}
          onClose={() => setFormState(null)}
        />
      </ModalDialog>
      <ModalDialog
        title={historyTruck ? `Maintenance · ${historyTruck.plate_number}` : ''}
        isOpen={historyTruck !== null}
        onClose={() => setHistoryTruck(null)}
      >
        {historyTruck ? <MaintenanceHistory truck={historyTruck} onLoad={onLoadMaintenance} /> : null}
      </ModalDialog>
      <ReasonDialog request={reasonRequest} isBusy={isBusy} failure={actionFailure} onClose={() => setReasonRequest(null)} />
      <Toast toast={toast} />
    </section>
  )
}
