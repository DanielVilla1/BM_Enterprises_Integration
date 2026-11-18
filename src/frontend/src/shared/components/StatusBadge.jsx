// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: StatusBadge =====
// Purpose: A coloured pill for any order, trip, truck, license, employee or finance status
// Inputs: kind and status code (props only)
// Returns: badge markup using the shared labels and tones
// Flow:
// 1. describeStatus decides the words and the colour
// 2. Neutral statuses use an outline so they stay visible on both themes
// 3. Tone classes are listed in full so Tailwind keeps them

import { describeStatus } from '../utils/statusLabels'

const TONE_CLASSES = {
  info: 'badge-soft badge-info',
  primary: 'badge-soft badge-primary',
  success: 'badge-soft badge-success',
  warning: 'badge-soft badge-warning',
  error: 'badge-soft badge-error',
  accent: 'badge-soft badge-accent',
  neutral: 'badge-outline border-base-content/40 text-base-content/70',
}

/**
 * @function StatusBadge
 * @description Pure UI status pill.
 * @param {{kind: string, status: string}} componentProps
 * @returns {import('react').ReactElement}
 */
export function StatusBadge({ kind, status }) {
  const { label, tone } = describeStatus(kind, status)
  return <span className={`badge whitespace-nowrap ${TONE_CLASSES[tone]}`}>{label}</span>
}
