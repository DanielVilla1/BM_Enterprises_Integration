// ===== AI GENERATED: ReportsPreview =====
// Purpose: Design mockup of operational reports and the owner's spot-check list (Sprint 6)
// Inputs: none (sample data only)
// Returns: page markup
// Flow:
// 1. KPI cards, a weekly deliveries bar chart and truck utilization bars (plain CSS, no chart library)
// 2. Trips completed without a stamped copy, for periodic review (specification section 6)

import { SAMPLE_REPORTS } from '../shared/mockups/sampleData'
import { PageHeader } from './PageHeader'
import { PreviewBanner } from './PreviewBanner'
import { StatCard } from './StatCard'

/**
 * @function ReportsPreview
 * @description Pure UI mockup for reports.
 * @returns {import('react').ReactElement}
 */
export function ReportsPreview() {
  const maximum = Math.max(...SAMPLE_REPORTS.weekly.map((week) => week.value))
  return (
    <section className="space-y-5">
      <PageHeader title="Reports" subtitle="How the operation is doing this month" />
      <PreviewBanner sprint="Sprint 6" />
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {SAMPLE_REPORTS.kpis.map((kpi) => (
          <StatCard key={kpi.label} {...kpi} />
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card card-border bg-base-100">
          <div className="card-body gap-4">
            <h2 className="font-semibold">Deliveries per week</h2>
            <div className="flex h-44 items-end gap-4" role="img" aria-label={`Deliveries per week: ${SAMPLE_REPORTS.weekly.map((week) => `${week.label} ${week.value}`).join(', ')}`}>
              {SAMPLE_REPORTS.weekly.map((week) => (
                <div key={week.label} className="flex h-full flex-1 flex-col items-center justify-end gap-2">
                  <span className="text-sm font-semibold tabular-nums">{week.value}</span>
                  <div className="w-full rounded-t-box bg-primary" style={{ height: `${(week.value / maximum) * 100}%` }} />
                  <span className="text-xs text-base-content/60">{week.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="card card-border bg-base-100">
          <div className="card-body gap-4">
            <h2 className="font-semibold">Truck utilization</h2>
            {SAMPLE_REPORTS.utilization.map((truck) => (
              <div key={truck.plate} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="font-medium">{truck.plate}</span>
                  <span className="tabular-nums">{truck.percent}%</span>
                </div>
                <progress className="progress progress-secondary h-2 w-full" value={truck.percent} max="100" aria-label={`${truck.plate} utilization`} />
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card card-border bg-base-100">
        <div className="card-body gap-3">
          <h2 className="font-semibold">Completed without a stamped copy</h2>
          <p className="text-sm text-base-content/70">A driver's own confirmation completes a trip, so these are worth a quick owner or dispatcher check.</p>
          <ul className="divide-y divide-base-300">
            {SAMPLE_REPORTS.withoutStampedCopy.map((entry) => (
              <li key={entry.id} className="flex items-center justify-between py-2 text-sm">
                <span className="font-medium">{entry.trip}</span>
                <span className="text-base-content/60">{entry.driver}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
