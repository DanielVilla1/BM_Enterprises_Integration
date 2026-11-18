// ===== AI GENERATED: ListSkeleton =====
// Purpose: Placeholder rows shown while a list loads
// Inputs: number of rows (props only)
// Returns: pulsing skeleton markup
// Flow:
// 1. Rows imitate a real list row so the layout does not jump when data arrives

/**
 * @function ListSkeleton
 * @description Pure UI loading placeholder.
 * @param {{rows?: number}} componentProps
 * @returns {import('react').ReactElement}
 */
export function ListSkeleton({ rows = 4 }) {
  return (
    <div className="card card-border bg-base-100" role="status" aria-label="Loading">
      <div className="divide-y divide-base-300">
        {Array.from({ length: rows }, (_unused, position) => (
          <div key={position} className="flex items-center gap-4 p-4">
            <div className="skeleton h-12 w-12 shrink-0 rounded-box" />
            <div className="flex flex-1 flex-col gap-2">
              <div className="skeleton h-4 w-2/5" />
              <div className="skeleton h-3 w-3/5" />
            </div>
            <div className="skeleton hidden h-6 w-20 sm:block" />
          </div>
        ))}
      </div>
    </div>
  )
}
