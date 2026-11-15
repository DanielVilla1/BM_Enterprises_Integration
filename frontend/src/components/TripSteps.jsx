// ===== AI GENERATED: TripSteps =====
// Purpose: A progress tracker showing where a trip is in its life
// Inputs: trip status (props only)
// Returns: full steps on wider screens, a compact "step n of 7" bar on phones; nothing for failed or cancelled trips
// Flow:
// 1. Steps up to the current status are highlighted
// 2. Phones get a short label and a progress bar so nothing is cut off

import { TRIP_STEPS, tripStepIndex } from '../shared/utils/statusLabels'

/**
 * @function TripSteps
 * @description Pure UI trip progress.
 * @param {{status: string}} componentProps
 * @returns {import('react').ReactElement|null}
 */
export function TripSteps({ status }) {
  const currentIndex = tripStepIndex(status)
  if (currentIndex < 0) return null
  return (
    <>
      <div className="space-y-1 sm:hidden">
        <p className="flex justify-between text-xs text-base-content/70">
          <span className="font-semibold text-base-content">{TRIP_STEPS[currentIndex].label}</span>
          <span>
            Step {currentIndex + 1} of {TRIP_STEPS.length}
          </span>
        </p>
        <progress className="progress progress-primary h-2 w-full" value={currentIndex + 1} max={TRIP_STEPS.length} aria-label="Trip progress" />
      </div>
      <ul className="steps steps-horizontal hidden w-full text-[11px] sm:inline-grid" aria-label="Trip progress">
        {TRIP_STEPS.map((step, position) => (
          <li key={step.status} className={`step ${position <= currentIndex ? 'step-primary' : ''}`}>
            {step.label}
          </li>
        ))}
      </ul>
    </>
  )
}
