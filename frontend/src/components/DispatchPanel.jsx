// ===== AI GENERATED: DispatchPanel =====
// Purpose: Assign trips and manage them (clear dispatch, cancel, fail)
// Inputs: trips, orders, availability, permissions, callbacks (props only)
// Returns: panel markup
// Flow:
// 1. Assignment form: unavailable trucks and crew are shown disabled with the reason
// 2. Trip list with the actions that fit each status
// 3. Backend rule failures (capacity, blocked dispatch) show in the notice

import { assignableOrders, describeBlockReason, dispatcherActions } from '../shared/utils/dispatch'
import { compactPayload } from '../shared/utils/forms'
import { ErrorNotice } from './ErrorNotice'
import { ReasonForm } from './ReasonForm'

/**
 * @function ResourceOptions
 * @description Option list that disables unavailable resources and says why.
 * @param {{resources: Array<Object>}} componentProps
 * @returns {import('react').ReactElement}
 */
function ResourceOptions({ resources }) {
  return resources.map((resourceRecord) => (
    <option
      key={resourceRecord.resource_id}
      value={resourceRecord.resource_id}
      disabled={!resourceRecord.can_receive_assignment}
    >
      {resourceRecord.name}
      {resourceRecord.capacity_tons ? ` (${resourceRecord.capacity_tons} t)` : ''}
      {resourceRecord.can_receive_assignment ? '' : ` — ${describeBlockReason(resourceRecord.reason)}`}
    </option>
  ))
}

/**
 * @function DispatchPanel
 * @description Pure UI for dispatching.
 * @param {Object} componentProps Props: loadState, trips, orders, resources, failure, actionFailure, isBusy, canWrite, onAssign, onClear, onClose
 * @returns {import('react').ReactElement}
 */
export function DispatchPanel({
  loadState,
  trips,
  orders,
  resources,
  failure,
  actionFailure,
  isBusy,
  canWrite,
  onAssign,
  onClear,
  onClose,
}) {
  const openOrders = assignableOrders(orders)
  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">Dispatch</h2>
      <ErrorNotice failure={failure} />
      {loadState === 'loading' ? <p role="status">Loading…</p> : null}
      {canWrite ? (
        <form
          className="grid gap-2 sm:grid-cols-2"
          onSubmit={async (event) => {
            event.preventDefault()
            const formElement = event.currentTarget
            const values = Object.fromEntries(new FormData(formElement))
            const helperIds = [values.helper_one, values.helper_two].filter(Boolean)
            const assignment = compactPayload({
              truck_id: values.truck_id,
              driver_id: values.driver_id,
              load_tons: Number(values.load_tons),
            })
            if (await onAssign(values.order_id, { ...assignment, helper_ids: helperIds })) {
              formElement.reset()
            }
          }}
        >
          <select name="order_id" required aria-label="Order" className="rounded border px-2 py-1 sm:col-span-2">
            <option value="">Select order</option>
            {openOrders.map((orderRecord) => (
              <option key={orderRecord.order_id} value={orderRecord.order_id}>
                {orderRecord.scheduled_date} · {orderRecord.delivery_location} · {orderRecord.total_weight_tons} t ({orderRecord.status})
              </option>
            ))}
          </select>
          <select name="truck_id" required aria-label="Truck" className="rounded border px-2 py-1">
            <option value="">Select truck</option>
            <ResourceOptions resources={resources.trucks} />
          </select>
          <select name="driver_id" required aria-label="Driver" className="rounded border px-2 py-1">
            <option value="">Select driver</option>
            <ResourceOptions resources={resources.drivers} />
          </select>
          <select name="helper_one" required aria-label="Helper 1" className="rounded border px-2 py-1">
            <option value="">Select helper 1</option>
            <ResourceOptions resources={resources.helpers} />
          </select>
          <select name="helper_two" aria-label="Helper 2 (optional)" className="rounded border px-2 py-1">
            <option value="">Helper 2 (optional)</option>
            <ResourceOptions resources={resources.helpers} />
          </select>
          <input name="load_tons" type="number" required min="0.001" step="0.001" placeholder="Load (tons)" aria-label="Load in tons" className="rounded border px-2 py-1 sm:col-span-2" />
          <button type="submit" disabled={isBusy} className="rounded bg-gray-900 px-3 py-1 text-white sm:col-span-2">
            Assign trip
          </button>
          <div className="sm:col-span-2">
            <ErrorNotice failure={actionFailure} />
          </div>
        </form>
      ) : null}
      <ul className="divide-y rounded border">
        {trips.map((tripRecord) => {
          const available = dispatcherActions(tripRecord)
          return (
            <li key={tripRecord.trip_id} className="space-y-1 p-2">
              <div className="flex flex-wrap justify-between gap-2">
                <span className="font-medium">
                  {tripRecord.scheduled_date} · {tripRecord.delivery_location}
                </span>
                <span className="font-mono text-sm">{tripRecord.status}</span>
              </div>
              <p className="text-sm">{tripRecord.load_tons} t</p>
              {canWrite && available.canClear ? (
                <button
                  type="button"
                  disabled={isBusy}
                  onClick={() => onClear(tripRecord.trip_id)}
                  className="rounded bg-gray-900 px-2 py-1 text-sm text-white"
                >
                  Clear for dispatch
                </button>
              ) : null}
              {canWrite && available.canCancel ? (
                <ReasonForm
                  label="Cancel trip"
                  disabled={isBusy}
                  onSubmit={(reasonText) => onClose(tripRecord.trip_id, 'cancel', reasonText)}
                />
              ) : null}
              {canWrite && available.canFail ? (
                <ReasonForm
                  label="Mark failed"
                  disabled={isBusy}
                  onSubmit={(reasonText) => onClose(tripRecord.trip_id, 'fail', reasonText)}
                />
              ) : null}
            </li>
          )
        })}
      </ul>
    </section>
  )
}
