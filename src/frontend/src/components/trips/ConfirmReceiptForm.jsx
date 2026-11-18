// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: ConfirmReceiptForm =====
// Purpose: The driver reports when the steel company received the OR
// Inputs: disabled flag, onConfirm callback (props only)
// Returns: small form markup
// Flow:
// 1. Receipt time defaults to now; the driver may adjust it
// 2. The parent sends it with an Idempotency-Key (safe to retry)
// 3. Confirming completes the trip; there is no dispatcher approval

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { localInputToIso, toLocalInputValue } from '../../shared/utils/forms'
import { Icon } from '../../shared/components/Icon'

/**
 * @function ConfirmReceiptForm
 * @description Pure UI for confirming company receipt.
 * @param {{disabled: boolean, onConfirm: function(string): Promise<boolean>}} componentProps
 * @returns {import('react').ReactElement}
 */
export function ConfirmReceiptForm({ disabled, onConfirm }) {
  return (
    <form
      className="space-y-2"
      onSubmit={async (event) => {
        event.preventDefault()
        const receivedAt = new FormData(event.currentTarget).get('received_at')
        await onConfirm(localInputToIso(receivedAt))
      }}
    >
      <fieldset className="fieldset">
        <legend className="fieldset-legend">When did the steel company receive the OR?</legend>
        <input
          name="received_at"
          type="datetime-local"
          // AI MODIFIED: Avoid rounding a receipt back before a same-minute delivery.
          step="0.001"
          required
          defaultValue={toLocalInputValue(new Date(), 'milliseconds')}
          className="input w-full"
        />
        <p className="label text-xs">
          Confirming completes the trip and frees the truck and crew for the next dispatch.
        </p>
      </fieldset>
      <button type="submit" disabled={disabled} className="btn btn-primary btn-sm">
        <Icon name="check" className="h-4 w-4" /> Confirm receipt
      </button>
    </form>
  )
}
