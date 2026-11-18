// ===== AI GENERATED: PayrollPanel =====
// Purpose: Persistent earnings, payroll drafts, statements and actual payment records.
// Inputs: Authorized payroll DTOs and capability hints.
// Returns: Pure financial UI; all totals and repayment decisions come from the API.
// Flow: Prepare, inspect itemized statements, finalize, then record real disbursements.

import { FinanceForm, FinanceId, FinanceTable } from './FinanceWidgets'
import { StatusBadge } from '../../shared/components/StatusBadge'
import { formatDate, formatPeso } from '../../shared/utils/formatting'
import { financialPerson, financialToday, independentReviewer } from '../../shared/utils/finance'

/** @param {{snapshot:Object,permissions:Object,employeeId:string,busy:boolean,onCommand:Function}} props @returns {import('react').ReactElement} */
export function PayrollPanel({ snapshot, permissions, employeeId, busy, onCommand }) {
  const { payrolls, statements, earnings, adjustments, people, trips } = snapshot
  const personOptions = people.map((person) => ({ value: person.record_id, label: person.name }))
  return (
    <div className="space-y-5">
      <p className="text-sm text-base-content/70">
        Periods run 1–15 and 16–month-end, Manila time. Draft repayments do not change advance
        balances. Late earnings carry forward with their original trip date.
      </p>
      {!snapshot.deductions_enabled ? (
        <div className="alert alert-info text-sm">
          Personal deductions are disabled pending the documented D16 review. Approved positive
          adjustments and agreed advance repayments have separate controls.
        </div>
      ) : null}
      <div className="grid gap-3 lg:grid-cols-2">
        {permissions.calculate ? (
          <FinanceForm
            title="Calculate ready trip earnings"
            busy={busy}
            fields={[
              {
                name: 'trip_id',
                label: 'Trip',
                options: trips.map((trip) => ({
                  value: trip.trip_id,
                  label: `${trip.trip_id.slice(0, 8)} · ${trip.status} · ${trip.earnings_state}`,
                })),
              },
            ]}
            onSubmit={({ trip_id }) => onCommand(`/earnings/${trip_id}/calculate`)}
          />
        ) : null}
        {permissions.prepare ? (
          <FinanceForm
            title="Prepare payroll period"
            busy={busy}
            fields={[{ name: 'start_on', label: 'Period start (1st or 16th)', type: 'date' }]}
            onSubmit={(payload) => onCommand('/payrolls', payload)}
          />
        ) : null}
        {permissions.creditAdjustment || (permissions.adjust && snapshot.deductions_enabled) ? (
          <FinanceForm
            title="Propose employee adjustment"
            busy={busy}
            fields={[
              { name: 'employee_id', label: 'Employee', options: personOptions },
              { name: 'amount', label: 'Amount (PHP)', money: true },
              {
                name: 'kind',
                label: 'Type',
                options: [
                  ...(permissions.creditAdjustment
                    ? [{ value: 'CREDIT', label: 'Positive earnings adjustment' }]
                    : []),
                  ...(snapshot.deductions_enabled
                    ? [
                        { value: 'VOLUNTARY', label: 'Authorized voluntary deduction' },
                        { value: 'OVERPAYMENT', label: 'Documented payroll overpayment recovery' },
                        { value: 'DEBIT', label: 'Reviewed debit adjustment' },
                      ]
                    : []),
                ],
              },
              { name: 'period_start', label: 'Period start', type: 'date' },
              { name: 'reason', label: 'Reason / source trip' },
              { name: 'authorization', label: 'Written basis / authorization reference' },
            ]}
            onSubmit={(payload) => onCommand('/adjustments', payload)}
          />
        ) : null}
      </div>
      <FinanceTable
        columns={['Employee', 'Trip / original date', 'Rate', 'Base', 'Gross', 'State']}
        empty={!earnings.length}
      >
        {earnings.map((earning) => (
          <tr key={earning.record_id}>
            <td>{financialPerson(people, earning.employee_id)}</td>
            <td>
              <FinanceId identifier={earning.trip_id} />
              <br />
              {formatDate(earning.original_date)}
            </td>
            <td>{earning.percentage}%</td>
            <td>{formatPeso(earning.base)}</td>
            <td>{formatPeso(earning.amount)}</td>
            <td>{earning.state}</td>
          </tr>
        ))}
      </FinanceTable>
      {adjustments.length ? (
        <FinanceTable columns={['Employee', 'Proposal', 'Amount', 'State', 'Review']} empty={false}>
          {adjustments.map((adjustment) => (
            <tr key={adjustment.record_id}>
              <td>{financialPerson(people, adjustment.employee_id)}</td>
              <td>
                {adjustment.kind}: {adjustment.reason}
              </td>
              <td>{formatPeso(adjustment.amount)}</td>
              <td>{adjustment.state}</td>
              <td>
                {permissions.approveAdjustment &&
                adjustment.state === 'PENDING' &&
                independentReviewer(employeeId, [adjustment.entered_by, adjustment.employee_id]) ? (
                  <button
                    className="btn btn-sm"
                    disabled={busy}
                    onClick={() => onCommand(`/adjustments/${adjustment.record_id}/approve`)}
                  >
                    Approve proposal
                  </button>
                ) : null}
              </td>
            </tr>
          ))}
        </FinanceTable>
      ) : null}
      <FinanceTable columns={['Payroll period', 'State', 'Actions']} empty={!payrolls.length}>
        {payrolls.map((payroll) => (
          <tr key={payroll.record_id}>
            <td>
              {formatDate(payroll.start_on)} – {formatDate(payroll.end_on)}
            </td>
            <td>
              <StatusBadge kind="payroll" status={payroll.state} />
            </td>
            <td>
              {permissions.prepare && payroll.state === 'DRAFT' ? (
                <button
                  className="btn btn-sm btn-primary"
                  disabled={busy}
                  onClick={() => onCommand(`/payrolls/${payroll.record_id}/finalize`)}
                >
                  Finalize reviewed payroll
                </button>
              ) : null}
              {permissions.reverse && payroll.state === 'FINALIZED' ? (
                <FinanceForm
                  title="Reverse unpaid payroll"
                  busy={busy}
                  fields={[{ name: 'reason', label: 'Independent reversal reason' }]}
                  onSubmit={(payload) =>
                    onCommand(`/payrolls/${payroll.record_id}/reverse`, payload)
                  }
                />
              ) : null}
            </td>
          </tr>
        ))}
      </FinanceTable>
      <div className="grid gap-4 lg:grid-cols-2">
        {statements.map((statement) => (
          <article
            className="card border border-base-300 bg-base-100 p-5"
            key={statement.record_id}
          >
            <h2 className="font-semibold">
              {financialPerson(people, statement.employee_id)} ·{' '}
              <FinanceId identifier={statement.payroll_id} />
            </h2>
            {statement.held ? (
              <p className="text-error">Financial hold — payment is blocked.</p>
            ) : null}
            <dl className="my-3 grid grid-cols-2 gap-1 text-sm">
              <dt>Gross</dt>
              <dd>{formatPeso(statement.gross)}</dd>
              <dt>Approved deductions</dt>
              <dd>{formatPeso(statement.deductions)}</dd>
              <dt>Advance repayments</dt>
              <dd>{formatPeso(statement.repayments)}</dd>
              <dt className="font-bold">Net pay</dt>
              <dd className="font-bold">{formatPeso(statement.net)}</dd>
              <dt>Paid / unpaid</dt>
              <dd>
                {formatPeso(statement.paid)} / {formatPeso(statement.unpaid)}
              </dd>
              <dt>Personal advance balance</dt>
              <dd>{formatPeso(statement.remaining_advance)}</dd>
            </dl>
            <details className="mb-3 text-sm">
              <summary className="cursor-pointer">Statement lines</summary>
              <ul className="mt-2 space-y-1">
                {statement.lines.map((line, index) => (
                  <li key={index}>
                    {line.kind} ·{' '}
                    {line.trip_id
                      ? `${line.trip_id.slice(0, 8)} · ${line.original_date} · ${line.percentage}%`
                      : (line.reason ?? '')}{' '}
                    · {formatPeso(line.amount)}
                    {line.carry_forward === 'True' ? ' · Carry-forward' : ''}
                  </li>
                ))}
              </ul>
            </details>
            {permissions.pay &&
            !statement.held &&
            payrolls.find((payroll) => payroll.record_id === statement.payroll_id)?.state ===
              'FINALIZED' ? (
              <FinanceForm
                title="Record actual payroll payment"
                busy={busy}
                fields={[
                  { name: 'amount', label: 'Actual amount (PHP)', money: true },
                  { name: 'paid_on', label: 'Payment date', type: 'date', value: financialToday() },
                  { name: 'method', label: 'Payment method' },
                  { name: 'reference', label: 'Actual payment reference' },
                ]}
                onSubmit={(payload) =>
                  onCommand(`/statements/${statement.record_id}/payments`, payload)
                }
              />
            ) : null}
          </article>
        ))}
      </div>
    </div>
  )
}
