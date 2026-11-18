// ===== AI GENERATED: ReportsPanel =====
// Purpose: Persistent operational exceptions and authorized financial summaries.
// Inputs: Server-scoped report DTOs; no sample records.
// Returns: Responsive totals and actionable exception list.
// Flow: Identify OR/receipt gaps and financial holds without conflating completion and payment.

import { FinanceId, FinanceTable } from '../finance/FinanceWidgets'
import { StatusBadge } from '../../shared/components/StatusBadge'
import { formatDate, formatPeso } from '../../shared/utils/formatting'
import { humanizeCode } from '../../shared/utils/statusLabels'
import { financialPerson } from '../../shared/utils/finance'

/** @param {{snapshot:Object}} props @returns {import('react').ReactElement} */
export function ReportsPanel({ snapshot }) {
  return (
    <div className="space-y-5">
      <p className="text-sm text-base-content/70">
        Operational counts cover the current page. Financial totals cover the records your account
        may view. Crew members see only assigned trips and their own earnings.
      </p>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {Object.entries(snapshot.totals).map(([name, total]) => (
          <article key={name} className="stat rounded-box border border-base-300 bg-base-100">
            <div className="stat-title whitespace-normal">{humanizeCode(name)}</div>
            <div className="stat-value text-2xl">{total}</div>
          </article>
        ))}
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {Object.entries(snapshot.financial_totals).map(([name, total]) => (
          <article key={name} className="stat rounded-box border border-base-300 bg-base-100">
            <div className="stat-title whitespace-normal">{humanizeCode(name.toUpperCase())}</div>
            <div className="stat-value text-xl">{formatPeso(total)}</div>
          </article>
        ))}
      </div>
      <FinanceTable
        columns={['Trip', 'Scheduled', 'Status', 'Exceptions']}
        empty={!snapshot.trips.length}
      >
        {snapshot.trips.map((trip) => (
          <tr key={trip.trip_id}>
            <td>
              <FinanceId identifier={trip.trip_id} />
            </td>
            <td>{formatDate(trip.scheduled_date)}</td>
            <td>
              <StatusBadge kind="trip" status={trip.status} />
            </td>
            <td>
              {trip.flags.length ? (
                <ul>
                  {trip.flags.map((flag) => (
                    <li className="text-warning" key={flag}>
                      {humanizeCode(flag)}
                    </li>
                  ))}
                </ul>
              ) : (
                'No flagged exceptions'
              )}
            </td>
          </tr>
        ))}
      </FinanceTable>
      {snapshot.statements?.length ? (
        <div className="space-y-2">
          <h2 className="text-lg font-semibold">Employee pay and unpaid balances</h2>
          <FinanceTable
            columns={['Employee', 'Gross', 'Deductions', 'Repayments', 'Net', 'Unpaid']}
            empty={false}
          >
            {snapshot.statements.map((statement) => (
              <tr key={statement.record_id}>
                <td>{financialPerson(snapshot.people ?? [], statement.employee_id)}</td>
                <td>{formatPeso(statement.gross)}</td>
                <td>{formatPeso(statement.deductions)}</td>
                <td>{formatPeso(statement.repayments)}</td>
                <td>{formatPeso(statement.net)}</td>
                <td>
                  {formatPeso(statement.unpaid)}
                  {statement.held ? ' · Held' : ''}
                </td>
              </tr>
            ))}
          </FinanceTable>
        </div>
      ) : null}
      {snapshot.advances?.length ? (
        <div className="space-y-2">
          <h2 className="text-lg font-semibold">Personal and operating advances</h2>
          <FinanceTable
            columns={['Employee', 'Type', 'State', 'Released', 'Balance']}
            empty={false}
          >
            {snapshot.advances.map((advance) => (
              <tr key={advance.record_id}>
                <td>{financialPerson(snapshot.people ?? [], advance.employee_id)}</td>
                <td>{advance.kind}</td>
                <td>{humanizeCode(advance.state)}</td>
                <td>{formatPeso(advance.released)}</td>
                <td>{formatPeso(advance.balance)}</td>
              </tr>
            ))}
          </FinanceTable>
        </div>
      ) : null}
      {snapshot.invoices?.length ? (
        <div className="space-y-2">
          <h2 className="text-lg font-semibold">Billing batches and client balances</h2>
          <FinanceTable
            columns={['Invoice', 'State', 'Cutoff', 'Total', 'Outstanding']}
            empty={false}
          >
            {snapshot.invoices.map((invoice) => (
              <tr key={invoice.record_id}>
                <td>
                  <FinanceId identifier={invoice.record_id} />
                </td>
                <td>{humanizeCode(invoice.state)}</td>
                <td>{formatDate(invoice.cutoff)}</td>
                <td>{formatPeso(invoice.total)}</td>
                <td>{formatPeso(invoice.outstanding)}</td>
              </tr>
            ))}
          </FinanceTable>
        </div>
      ) : null}
      {snapshot.fleet?.length ? (
        <div className="space-y-2">
          <h2 className="text-lg font-semibold">Fleet and maintenance</h2>
          <FinanceTable columns={['Truck', 'Current status', 'Maintenance history']} empty={false}>
            {snapshot.fleet.map((truck) => (
              <tr key={truck.truck_id}>
                <td>{truck.plate_number}</td>
                <td>{humanizeCode(truck.status)}</td>
                <td>
                  {truck.maintenance.length ? (
                    <ul>
                      {truck.maintenance.map((entry) => (
                        <li key={entry.record_id}>
                          {entry.reason} · {entry.ended_at ? 'Closed' : 'Open'}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    'No maintenance recorded'
                  )}
                </td>
              </tr>
            ))}
          </FinanceTable>
        </div>
      ) : null}
      {snapshot.replacements?.length ? (
        <div className="space-y-2">
          <h2 className="text-lg font-semibold">Truck replacement history</h2>
          <FinanceTable
            columns={['Trip', 'Original truck', 'Replacement truck', 'Reason']}
            empty={false}
          >
            {snapshot.replacements.map((entry) => (
              <tr key={entry.replacement_id}>
                <td>
                  <FinanceId identifier={entry.trip_id} />
                </td>
                <td>
                  <FinanceId identifier={entry.original_truck_id} />
                </td>
                <td>
                  <FinanceId identifier={entry.replacement_truck_id} />
                </td>
                <td>{entry.reason}</td>
              </tr>
            ))}
          </FinanceTable>
        </div>
      ) : null}
    </div>
  )
}
