// ===== AI GENERATED: MyTripsPanel =====
// Purpose: A crew member's trips; the driver sees the next step button
// Inputs: trips, employee id, callbacks (props only)
// Returns: panel markup
// Flow:
// 1. Show route, date, load and status for each trip
// 2. Offer accept / depart / deliver only to the assigned driver
// 3. Failures (for example a blocked dispatch) show in the notice

import { crewProgressAction } from '../shared/utils/dispatch'
import { ErrorNotice } from './ErrorNotice'

/**
 * @function MyTripsPanel
 * @description Pure UI for a crew member's trips.
 * @param {Object} componentProps Props: loadState, trips, employeeIdentifier, failure, actionFailure, isBusy, onProgress
 * @returns {import('react').ReactElement}
 */
export function MyTripsPanel({
  loadState,
  trips,
  employeeIdentifier,
  failure,
  actionFailure,
  isBusy,
  onProgress,
}) {
  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">My trips</h2>
      <ErrorNotice failure={failure} />
      <ErrorNotice failure={actionFailure} />
      {loadState === 'loading' ? <p role="status">Loading…</p> : null}
      {loadState === 'ready' && trips.length === 0 ? <p>No trips assigned.</p> : null}
      <ul className="divide-y rounded border">
        {trips.map((tripRecord) => {
          const nextAction = crewProgressAction(tripRecord, employeeIdentifier)
          return (
            <li key={tripRecord.trip_id} className="space-y-1 p-2">
              <div className="flex flex-wrap justify-between gap-2">
                <span className="font-medium">{tripRecord.scheduled_date}</span>
                <span className="font-mono text-sm">{tripRecord.status}</span>
              </div>
              <p className="text-sm">
                {tripRecord.pickup_location} → {tripRecord.delivery_location} · {tripRecord.load_tons} t
              </p>
              {nextAction ? (
                <button
                  type="button"
                  disabled={isBusy}
                  onClick={() => onProgress(tripRecord.trip_id, nextAction.name)}
                  className="rounded bg-gray-900 px-3 py-1 text-white"
                >
                  {nextAction.label}
                </button>
              ) : null}
            </li>
          )
        })}
      </ul>
    </section>
  )
}
