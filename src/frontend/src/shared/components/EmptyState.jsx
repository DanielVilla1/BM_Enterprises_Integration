// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: EmptyState =====
// Purpose: A friendly message when a list has nothing to show
// Inputs: icon, title, description and an optional action (props only)
// Returns: centred card markup
// Flow:
// 1. Icon in a soft circle, short text, optional call-to-action

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { Icon } from './Icon'

/**
 * @function EmptyState
 * @description Pure UI empty state.
 * @param {{icon?: string, title: string, description?: string, action?: import('react').ReactNode}} componentProps
 * @returns {import('react').ReactElement}
 */
export function EmptyState({ icon = 'info', title, description, action }) {
  return (
    <div className="card card-border bg-base-100">
      <div className="card-body items-center py-12 text-center">
        <div className="mb-1 flex h-14 w-14 items-center justify-center rounded-full bg-base-200 text-base-content/60">
          <Icon name={icon} className="h-7 w-7" />
        </div>
        <h2 className="text-lg font-semibold">{title}</h2>
        {description ? (
          <p className="max-w-md text-sm text-base-content/70">{description}</p>
        ) : null}
        {action ? <div className="mt-3">{action}</div> : null}
      </div>
    </div>
  )
}
