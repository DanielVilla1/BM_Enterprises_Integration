// ===== AI GENERATED: ReasonForm =====
// Purpose: Small inline form asking for a reason before an action
// Inputs: label, disabled, onSubmit (props only)
// Returns: collapsible form markup
// Flow:
// 1. Collapsed by default so lists stay compact
// 2. Submit passes the typed reason up; the parent decides what it means

/**
 * @function ReasonForm
 * @description Pure UI that collects a short reason.
 * @param {{label: string, disabled: boolean, onSubmit: function(string): Promise<boolean>}} componentProps
 * @returns {import('react').ReactElement}
 */
export function ReasonForm({ label, disabled, onSubmit }) {
  return (
    <details className="inline-block">
      <summary className="cursor-pointer text-sm underline">{label}</summary>
      <form
        className="mt-1 flex gap-2"
        onSubmit={async (event) => {
          event.preventDefault()
          const formElement = event.currentTarget
          const submitted = await onSubmit(new FormData(formElement).get('reason'))
          if (submitted) formElement.reset()
        }}
      >
        <input
          name="reason"
          required
          minLength={3}
          maxLength={500}
          placeholder="Reason"
          aria-label={`${label} reason`}
          className="rounded border px-2 py-1 text-sm"
        />
        <button type="submit" disabled={disabled} className="rounded bg-gray-900 px-2 py-1 text-sm text-white">
          Confirm
        </button>
      </form>
    </details>
  )
}
