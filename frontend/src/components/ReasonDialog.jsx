// ===== AI GENERATED: ReasonDialog =====
// Purpose: Ask for a short reason before a consequential action (cancel, fail, correct...)
// Inputs: request {title, description, confirmLabel, onConfirm} or null, busy flag, close handler (props only)
// Returns: modal markup
// Flow:
// 1. Open while a request is set; the parent decides what confirming means
// 2. Closes only when the action succeeded; failures stay visible in the page notice

import { ErrorNotice } from './ErrorNotice'
import { FormField } from './FormField'
import { ModalDialog } from './ModalDialog'

/**
 * @function ReasonDialog
 * @description Pure UI reason prompt.
 * @param {{request: {title: string, description?: string, confirmLabel: string, onConfirm: function(string): Promise<boolean>}|null, isBusy: boolean, failure: Object|null, onClose: function(): void}} componentProps
 * @returns {import('react').ReactElement}
 */
export function ReasonDialog({ request, isBusy, failure, onClose }) {
  return (
    <ModalDialog title={request?.title ?? ''} isOpen={request !== null} onClose={onClose}>
      {request ? (
        <form
          className="space-y-4"
          onSubmit={async (event) => {
            event.preventDefault()
            const reason = new FormData(event.currentTarget).get('reason')
            if (await request.onConfirm(String(reason).trim())) onClose()
          }}
        >
          {request.description ? <p className="text-sm text-base-content/70">{request.description}</p> : null}
          <FormField label="Reason">
            <textarea
              name="reason"
              required
              minLength={3}
              maxLength={500}
              rows={3}
              className="textarea w-full"
              placeholder="A few words are enough"
            />
          </FormField>
          <ErrorNotice failure={failure} />
          <div className="modal-action">
            <button type="button" className="btn btn-ghost" onClick={onClose}>
              Back
            </button>
            <button type="submit" className="btn btn-primary" disabled={isBusy}>
              {request.confirmLabel}
            </button>
          </div>
        </form>
      ) : null}
    </ModalDialog>
  )
}
