// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: StatCard =====
// Purpose: A single number with a label, for dashboards and summaries
// Inputs: label, value, icon, tone, hint and an optional click handler (props only)
// Returns: card markup
// Flow:
// 1. Big value, small label, coloured icon chip
// 2. Becomes a button when it can take the user somewhere

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { Icon } from './Icon'

const TONE_CHIP = {
  primary: 'bg-primary/15 text-primary',
  success: 'bg-success/15 text-success',
  warning: 'bg-warning/15 text-warning',
  info: 'bg-info/15 text-info',
  error: 'bg-error/15 text-error',
  neutral: 'bg-base-300 text-base-content/70',
}

/**
 * @function StatCard
 * @description Pure UI statistic card.
 * @param {{label: string, value: string|number, icon: string, tone?: string, hint?: string, onClick?: function(): void}} componentProps
 * @returns {import('react').ReactElement}
 */
export function StatCard({ label, value, icon, tone = 'neutral', hint, onClick }) {
  const content = (
    <div className="card-body gap-2 p-4">
      <div className="flex items-center justify-between">
        <span className="text-sm text-base-content/70">{label}</span>
        <span
          className={`flex h-9 w-9 items-center justify-center rounded-field ${TONE_CHIP[tone]}`}
        >
          <Icon name={icon} className="h-5 w-5" />
        </span>
      </div>
      <div className="text-3xl font-bold tabular-nums">{value}</div>
      {hint ? <p className="text-xs text-base-content/60">{hint}</p> : null}
    </div>
  )
  if (onClick) {
    return (
      <button
        type="button"
        onClick={onClick}
        className="card card-border bg-base-100 text-left transition hover:border-primary/50"
      >
        {content}
      </button>
    )
  }
  return <div className="card card-border bg-base-100">{content}</div>
}
