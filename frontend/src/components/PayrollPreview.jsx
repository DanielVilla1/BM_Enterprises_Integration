// ===== AI GENERATED: PayrollPreview =====
// Purpose: Design mockup of payroll: crew earnings, deductions, net pay and a personal statement
// Inputs: whether the viewer sees only their own statement (props only)
// Returns: page markup with disabled actions
// Flow:
// 1. HR view: period summary, per-trip earnings and the percentage example from the specification
// 2. Crew view: a personal statement (gross, deductions, advance repayment, net)

import {
  SAMPLE_CALCULATION,
  SAMPLE_EARNINGS,
  SAMPLE_PAYROLL_PERIOD,
  SAMPLE_STATEMENT,
} from '../shared/mockups/sampleData'
import { formatPeso } from '../shared/utils/formatting'
import { PageHeader } from './PageHeader'
import { PreviewBanner } from './PreviewBanner'
import { StatCard } from './StatCard'
import { StatusBadge } from './StatusBadge'

/**
 * @function ShareRow
 * @description One line of the percentage explanation.
 * @param {{role: string, percent: number, amount: number}} componentProps
 * @returns {import('react').ReactElement}
 */
function ShareRow({ role, percent, amount }) {
  return (
    <li className="flex items-center justify-between text-sm">
      <span>
        {role} <span className="text-base-content/60">· {percent}%</span>
      </span>
      <span className="font-semibold tabular-nums">{formatPeso(amount)}</span>
    </li>
  )
}

/**
 * @function PayrollPreview
 * @description Pure UI mockup for payroll.
 * @param {{isOwnView: boolean}} componentProps
 * @returns {import('react').ReactElement}
 */
export function PayrollPreview({ isOwnView }) {
  if (isOwnView) {
    const statement = SAMPLE_STATEMENT
    return (
      <section className="mx-auto max-w-2xl space-y-5">
        <PageHeader title="My earnings" subtitle={`Payroll statement · ${statement.period}`} />
        <PreviewBanner sprint="Sprint 5" />
        <div className="card card-border bg-base-100">
          <div className="card-body gap-4">
            <ul className="divide-y divide-base-300">
              {statement.trips.map((tripLine) => (
                <li key={tripLine.id} className="flex items-center justify-between py-2 text-sm">
                  <span>{tripLine.trip} <span className="text-base-content/60">· {tripLine.percent}%</span></span>
                  <span className="tabular-nums">{formatPeso(tripLine.amount)}</span>
                </li>
              ))}
            </ul>
            <dl className="space-y-2 border-t border-base-300 pt-3 text-sm">
              <div className="flex justify-between"><dt>Gross earnings</dt><dd className="tabular-nums">{formatPeso(statement.gross)}</dd></div>
              <div className="flex justify-between text-error"><dt>Deduction · {statement.deductionNote}</dt><dd className="tabular-nums">−{formatPeso(statement.deduction)}</dd></div>
              <div className="flex justify-between text-error"><dt>Cash advance repayment</dt><dd className="tabular-nums">−{formatPeso(statement.repayment)}</dd></div>
              <div className="flex justify-between border-t border-base-300 pt-3 text-lg font-bold"><dt>Net pay</dt><dd className="tabular-nums text-primary">{formatPeso(statement.net)}</dd></div>
            </dl>
            <p className="text-xs text-base-content/60">Remaining advance balance: {formatPeso(statement.remainingAdvance)}</p>
          </div>
        </div>
      </section>
    )
  }
  const gross = SAMPLE_EARNINGS.reduce((sum, row) => sum + row.amount, 0)
  return (
    <section className="space-y-5">
      <PageHeader
        title="Payroll"
        subtitle={SAMPLE_PAYROLL_PERIOD.label}
        actions={
          <>
            <StatusBadge kind="payroll" status={SAMPLE_PAYROLL_PERIOD.status} />
            <button type="button" className="btn btn-primary" disabled>
              Finalize period
            </button>
          </>
        }
      />
      <PreviewBanner sprint="Sprint 5" />
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Gross earnings" value={formatPeso(gross)} icon="wallet" tone="primary" />
        <StatCard label="Deductions" value={formatPeso(300)} icon="receipt" tone="error" />
        <StatCard label="Advance repayments" value={formatPeso(1000)} icon="cash" tone="warning" />
        <StatCard label="Net to pay" value={formatPeso(gross - 1300)} icon="check" tone="success" />
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <div className="card card-border overflow-x-auto bg-base-100 lg:col-span-2">
          <table className="table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Trip</th>
                <th className="text-right">Share</th>
                <th className="text-right">Earning</th>
              </tr>
            </thead>
            <tbody>
              {SAMPLE_EARNINGS.map((row) => (
                <tr key={row.id}>
                  <td>
                    <p className="font-medium">{row.employee}</p>
                    <p className="text-xs text-base-content/60">{row.role}</p>
                  </td>
                  <td>{row.trip}</td>
                  <td className="text-right tabular-nums">{row.percent}%</td>
                  <td className="text-right font-semibold tabular-nums">{formatPeso(row.amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card card-border bg-base-100">
          <div className="card-body gap-3">
            <h2 className="font-semibold">How a trip is shared</h2>
            <p className="text-sm text-base-content/70">
              Charge {formatPeso(SAMPLE_CALCULATION.charge)} − approved expenses {formatPeso(SAMPLE_CALCULATION.expenses)} = earnings base{' '}
              <strong>{formatPeso(SAMPLE_CALCULATION.base)}</strong>
            </p>
            <div>
              <p className="mb-1 text-xs font-bold uppercase tracking-wide text-primary">Driver + 1 helper (12%)</p>
              <ul className="space-y-1">{SAMPLE_CALCULATION.oneHelper.map((share) => <ShareRow key={share.role} {...share} />)}</ul>
            </div>
            <div>
              <p className="mb-1 text-xs font-bold uppercase tracking-wide text-primary">Driver + 2 helpers (12%)</p>
              <ul className="space-y-1">{SAMPLE_CALCULATION.twoHelpers.map((share) => <ShareRow key={share.role} {...share} />)}</ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
