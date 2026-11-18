// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: FullPageNotice =====
// Purpose: A centred full-page message for loading, errors and setup problems
// Inputs: tone, title, message, busy flag and optional extra content (props only)
// Returns: page markup
// Flow:
// 1. Spinner while busy, otherwise a coloured icon

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { Icon } from './Icon'

const TONE_ICON = { error: 'alert', warning: 'alert', info: 'info' }
const TONE_CHIP = {
  error: 'bg-error/15 text-error',
  warning: 'bg-warning/15 text-warning',
  info: 'bg-info/15 text-info',
}

/**
 * @function FullPageNotice
 * @description Pure UI full-page message.
 * @param {{tone?: string, title: string, message?: string, busy?: boolean, children?: import('react').ReactNode}} componentProps
 * @returns {import('react').ReactElement}
 */
export function FullPageNotice({ tone = 'info', title, message, busy = false, children }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-base-200 p-6">
      <div className="card card-border w-full max-w-md bg-base-100">
        <div className="card-body items-center gap-3 text-center" role={busy ? 'status' : 'alert'}>
          {busy ? (
            <span className="loading loading-spinner loading-lg text-primary" />
          ) : (
            <span
              className={`flex h-14 w-14 items-center justify-center rounded-full ${TONE_CHIP[tone]}`}
            >
              <Icon name={TONE_ICON[tone]} className="h-7 w-7" />
            </span>
          )}
          <h1 className="text-xl font-bold">{title}</h1>
          {message ? <p className="text-sm text-base-content/70">{message}</p> : null}
          {children}
        </div>
      </div>
    </div>
  )
}
