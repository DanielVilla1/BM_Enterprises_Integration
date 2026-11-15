// ===== AI GENERATED: ConfirmReceiptForm =====
// Purpose: The driver reports when the steel company received the OR
// Inputs: disabled flag, onConfirm callback (props only)
// Returns: small form markup
// Flow:
// 1. Receipt time defaults to now; the driver may adjust it
// 2. The parent sends it with an Idempotency-Key (safe to retry)
// 3. Confirming completes the trip; there is no dispatcher approval

import { localInputToIso, toLocalInputValue } from '../shared/utils/forms'

/**
 * @function ConfirmReceiptForm
 * @description Pure UI for confirming company receipt.
 * @param {{disabled: boolean, onConfirm: function(string): Promise<boolean>}} componentProps
 * @returns {import('react').ReactElement}
 */
export function ConfirmReceiptForm({ disabled, onConfirm }) {
  return (
    <form
      className="flex flex-wrap items-end gap-2"
      onSubmit={async (event) => {
        event.preventDefault()
        const receivedAt = new FormData(event.currentTarget).get('received_at')
        await onConfirm(localInputToIso(receivedAt))
      }}
    >
      <label className="text-sm">
        Steel company received the OR at
        <input
          name="received_at"
          type="datetime-local"
          required
          defaultValue={toLocalInputValue(new Date())}
          className="mt-1 block rounded border px-2 py-1"
        />
      </label>
      <button type="submit" disabled={disabled} className="rounded bg-gray-900 px-3 py-1 text-white">
        Confirm receipt
      </button>
    </form>
  )
}
