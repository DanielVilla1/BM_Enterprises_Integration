// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: PreviewBanner =====
// Purpose: A clear label on screens that are design mockups, not connected to the backend
// Inputs: the sprint that will deliver the feature (props only)
// Returns: alert markup
// Flow:
// 1. Amber notice at the top of every mockup page so sample data is never mistaken for real data

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { Icon } from './Icon'

/**
 * @function PreviewBanner
 * @description Pure UI notice for mockup screens.
 * @param {{sprint: string}} componentProps
 * @returns {import('react').ReactElement}
 */
export function PreviewBanner({ sprint }) {
  return (
    <div role="note" className="alert alert-warning alert-soft items-start text-sm">
      <Icon name="info" className="mt-0.5 h-5 w-5 shrink-0" />
      <div>
        <p className="font-semibold">Design preview · coming soon</p>
        <p>
          This screen shows how the feature will look, with sample data. It is not connected yet;
          the backend arrives in {sprint}. Nothing here is real or can be saved.
        </p>
      </div>
    </div>
  )
}
