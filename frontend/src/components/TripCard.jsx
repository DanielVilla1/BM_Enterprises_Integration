// ===== AI GENERATED: TripCard =====
// Purpose: One trip on the dispatch board: route, crew, progress and its actions
// Inputs: trip, readable names, permissions and bound handlers (props only)
// Returns: card markup
// Flow:
// 1. Names come from the dispatch resources lookup, never raw ids
// 2. The main action (clear for dispatch) is a button; the rest live in the card menu
// 3. Which actions appear follows the trip's status; the backend still enforces the rules

import { dispatcherActions } from '../shared/utils/dispatch'
import { formatDate, formatTons } from '../shared/utils/formatting'
import { tripStepIndex, TRIP_STEPS } from '../shared/utils/statusLabels'
import { DocumentLinks } from './DocumentLinks'
import { Icon } from './Icon'
import { RowMenu } from './RowMenu'
import { StatusBadge } from './StatusBadge'

/**
 * @function TripCard
 * @description Pure UI for a dispatch board card.
 * @param {Object} componentProps Props: trip, clientName, lookup, canWrite, canCorrect, isBusy, handlers
 * @returns {import('react').ReactElement}
 */
export function TripCard({ trip, clientName, lookup, canWrite, canCorrect, isBusy, handlers }) {
  const available = dispatcherActions(trip)
  const stepIndex = tripStepIndex(trip.status)
  const helperNames = trip.helper_ids.map((identifier) => lookup.people[identifier] ?? 'Unknown').join(', ')
  const menuItems = []
  if (canWrite && available.canChangeCrew) menuItems.push({ label: 'Change crew', onSelect: handlers.changeCrew })
  if (canWrite && available.canReplaceTruck) menuItems.push({ label: 'Replace truck', onSelect: handlers.replaceTruck })
  if (canWrite && available.canCancel) menuItems.push({ label: 'Cancel trip', danger: true, onSelect: handlers.cancel })
  if (canWrite && available.canFail) menuItems.push({ label: 'Mark as failed', danger: true, onSelect: handlers.fail })
  if (canCorrect && trip.status === 'COMPLETED') {
    menuItems.push({ label: 'Correct receipt confirmation', danger: true, onSelect: handlers.correct })
  }

  return (
    <article className="card card-border bg-base-100">
      <div className="card-body gap-3 p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="truncate font-semibold">{clientName}</p>
            <p className="text-xs text-base-content/60">
              {formatDate(trip.scheduled_date)} · {formatTons(trip.load_tons)}
            </p>
          </div>
          <RowMenu label="Trip actions" items={menuItems} />
        </div>
        <StatusBadge kind="trip" status={trip.status} />
        <div className="space-y-1 text-sm">
          <p className="flex items-start gap-2">
            <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-base-content/40" />
            <span>{trip.pickup_location}</span>
          </p>
          <p className="flex items-start gap-2">
            <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary" />
            <span>{trip.delivery_location}</span>
          </p>
        </div>
        <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm">
          <dt className="text-base-content/60">Truck</dt>
          <dd className="font-medium">{lookup.trucks[trip.truck_id] ?? 'Unknown'}</dd>
          <dt className="text-base-content/60">Driver</dt>
          <dd className="font-medium">{lookup.people[trip.driver_id] ?? 'Unknown'}</dd>
          <dt className="text-base-content/60">Helpers</dt>
          <dd className="font-medium">{helperNames || '—'}</dd>
        </dl>
        {stepIndex >= 0 ? (
          <progress
            className="progress progress-primary h-1.5 w-full"
            value={stepIndex + 1}
            max={TRIP_STEPS.length}
            aria-label={`Trip progress: step ${stepIndex + 1} of ${TRIP_STEPS.length}`}
          />
        ) : null}
        {trip.closed_reason ? <p className="text-xs text-base-content/60">Reason: {trip.closed_reason}</p> : null}
        <DocumentLinks documents={trip.documents} disabled={isBusy} onOpen={handlers.openDocument} />
        {canWrite && available.canClear ? (
          <button type="button" className="btn btn-primary btn-sm" disabled={isBusy} onClick={handlers.clear}>
            <Icon name="check" className="h-4 w-4" /> Clear for dispatch
          </button>
        ) : null}
      </div>
    </article>
  )
}
