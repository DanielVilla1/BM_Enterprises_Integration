// ===== AI GENERATED: ErrorNotice =====
// Purpose: Show a normalized API failure
// Inputs: failure (props only)
// Returns: alert markup or nothing
// Flow:
// 1. Title and detail from the problem+json body
// 2. Field errors and the trace reference when present

/**
 * @function ErrorNotice
 * @description Pure UI for an ApiFailure.
 * @param {{failure: Object|null}} componentProps
 * @returns {import('react').ReactElement|null}
 */
export function ErrorNotice({ failure }) {
  if (!failure) return null
  return (
    <div role="alert" className="rounded border border-red-300 bg-red-50 p-3 text-sm">
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
        <p className="text-xs text-gray-600">Reference: {failure.traceIdentifier}</p>
      ) : null}
    </div>
  )
}
