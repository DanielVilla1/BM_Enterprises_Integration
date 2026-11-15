// ===== AI GENERATED: DeliveryOrdersPanel =====
// Purpose: Delivery order list, encode form and cancel action
// Inputs: list state, clients, permissions and callbacks (props only)
// Returns: panel markup
// Flow:
// 1. List orders with status and weight
// 2. Encode form only when writing is allowed; clients come from props
// 3. Pending orders can be cancelled with a reason

import { compactPayload } from '../shared/utils/forms'
import { ErrorNotice } from './ErrorNotice'
import { ReasonForm } from './ReasonForm'

/**
 * @function DeliveryOrdersPanel
 * @description Pure UI for delivery orders.
 * @param {Object} componentProps Props: loadState, orders, clients, failure, actionFailure, isBusy, canWrite, onCreate, onCancel
 * @returns {import('react').ReactElement}
 */
export function DeliveryOrdersPanel({
  loadState,
  orders,
  clients,
  failure,
  actionFailure,
  isBusy,
  canWrite,
  onCreate,
  onCancel,
}) {
  const clientNames = Object.fromEntries(clients.map((clientRecord) => [clientRecord.client_id, clientRecord.name]))
  const activeClients = clients.filter((clientRecord) => clientRecord.is_active)
  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">Delivery orders</h2>
      <ErrorNotice failure={failure} />
      {loadState === 'loading' ? <p role="status">Loading…</p> : null}
      <ul className="divide-y rounded border">
        {orders.map((orderRecord) => (
          <li key={orderRecord.order_id} className="space-y-1 p-2">
            <div className="flex flex-wrap justify-between gap-2">
              <span className="font-medium">
                {clientNames[orderRecord.client_id] ?? 'Client'} · {orderRecord.scheduled_date}
              </span>
              <span className="font-mono text-sm">{orderRecord.status}</span>
            </div>
            <p className="text-sm">
              {orderRecord.pickup_location} → {orderRecord.delivery_location} · {orderRecord.total_weight_tons} t
            </p>
            {canWrite && orderRecord.status === 'PENDING' ? (
              <ReasonForm
                label="Cancel order"
                disabled={isBusy}
                onSubmit={(reasonText) => onCancel(orderRecord.order_id, reasonText)}
              />
            ) : null}
          </li>
        ))}
      </ul>
      {canWrite ? (
        <form
          className="grid gap-2 sm:grid-cols-2"
          onSubmit={async (event) => {
            event.preventDefault()
            const formElement = event.currentTarget
            const values = Object.fromEntries(new FormData(formElement))
            const payload = compactPayload({
              ...values,
              total_weight_tons: Number(values.total_weight_tons),
            })
            if (await onCreate(payload)) formElement.reset()
          }}
        >
          <select name="client_id" required aria-label="Client" className="rounded border px-2 py-1">
            <option value="">Select client</option>
            {activeClients.map((clientRecord) => (
              <option key={clientRecord.client_id} value={clientRecord.client_id}>
                {clientRecord.name}
              </option>
            ))}
          </select>
          <input name="client_reference" maxLength={64} placeholder="Client reference" aria-label="Client reference" className="rounded border px-2 py-1" />
          <input name="pickup_location" required minLength={3} maxLength={300} placeholder="Pickup location" aria-label="Pickup location" className="rounded border px-2 py-1" />
          <input name="delivery_location" required minLength={3} maxLength={300} placeholder="Delivery location" aria-label="Delivery location" className="rounded border px-2 py-1" />
          <input name="scheduled_date" type="date" required aria-label="Scheduled date" className="rounded border px-2 py-1" />
          <input name="total_weight_tons" type="number" required min="0.001" step="0.001" placeholder="Weight (tons)" aria-label="Weight in tons" className="rounded border px-2 py-1" />
          <input name="notes" maxLength={1000} placeholder="Notes" aria-label="Notes" className="rounded border px-2 py-1 sm:col-span-2" />
          <button type="submit" disabled={isBusy} className="rounded bg-gray-900 px-3 py-1 text-white sm:col-span-2">
            Record order
          </button>
          <div className="sm:col-span-2">
            <ErrorNotice failure={actionFailure} />
          </div>
        </form>
      ) : null}
    </section>
  )
}
