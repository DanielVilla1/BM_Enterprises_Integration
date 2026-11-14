// ===== AI GENERATED: FleetPanel =====
// Purpose: Truck list, registration form and maintenance actions
// Inputs: list state, permissions and callbacks (props only)
// Returns: panel markup
// Flow:
// 1. List trucks with capacity and status
// 2. Writers can register trucks and start/complete maintenance
// 3. The backend decides which transitions are legal; failures show in the notice

import { compactPayload } from '../shared/utils/forms'
import { ErrorNotice } from './ErrorNotice'
import { ReasonForm } from './ReasonForm'

/**
 * @function FleetPanel
 * @description Pure UI for the fleet.
 * @param {Object} componentProps Props: loadState, trucks, failure, actionFailure, isBusy, canWrite, onCreate, onStartMaintenance, onCompleteMaintenance
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
  onStartMaintenance,
  onCompleteMaintenance,
}) {
  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">Fleet</h2>
      <ErrorNotice failure={failure} />
      {loadState === 'loading' ? <p role="status">Loading…</p> : null}
      <ul className="divide-y rounded border">
        {trucks.map((truckRecord) => (
          <li key={truckRecord.truck_id} className="space-y-1 p-2">
            <div className="flex flex-wrap justify-between gap-2">
              <span className="font-medium">
                {truckRecord.plate_number}
                {truckRecord.is_active ? '' : ' (retired)'}
              </span>
              <span className="font-mono text-sm">{truckRecord.status}</span>
            </div>
            <p className="text-sm">
              {truckRecord.description ?? 'No description'} · {truckRecord.capacity_tons} t capacity
            </p>
            {canWrite && truckRecord.status === 'AVAILABLE' ? (
              <ReasonForm
                label="Start maintenance"
                disabled={isBusy}
                onSubmit={(reasonText) => onStartMaintenance(truckRecord.truck_id, reasonText)}
              />
            ) : null}
            {canWrite && truckRecord.status === 'MAINTENANCE' ? (
              <button
                type="button"
                disabled={isBusy}
                onClick={() => onCompleteMaintenance(truckRecord.truck_id)}
                className="rounded bg-gray-900 px-2 py-1 text-sm text-white"
              >
                Complete maintenance
              </button>
            ) : null}
          </li>
        ))}
      </ul>
      {canWrite ? (
        <form
          className="grid gap-2 sm:grid-cols-3"
          onSubmit={async (event) => {
            event.preventDefault()
            const formElement = event.currentTarget
            const values = Object.fromEntries(new FormData(formElement))
            const payload = compactPayload({ ...values, capacity_tons: Number(values.capacity_tons) })
            if (await onCreate(payload)) formElement.reset()
          }}
        >
          <input name="plate_number" required minLength={2} maxLength={16} placeholder="Plate number" aria-label="Plate number" className="rounded border px-2 py-1" />
          <input name="description" maxLength={120} placeholder="Description" aria-label="Description" className="rounded border px-2 py-1" />
          <input name="capacity_tons" type="number" required min="0.001" max="100" step="0.001" placeholder="Capacity (tons)" aria-label="Capacity in tons" className="rounded border px-2 py-1" />
          <button type="submit" disabled={isBusy} className="rounded bg-gray-900 px-3 py-1 text-white sm:col-span-3">
            Register truck
          </button>
          <div className="sm:col-span-3">
            <ErrorNotice failure={actionFailure} />
          </div>
        </form>
      ) : null}
    </section>
  )
}
