// ===== AI GENERATED: ExpensesPanel =====
// Purpose: Real trip expenses, independent review, final charges and rate versions.
// Inputs: Authorized workspace DTOs, permission hints and command callbacks.
// Returns: Presentational financial forms and persistent record tables.
// Flow: Show readiness, submit explicit declarations and expose independent review actions.

import { FinanceForm, FinanceId, FinanceTable } from './FinanceWidgets'
import { StatusBadge } from '../../shared/components/StatusBadge'
import { formatPeso } from '../../shared/utils/formatting'
import { expenseLinePayload, financialToday, independentReviewer } from '../../shared/utils/finance'

/** @param {{snapshot:Object,permissions:Object,employeeId:string,busy:boolean,onCommand:Function}} props @returns {import('react').ReactElement} */
export function ExpensesPanel({ snapshot, permissions, employeeId, busy, onCommand }) {
  const { trips, expenses, charges, rates } = snapshot
  const tripOptions = trips.map((trip) => ({
    value: trip.trip_id,
    label: `${trip.trip_id.slice(0, 8)} · ${trip.scheduled_date} · ${trip.expense_state}`,
  }))
  return (
    <div className="space-y-5">
      <p className="text-sm text-base-content/70">
        Missing expenses keep earnings pending. A zero declaration also requires a different
        reviewer. Hauling rates are visible only with commercial access.
      </p>
      {permissions.enter ? (
        <div className="grid gap-3 lg:grid-cols-2">
          <FinanceForm
            title="Add an expense line"
            busy={busy}
            fields={[
              { name: 'trip_id', label: 'Trip', options: tripOptions },
              {
                name: 'category',
                label: 'Category',
                options: [
                  { value: 'FUEL', label: 'Fuel' },
                  { value: 'TOLL', label: 'Toll' },
                ],
              },
              { name: 'amount', label: 'Actual amount (PHP)', money: true },
              { name: 'description', label: 'Purchase description' },
              {
                name: 'incurred_on',
                label: 'Purchase date',
                type: 'date',
                value: financialToday(),
              },
              { name: 'evidence', label: 'Receipt or evidence reference' },
              { name: 'reason', label: 'Entry reference / reason' },
            ]}
            onSubmit={(fields) =>
              onCommand(`/expenses/${fields.trip_id}`, expenseLinePayload(fields, expenses))
            }
          />
          <FinanceForm
            title="Declare zero expenses"
            busy={busy}
            fields={[
              { name: 'trip_id', label: 'Trip', options: tripOptions },
              { name: 'reason', label: 'Why were there no trip expenses?' },
            ]}
            onSubmit={({ trip_id, reason }) =>
              onCommand(`/expenses/${trip_id}`, { declared_zero: true, lines: [], reason })
            }
          />
        </div>
      ) : null}
      <FinanceTable
        columns={['Trip', 'Review state', 'Expense lines', 'Total', 'Actions']}
        empty={!expenses.length}
      >
        {expenses.map((sheet) => (
          <tr key={sheet.record_id}>
            <td>
              <FinanceId identifier={sheet.trip_id} />
            </td>
            <td>
              <StatusBadge kind="expense" status={sheet.state} />
            </td>
            <td>
              {sheet.declared_zero ? (
                'Explicit zero declaration'
              ) : (
                <ul>
                  {sheet.lines.map((line, index) => (
                    <li key={`${line.evidence}-${index}`}>
                      {line.category}: {line.description} · {line.evidence} ·{' '}
                      {formatPeso(line.amount)}
                    </li>
                  ))}
                </ul>
              )}
              <p className="text-xs opacity-60">{sheet.reason}</p>
            </td>
            <td>{formatPeso(sheet.total)}</td>
            <td className="min-w-52">
              {permissions.enter && sheet.state === 'ENTERING' ? (
                <button
                  className="btn btn-sm btn-primary"
                  disabled={busy}
                  onClick={() => onCommand(`/expenses/${sheet.trip_id}/submit`)}
                >
                  Submit for review
                </button>
              ) : null}
              {permissions.review &&
              sheet.state === 'AWAITING_REVIEW' &&
              independentReviewer(employeeId, [sheet.entered_by, ...(sheet.contributors ?? [])]) ? (
                <FinanceForm
                  title="Review declaration"
                  busy={busy}
                  fields={[
                    {
                      name: 'approved',
                      label: 'Decision',
                      options: [
                        { value: 'true', label: 'Approve' },
                        { value: 'false', label: 'Return for changes' },
                      ],
                    },
                    { name: 'reason', label: 'Review reason' },
                  ]}
                  onSubmit={(fields) =>
                    onCommand(`/expenses/${sheet.trip_id}/review`, {
                      ...fields,
                      approved: fields.approved === 'true',
                    })
                  }
                />
              ) : null}
            </td>
          </tr>
        ))}
      </FinanceTable>
      <FinanceTable columns={['Trip', 'Operations', 'Expenses', 'Earnings']} empty={!trips.length}>
        {trips.map((trip) => (
          <tr key={trip.trip_id}>
            <td>
              <FinanceId identifier={trip.trip_id} />
            </td>
            <td>
              <StatusBadge kind="trip" status={trip.status} />
            </td>
            <td>{trip.expense_state}</td>
            <td>{trip.earnings_state}</td>
          </tr>
        ))}
      </FinanceTable>
      {permissions.charge ? (
        <FinanceForm
          title="Finalize agreed hauling charge"
          busy={busy}
          fields={[
            { name: 'trip_id', label: 'Trip', options: tripOptions },
            { name: 'amount', label: 'Final charge (PHP)', money: true },
            { name: 'agreed_amount', label: 'Agreed reference amount (PHP)', money: true },
            { name: 'reference', label: 'Agreement / quotation reference' },
            { name: 'reason', label: 'Reason (explain any variance)' },
          ]}
          onSubmit={({ trip_id, ...payload }) => onCommand(`/charges/${trip_id}`, payload)}
        />
      ) : null}
      {charges.length ? (
        <FinanceTable columns={['Trip', 'Charge', 'State', 'Reference', 'Review']} empty={false}>
          {charges.map((charge) => (
            <tr key={charge.record_id}>
              <td>
                <FinanceId identifier={charge.trip_id} />
              </td>
              <td>{charge.charge ? formatPeso(charge.charge) : 'Missing'}</td>
              <td>{charge.held ? `Held: ${charge.hold_reason}` : charge.charge_state}</td>
              <td>{charge.reference}</td>
              <td>
                {permissions.rates &&
                charge.charge_state === 'AWAITING_REVIEW' &&
                independentReviewer(employeeId, [charge.entered_by]) ? (
                  <button
                    className="btn btn-sm"
                    disabled={busy}
                    onClick={() => onCommand(`/charges/${charge.trip_id}/approve-variance`)}
                  >
                    Approve variance
                  </button>
                ) : null}
                {permissions.rates && charge.held ? (
                  <FinanceForm
                    title="Release reviewed hold"
                    busy={busy}
                    fields={[{ name: 'reason', label: 'Independent review reference' }]}
                    onSubmit={(payload) => onCommand(`/holds/${charge.trip_id}/release`, payload)}
                  />
                ) : null}
              </td>
            </tr>
          ))}
        </FinanceTable>
      ) : null}
      {permissions.rates ? (
        <FinanceForm
          title="Schedule a future earnings-rate version"
          busy={busy}
          fields={[
            { name: 'effective_on', label: 'Future effective date (Manila)', type: 'date' },
            { name: 'driver_one', label: 'Driver with 1 helper (%)' },
            { name: 'helper_one', label: 'One helper (%)' },
            { name: 'driver_two', label: 'Driver with 2 helpers (%)' },
            { name: 'helper_two', label: 'Each of 2 helpers (%)' },
            { name: 'reference', label: 'Rate authorization reference' },
          ]}
          onSubmit={(payload) => onCommand('/rates', payload)}
        />
      ) : null}
      {rates.length ? (
        <p className="text-sm text-base-content/70">
          Rate versions:{' '}
          {rates
            .map(
              (rate) =>
                `${rate.effective_on}: ${rate.driver_one}/${rate.helper_one} or ${rate.driver_two}/${rate.helper_two}/${rate.helper_two}%`,
            )
            .join(' · ')}
          . Departed trips retain their snapshot.
        </p>
      ) : null}
    </div>
  )
}
