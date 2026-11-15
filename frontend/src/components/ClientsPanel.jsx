// ===== AI GENERATED: ClientsPanel =====
// Purpose: Client list and create form
// Inputs: list state, permissions and callbacks (props only)
// Returns: panel markup
// Flow:
// 1. Show loading / error / list
// 2. Show the create form only when writing is allowed
// 3. Emit the cleaned payload through onCreate

import { compactPayload } from '../shared/utils/forms'
import { ErrorNotice } from './ErrorNotice'

/**
 * @function ClientsPanel
 * @description Pure UI for clients.
 * @param {Object} componentProps Props: loadState, clients, failure, actionFailure, isBusy, canWrite, onCreate
 * @returns {import('react').ReactElement}
 */
export function ClientsPanel({ loadState, clients, failure, actionFailure, isBusy, canWrite, onCreate }) {
  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">Clients</h2>
      <ErrorNotice failure={failure} />
      {loadState === 'loading' ? <p role="status">Loading…</p> : null}
      <ul className="divide-y rounded border">
        {clients.map((clientRecord) => (
          <li key={clientRecord.client_id} className="flex justify-between p-2">
            <span>
              {clientRecord.name}
              {clientRecord.contact_person ? ` · ${clientRecord.contact_person}` : ''}
            </span>
            {clientRecord.is_active ? null : <span className="text-sm text-gray-600">inactive</span>}
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
            if (await onCreate(compactPayload(values))) formElement.reset()
          }}
        >
          <input name="name" required maxLength={160} placeholder="Client name" aria-label="Client name" className="rounded border px-2 py-1" />
          <input name="address" maxLength={300} placeholder="Address" aria-label="Address" className="rounded border px-2 py-1" />
          <input name="contact_person" maxLength={120} placeholder="Contact person" aria-label="Contact person" className="rounded border px-2 py-1" />
          <input name="contact_phone" maxLength={32} placeholder="Contact phone" aria-label="Contact phone" className="rounded border px-2 py-1" />
          <button type="submit" disabled={isBusy} className="rounded bg-gray-900 px-3 py-1 text-white sm:col-span-2">
            Add client
          </button>
          <div className="sm:col-span-2">
            <ErrorNotice failure={actionFailure} />
          </div>
        </form>
      ) : null}
    </section>
  )
}
