// ===== AI GENERATED: Toast =====
// Purpose: A small confirmation message in the corner
// Inputs: toast {message, tone} or null (props only)
// Returns: toast markup or nothing
// Flow:
// 1. Announced politely to screen readers; sits above the phone dock

import { Icon } from './Icon'

const TONE_CLASSES = { success: 'alert-success', error: 'alert-error', info: 'alert-info' }

/**
 * @function Toast
 * @description Pure UI toast.
 * @param {{toast: {message: string, tone: string}|null}} componentProps
 * @returns {import('react').ReactElement|null}
 */
export function Toast({ toast }) {
  if (!toast) return null
  return (
    <div className="toast toast-end toast-bottom z-50 mb-16 lg:mb-0">
      <div role="status" className={`alert ${TONE_CLASSES[toast.tone] ?? 'alert-success'} shadow-lg`}>
        <Icon name="check" className="h-5 w-5" />
        <span>{toast.message}</span>
      </div>
    </div>
  )
}
