// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: PageHeader =====
// Purpose: Consistent page title, subtitle and action buttons
// Inputs: title, subtitle, actions (props only)
// Returns: header markup
// Flow:
// 1. Title and subtitle on the left, actions wrap underneath on small screens

/**
 * @function PageHeader
 * @description Pure UI page heading.
 * @param {{title: string, subtitle?: string, actions?: import('react').ReactNode}} componentProps
 * @returns {import('react').ReactElement}
 */
export function PageHeader({ title, subtitle, actions }) {
  return (
    <header className="flex flex-wrap items-end justify-between gap-3">
      <div className="min-w-0">
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        {subtitle ? <p className="text-sm text-base-content/70">{subtitle}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </header>
  )
}
