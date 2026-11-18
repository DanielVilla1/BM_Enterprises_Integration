// ===== AI GENERATED: DashboardPanel =====
// Purpose: The dispatcher's and owner's home: what is happening and what needs attention
// Inputs: loaded snapshot of orders, trips, trucks and resources, plus navigation (props only)
// Returns: page markup
// Flow:
// 1. Greeting and four headline numbers that link to the screen behind them
// 2. "Needs attention": trips waiting for a person to act
// 3. Orders still to assign, and a fleet availability breakdown

import { firstNameOf, formatDate, formatTons, greetingFor } from '../shared/utils/formatting'
import { attentionItems, buildNameLookup, summarizeOperations, summarizeTrucks } from '../shared/utils/operations'
import { EmptyState } from './EmptyState'
import { ErrorNotice } from './ErrorNotice'
import { Icon } from './Icon'
import { PageHeader } from './PageHeader'
import { StatCard } from './StatCard'
import { StatusBadge } from './StatusBadge'

const ATTENTION_ICON = { clear: 'check', upload: 'upload', receipt: 'document' }
const ATTENTION_TONE = { clear: 'bg-warning/15 text-warning', upload: 'bg-info/15 text-info', receipt: 'bg-accent/20 text-accent' }

/**
 * @function FleetBar
 * @description One labelled bar in the fleet breakdown.
 * @param {{label: string, value: number, total: number, tone: string}} componentProps
 * @returns {import('react').ReactElement}
 */
function FleetBar({ label, value, total, tone }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span>{label}</span>
        <span className="font-semibold tabular-nums">{value}</span>
      </div>
      <progress className={`progress ${tone} h-2 w-full`} value={total === 0 ? 0 : value} max={Math.max(total, 1)} aria-label={label} />
    </div>
  )
}

/**
 * @function DashboardPanel
 * @description Pure UI for the operations dashboard.
 * @param {Object} componentProps Props: loadState, snapshot, failure, userName, onOpenPage
 * @returns {import('react').ReactElement}
 */
export function DashboardPanel({ loadState, snapshot, failure, userName, onOpenPage }) {
  const loading = loadState === 'idle' || loadState === 'loading'
  const summary = summarizeOperations(snapshot)
  const fleet = summarizeTrucks(snapshot.trucks)
  const attention = attentionItems(snapshot.trips)
  const lookup = buildNameLookup(snapshot.resources)
  const ordersToAssign = snapshot.orders
    .filter((orderRecord) => ['PENDING', 'PARTIALLY_ASSIGNED'].includes(orderRecord.status))
    .sort((left, right) => left.scheduled_date.localeCompare(right.scheduled_date))
    .slice(0, 5)

  return (
    <section className="space-y-6">
      <PageHeader
        title={`${greetingFor(new Date().getHours())}, ${firstNameOf(userName)}`}
        subtitle="Here is what is happening across your operation"
      />
      <ErrorNotice failure={failure} />

      {loading ? (
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4" role="status" aria-label="Loading">
          {[0, 1, 2, 3].map((position) => (
            <div key={position} className="skeleton h-28 w-full" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          <StatCard label="Orders to assign" value={summary.pendingOrders} icon="clipboard" tone="warning" hint="Waiting for a truck and crew" onClick={() => onOpenPage('orders')} />
          <StatCard label="Trips in progress" value={summary.activeTrips} icon="route" tone="primary" hint={`${summary.inTransit} on the road`} onClick={() => onOpenPage('dispatch')} />
          <StatCard label="Awaiting receipt" value={summary.awaitingReceipt} icon="document" tone="info" hint="Delivered, OR not yet received" onClick={() => onOpenPage('dispatch')} />
          <StatCard label="Trucks available" value={summary.availableTrucks} icon="truck" tone="success" hint={`${summary.maintenanceTrucks} in maintenance`} onClick={() => onOpenPage('fleet')} />
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="card card-border bg-base-100 lg:col-span-2">
          <div className="card-body gap-3 p-5">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Needs attention</h2>
              <button type="button" className="btn btn-ghost btn-sm" onClick={() => onOpenPage('dispatch')}>
                Open dispatch <Icon name="arrow" className="h-4 w-4" />
              </button>
            </div>
            {!loading && attention.length === 0 ? (
              <EmptyState icon="check" title="All caught up" description="No trip is waiting for you right now." />
            ) : null}
            <ul className="divide-y divide-base-300">
              {attention.slice(0, 6).map((entry) => (
                <li key={entry.trip.trip_id} className="flex items-center gap-3 py-3">
                  <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${ATTENTION_TONE[entry.kind]}`}>
                    <Icon name={ATTENTION_ICON[entry.kind]} className="h-5 w-5" />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{entry.message}</p>
                    <p className="truncate text-xs text-base-content/60">
                      {entry.trip.delivery_location} · {lookup.trucks[entry.trip.truck_id] ?? 'Truck'} · {lookup.people[entry.trip.driver_id] ?? 'Driver'}
                    </p>
                  </div>
                  <StatusBadge kind="trip" status={entry.trip.status} />
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="card card-border bg-base-100">
          <div className="card-body gap-4 p-5">
            <h2 className="text-lg font-semibold">Fleet right now</h2>
            <FleetBar label="Available" value={fleet.available} total={fleet.total} tone="progress-success" />
            <FleetBar label="On a trip" value={fleet.working} total={fleet.total} tone="progress-primary" />
            <FleetBar label="In maintenance" value={fleet.maintenance} total={fleet.total} tone="progress-warning" />
            <p className="text-xs text-base-content/60">{fleet.total} active trucks · {summary.blockedResources} trucks or crew unavailable for new trips</p>
          </div>
        </div>
      </div>

      <div className="card card-border bg-base-100">
        <div className="card-body gap-3 p-5">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Next orders to assign</h2>
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => onOpenPage('orders')}>
              All orders <Icon name="arrow" className="h-4 w-4" />
            </button>
          </div>
          {!loading && ordersToAssign.length === 0 ? <p className="text-sm text-base-content/70">Every order has trips assigned.</p> : null}
          <ul className="divide-y divide-base-300">
            {ordersToAssign.map((orderRecord) => (
              <li key={orderRecord.order_id} className="flex flex-wrap items-center gap-3 py-3">
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{orderRecord.delivery_location}</p>
                  <p className="text-xs text-base-content/60">{formatDate(orderRecord.scheduled_date)} · {formatTons(orderRecord.total_weight_tons)}</p>
                </div>
                <StatusBadge kind="order" status={orderRecord.status} />
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
