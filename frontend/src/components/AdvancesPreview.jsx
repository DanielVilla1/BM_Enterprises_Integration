// ===== AI GENERATED: AdvancesPreview =====
// Purpose: Design mockup of personal cash advances: request, approval, release and repayment
// Inputs: none (sample data only)
// Returns: page markup with disabled actions
// Flow:
// 1. Only released money counts toward a balance; approval alone creates no debt
// 2. Trip operating advances are a different thing, explained in a note

import { SAMPLE_ADVANCES } from '../shared/mockups/sampleData'
import { formatPeso } from '../shared/utils/formatting'
import { Icon } from './Icon'
import { PageHeader } from './PageHeader'
import { PreviewBanner } from './PreviewBanner'
import { StatCard } from './StatCard'
import { StatusBadge } from './StatusBadge'

/**
 * @function AdvancesPreview
 * @description Pure UI mockup for cash advances.
 * @returns {import('react').ReactElement}
 */
export function AdvancesPreview() {
  const outstanding = SAMPLE_ADVANCES.reduce((sum, entry) => sum + entry.balance, 0)
  return (
    <section className="space-y-5">
      <PageHeader
        title="Cash advances"
        subtitle="Personal advances to drivers and helpers"
        actions={
          <button type="button" className="btn btn-primary" disabled>
            Request advance
          </button>
        }
      />
      <PreviewBanner sprint="Sprint 5" />
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-3">
        <StatCard label="Outstanding balance" value={formatPeso(outstanding)} icon="cash" tone="warning" hint="Released, not yet repaid" />
        <StatCard label="Awaiting approval" value={SAMPLE_ADVANCES.filter((entry) => entry.status === 'REQUESTED').length} icon="clock" tone="info" />
        <StatCard label="Repaying" value={SAMPLE_ADVANCES.filter((entry) => entry.status === 'REPAYING').length} icon="wallet" tone="primary" />
      </div>
      <ul className="list card card-border bg-base-100">
        {SAMPLE_ADVANCES.map((advance) => (
          <li key={advance.id} className="list-row items-center">
            <div className="flex h-11 w-11 items-center justify-center rounded-box bg-base-200 text-primary">
              <Icon name="cash" />
            </div>
            <div>
              <p className="font-semibold">{advance.employee}</p>
              <p className="text-sm text-base-content/70">{advance.note}</p>
            </div>
            <div className="text-right">
              <p className="font-semibold tabular-nums">{formatPeso(advance.amount)}</p>
              <p className="text-xs text-base-content/60">Balance {formatPeso(advance.balance)}</p>
            </div>
            <StatusBadge kind="advance" status={advance.status} />
          </li>
        ))}
      </ul>
      <div role="note" className="alert alert-info alert-soft text-sm">
        <Icon name="info" className="h-5 w-5" />
        <span>Money given for fuel or tolls on a trip is a separate trip operating advance. It is reconciled against real expenses and never becomes personal debt automatically.</span>
      </div>
    </section>
  )
}
