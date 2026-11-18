// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: ExpensesPreview =====
// Purpose: Design mockup of trip expense entry and review (backend arrives in Sprint 5)
// Inputs: none (sample data only)
// Returns: page markup with disabled actions
// Flow:
// 1. Four expense states from the specification, never silently treated as zero
// 2. The approver must differ from the person who entered the expense

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { useState } from 'react'
import { SAMPLE_EXPENSES } from '../../shared/mockups/sampleData'
import { formatPeso } from '../../shared/utils/formatting'
import { FilterTabs } from '../../shared/components/FilterTabs'
import { PageHeader } from '../../shared/components/PageHeader'
import { PreviewBanner } from '../../shared/components/PreviewBanner'
import { StatCard } from '../../shared/components/StatCard'
import { StatusBadge } from '../../shared/components/StatusBadge'

const TABS = [
  { key: 'all', label: 'All' },
  { key: 'AWAITING_REVIEW', label: 'Awaiting review' },
  { key: 'ENTERING', label: 'Being entered' },
  { key: 'FINALIZED', label: 'Finalized' },
]

/**
 * @function ExpensesPreview
 * @description Pure UI mockup for trip expenses.
 * @returns {import('react').ReactElement}
 */
export function ExpensesPreview() {
  const [tabKey, setTabKey] = useState('all')
  const rows = SAMPLE_EXPENSES.filter((expense) => tabKey === 'all' || expense.state === tabKey)
  const waiting = SAMPLE_EXPENSES.filter((expense) => expense.state === 'AWAITING_REVIEW')
  return (
    <section className="space-y-5">
      <PageHeader
        title="Trip expenses"
        subtitle="Fuel, tolls and other deductible costs per trip"
        actions={
          <button type="button" className="btn btn-primary" disabled>
            Add expense
          </button>
        }
      />
      <PreviewBanner sprint="Sprint 5" />
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard label="Awaiting review" value={waiting.length} icon="clock" tone="warning" />
        <StatCard
          label="Being entered"
          value={SAMPLE_EXPENSES.filter((entry) => entry.state === 'ENTERING').length}
          icon="pencil"
          tone="neutral"
        />
        <StatCard
          label="Finalized"
          value={SAMPLE_EXPENSES.filter((entry) => entry.state === 'FINALIZED').length}
          icon="check"
          tone="success"
        />
        <StatCard
          label="Awaiting amount"
          value={formatPeso(waiting.reduce((sum, entry) => sum + entry.amount, 0))}
          icon="receipt"
          tone="info"
        />
      </div>
      <FilterTabs tabs={TABS} activeKey={tabKey} onChange={setTabKey} label="Expense state" />
      <div className="card card-border overflow-x-auto bg-base-100">
        <table className="table">
          <thead>
            <tr>
              <th>Trip</th>
              <th>Category</th>
              <th className="text-right">Amount</th>
              <th>State</th>
              <th>Entered by</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((expense) => (
              <tr key={expense.id}>
                <td className="font-medium">{expense.trip}</td>
                <td>{expense.category}</td>
                <td className="text-right tabular-nums">{formatPeso(expense.amount)}</td>
                <td>
                  <StatusBadge kind="expense" status={expense.state} />
                </td>
                <td>{expense.enteredBy}</td>
                <td className="text-right">
                  {expense.state === 'AWAITING_REVIEW' ? (
                    <div
                      className="tooltip tooltip-left"
                      data-tip="Approver must differ from the person who entered it"
                    >
                      <button type="button" className="btn btn-outline btn-xs" disabled>
                        Approve
                      </button>
                    </div>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-base-content/60">
        Missing expenses are never treated as zero: a trip with no costs must be confirmed as “zero
        expenses”.
      </p>
    </section>
  )
}
