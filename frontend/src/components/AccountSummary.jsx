// ===== AI GENERATED: AccountSummary =====
// Purpose: Presentational view of the signed-in employee and capabilities
// Inputs: loadState, account, failure (props only)
// Returns: loading, error or account markup
// Flow:
// 1. Show a status message while loading or when access is denied
// 2. List roles and backend-confirmed capability levels

/**
 * @function AccountSummary
 * @description Pure UI for the current account; makes no API calls.
 * @param {{loadState: string, account: Object|null, failure: Object|null}} componentProps
 * @returns {import('react').ReactElement}
 */
export function AccountSummary({ loadState, account, failure }) {
  if (loadState === 'idle' || loadState === 'loading') {
    return <p role="status">Loading your account…</p>
  }
  if (loadState === 'failed') {
    return (
      <div role="alert" className="rounded border border-red-300 bg-red-50 p-4">
        <p className="font-semibold">{failure?.title ?? 'Something went wrong'}</p>
        <p>{failure?.detail}</p>
        {failure?.traceIdentifier ? (
          <p className="text-sm text-gray-600">Reference: {failure.traceIdentifier}</p>
        ) : null}
      </div>
    )
  }
  const capabilityEntries = Object.entries(account.capabilities)
  return (
    <section className="space-y-3">
      <h2 className="text-xl font-semibold">{account.full_name}</h2>
      <p>Roles: {account.role_codes.join(', ') || 'none assigned'}</p>
      <ul className="grid grid-cols-1 gap-1 sm:grid-cols-2">
        {capabilityEntries.map(([capabilityName, accessLevel]) => (
          <li key={capabilityName} className="flex justify-between rounded bg-gray-100 px-3 py-1">
            <span>{capabilityName}</span>
            <span className="font-mono text-sm">{accessLevel}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
