// ===== AI GENERATED: BillingPreview =====
// Purpose: Design mockup of client billing: unbilled trips, batches, invoice and payment status
// Inputs: none (sample data only)
// Returns: page markup with disabled actions
// Flow:
// 1. Unbilled trips carry forward to later periods without blocking others
// 2. Billing readiness, batch, invoice status and payment status are separate states

import { useState } from 'react'
import { SAMPLE_BATCHES, SAMPLE_UNBILLED_TRIPS } from '../shared/mockups/sampleData'
import { formatPeso } from '../shared/utils/formatting'
import { FilterTabs } from './FilterTabs'
import { PageHeader } from './PageHeader'
import { PreviewBanner } from './PreviewBanner'
import { StatCard } from './StatCard'
import { StatusBadge } from './StatusBadge'

const TABS = [
  { key: 'unbilled', label: 'Unbilled trips' },
  { key: 'batches', label: 'Batches & payments' },
]

/**
 * @function BillingPreview
 * @description Pure UI mockup for billing.
 * @returns {import('react').ReactElement}
 */
export function BillingPreview() {
  const [tabKey, setTabKey] = useState('unbilled')
  const unbilledTotal = SAMPLE_UNBILLED_TRIPS.reduce((sum, entry) => sum + entry.charge, 0)
  const outstanding = SAMPLE_BATCHES.filter((batch) => batch.status !== 'VOID').reduce((sum, batch) => sum + (batch.total - batch.paid), 0)
  return (
    <section className="space-y-5">
      <PageHeader
        title="Billing"
        subtitle="Prepare client billing batches and record payments"
        actions={
          <button type="button" className="btn btn-primary" disabled>
            Prepare batch
          </button>
        }
      />
      <PreviewBanner sprint="Sprint 5" />
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
        <StatCard label="Ready to bill" value={formatPeso(unbilledTotal)} icon="invoice" tone="primary" hint={`${SAMPLE_UNBILLED_TRIPS.length} trips`} />
        <StatCard label="Outstanding from clients" value={formatPeso(outstanding)} icon="wallet" tone="warning" />
        <StatCard label="Carried forward" value={SAMPLE_UNBILLED_TRIPS.filter((entry) => entry.carried).length} icon="clock" tone="info" hint="From earlier periods" />
      </div>
      <FilterTabs tabs={TABS} activeKey={tabKey} onChange={setTabKey} label="Billing view" />

      {tabKey === 'unbilled' ? (
        <ul className="list card card-border bg-base-100">
          {SAMPLE_UNBILLED_TRIPS.map((trip) => (
            <li key={trip.id} className="list-row items-center">
              <div className="flex h-11 w-12 flex-col items-center justify-center rounded-box bg-base-200 text-xs font-bold text-primary">{trip.date}</div>
              <div>
                <p className="font-semibold">{trip.trip}</p>
                {trip.carried ? <span className="badge badge-warning badge-soft badge-sm">Carried forward</span> : <span className="text-xs text-base-content/60">Ready for this batch</span>}
              </div>
              <span className="font-semibold tabular-nums">{formatPeso(trip.charge)}</span>
            </li>
          ))}
        </ul>
      ) : (
        <div className="card card-border overflow-x-auto bg-base-100">
          <table className="table">
            <thead>
              <tr>
                <th>Batch</th>
                <th className="text-right">Trips</th>
                <th className="text-right">Total</th>
                <th className="text-right">Paid</th>
                <th>Invoice</th>
              </tr>
            </thead>
            <tbody>
              {SAMPLE_BATCHES.map((batch) => (
                <tr key={batch.id}>
                  <td className="font-mono text-sm">{batch.id}</td>
                  <td className="text-right tabular-nums">{batch.trips}</td>
                  <td className="text-right tabular-nums">{formatPeso(batch.total)}</td>
                  <td className="text-right tabular-nums">{formatPeso(batch.paid)}</td>
                  <td><StatusBadge kind="invoice" status={batch.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
