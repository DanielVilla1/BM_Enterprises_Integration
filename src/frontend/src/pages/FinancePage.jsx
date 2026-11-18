// ===== AI GENERATED: FinancePage =====
// Purpose: Connect real finance/report screens to their account-scoped domain hooks.
// Inputs: Verified account and selected section.
// Returns: Loaded workspace with errors, actions and bounded paging.
// Flow: Derive UI hints centrally; render domain panel; keep all network access in hooks/services.

import { AdvancesPanel } from '../components/finance/AdvancesPanel'
import { BillingPanel } from '../components/finance/BillingPanel'
import { ExpensesPanel } from '../components/finance/ExpensesPanel'
import { PayrollPanel } from '../components/finance/PayrollPanel'
import { ReportsPanel } from '../components/reports/ReportsPanel'
import { useFinanceWorkspace } from '../hooks/useFinanceWorkspace'
import { ErrorNotice } from '../shared/components/ErrorNotice'
import { PageHeader } from '../shared/components/PageHeader'
import { financePermissions } from '../shared/utils/finance'

const PANELS = {
  expenses: ExpensesPanel,
  payroll: PayrollPanel,
  advances: AdvancesPanel,
  billing: BillingPanel,
  reports: ReportsPanel,
}
const TITLES = {
  expenses: 'Trip expenses',
  payroll: 'Payroll',
  advances: 'Cash advances',
  billing: 'Client billing',
  reports: 'Reports',
}

/** @param {{section:string,account:Object}} props @returns {import('react').ReactElement} */
export function FinancePage({ section, account }) {
  const state = useFinanceWorkspace(section, account.employee_id)
  const Panel = PANELS[section]
  return (
    <section className="space-y-5">
      <PageHeader
        title={TITLES[section]}
        subtitle="BM Enterprises · persistent business records"
        actions={
          <button className="btn btn-sm" disabled={state.isBusy} onClick={state.refresh}>
            Refresh
          </button>
        }
      />
      {state.snapshot?.presentation_data ? (
        <p role="status" className="alert alert-warning text-sm">
          Presentation data is loaded. DEMO records and amounts are fictional and must not be used
          for real payroll or invoices.
        </p>
      ) : null}
      <ErrorNotice failure={state.failure} />
      <ErrorNotice failure={state.actionFailure} />
      {state.notice ? (
        <p className="alert alert-info text-sm" role="status">
          {state.notice}
        </p>
      ) : null}
      {state.loadState === 'loading' ? (
        <p role="status" className="text-sm text-base-content/60">
          Loading records…
        </p>
      ) : null}
      {state.snapshot ? (
        <Panel
          snapshot={state.snapshot}
          employeeId={account.employee_id}
          permissions={financePermissions(account.capabilities)}
          busy={state.isBusy}
          onCommand={state.runCommand}
        />
      ) : null}
      <div className="flex items-center justify-between gap-3">
        <button
          className="btn btn-sm"
          disabled={state.offset === 0 || state.isBusy}
          onClick={state.previousPage}
        >
          Previous
        </button>
        <span className="text-sm">Page {Math.floor(state.offset / 50) + 1}</span>
        <button
          className="btn btn-sm"
          disabled={!state.snapshot?.has_more || state.isBusy}
          onClick={state.nextPage}
        >
          Next
        </button>
      </div>
    </section>
  )
}
