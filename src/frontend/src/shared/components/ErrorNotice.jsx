// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: ErrorNotice =====
// Purpose: Show a normalized API failure as a clear alert
// Inputs: failure (props only)
// Returns: alert markup or nothing
// Flow:
// 1. Title and detail from the problem+json body
// 2. Field errors and the trace reference (for support) when present

import { Icon } from './Icon'

/**
 * @function ErrorNotice
 * @description Pure UI for an ApiFailure.
 * @param {{failure: Object|null}} componentProps
 * @returns {import('react').ReactElement|null}
 */
export function ErrorNotice({ failure }) {
  if (!failure) return null
  return (
    <div role="alert" className="alert alert-error alert-soft items-start text-sm">
      <Icon name="alert" className="mt-0.5 h-5 w-5 shrink-0" />
      <div className="space-y-1">
        <p className="font-semibold">{failure.title}</p>
        <p>{failure.detail}</p>
        {failure.fieldErrors?.length ? (
          <ul className="list-disc pl-5">
            {failure.fieldErrors.map((fieldError) => (
              <li key={`${fieldError.field}-${fieldError.message}`}>
                {fieldError.field}: {fieldError.message}
              </li>
            ))}
          </ul>
        ) : null}
        {failure.traceIdentifier ? (
          <p className="text-xs opacity-70">Reference: {failure.traceIdentifier}</p>
        ) : null}
      </div>
    </div>
  )
}
