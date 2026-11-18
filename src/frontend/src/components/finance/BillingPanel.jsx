// ===== AI GENERATED: BillingPanel =====
// Purpose: Real eligible-trip billing, independent invoice voids and collections.
// Inputs: Authorized billing workspace, permission hints and callbacks.
// Returns: Batch form and immutable invoice line/payment details.
// Flow: Select ready charges, issue a reviewed batch, record collections or request a void.

import { FinanceForm, FinanceId, FinanceTable } from './FinanceWidgets'
import { StatusBadge } from '../../shared/components/StatusBadge'
import { formatDate, formatPeso } from '../../shared/utils/formatting'
import { financialToday, independentReviewer } from '../../shared/utils/finance'

/** @param {{snapshot:Object,permissions:Object,employeeId:string,busy:boolean,onCommand:Function}} props @returns {import('react').ReactElement} */
export function BillingPanel({ snapshot, permissions, employeeId, busy, onCommand }) {
  const { trips, invoices, payments } = snapshot
  const clients = [
    ...new Map(
      trips.map((trip) => [
        trip.client_id,
        { value: trip.client_id, label: trip.client_name || trip.client_id.slice(0, 8) },
      ]),
    ).values(),
  ]
  return (
    <div className="space-y-5">
      <p className="text-sm text-base-content/70">
        Ready trips can carry over from earlier orders and periods. Signed OR and actual receipt are
        required; payroll, client payment and stamped copies are separate states.
      </p>
      {permissions.bill ? (
        <FinanceForm
          title="Build client billing batch"
          busy={busy}
          fields={[
            { name: 'client_id', label: 'Client', options: clients },
            {
              name: 'cutoff',
              label: 'Inclusive delivery cutoff (Manila)',
              type: 'date',
              value: financialToday(),
            },
            {
              name: 'trip_ids',
              label: 'Ready unbilled trips for that client',
              multiple: true,
              hint: 'Select one or more trips. Each batch belongs to one client.',
              options: trips
                .filter((trip) => trip.billing_state === 'READY')
                .map((trip) => ({
                  value: trip.trip_id,
                  label: `${trip.client_name || trip.client_id.slice(0, 8)} · ${trip.trip_id.slice(0, 8)} · ${formatPeso(trip.charge)}`,
                })),
            },
            {
              name: 'terms_days',
              label: 'Payment terms (calendar days)',
              type: 'number',
              value: '30',
              min: 0,
              max: 365,
            },
          ]}
          onSubmit={(payload) =>
            onCommand('/invoices', { ...payload, terms_days: Number(payload.terms_days) })
          }
        />
      ) : null}
      <FinanceTable
        columns={['Invoice / client', 'State', 'Total', 'Collected / due', 'Dates', 'Actions']}
        empty={!invoices.length}
      >
        {invoices.map((invoice) => (
          <tr key={invoice.record_id}>
            <td>
              <FinanceId identifier={invoice.record_id} />
              <p className="text-xs">
                Client <FinanceId identifier={invoice.client_id} />
              </p>
            </td>
            <td>
              <StatusBadge kind="invoice" status={invoice.state} />
              {invoice.held ? <p className="text-error">Financial hold</p> : null}
            </td>
            <td>{formatPeso(invoice.total)}</td>
            <td>
              {formatPeso(invoice.paid)} / {formatPeso(invoice.outstanding)}
              <p className="text-xs">
                Unallocated credit: {formatPeso(invoice.unallocated_credit)}
              </p>
            </td>
            <td>
              Cutoff: {formatDate(invoice.cutoff)}
              <br />
              Issued: {formatDate(invoice.issued_on)}
              <br />
              Due: {formatDate(invoice.due_on)}
            </td>
            <td className="min-w-64 space-y-2">
              {permissions.bill && invoice.state === 'DRAFT' && !invoice.held ? (
                <button
                  className="btn btn-sm btn-primary"
                  disabled={busy}
                  onClick={() => onCommand(`/invoices/${invoice.record_id}/issue`)}
                >
                  Issue reviewed invoice
                </button>
              ) : null}
              {permissions.bill && invoice.state === 'ISSUED' && !invoice.held ? (
                <FinanceForm
                  title="Record actual collection"
                  busy={busy}
                  fields={[
                    { name: 'amount', label: 'Amount received (PHP)', money: true },
                    {
                      name: 'paid_on',
                      label: 'Collection date',
                      type: 'date',
                      value: financialToday(),
                    },
                    { name: 'method', label: 'Payment method' },
                    { name: 'reference', label: 'Actual collection reference' },
                  ]}
                  onSubmit={(payload) =>
                    onCommand(`/invoices/${invoice.record_id}/payments`, payload)
                  }
                />
              ) : null}
              {permissions.bill && ['DRAFT', 'ISSUED'].includes(invoice.state) ? (
                <FinanceForm
                  title="Request independent void approval"
                  busy={busy}
                  fields={[{ name: 'reason', label: 'Void reason' }]}
                  onSubmit={(payload) =>
                    onCommand(`/invoices/${invoice.record_id}/request-void`, payload)
                  }
                />
              ) : null}
              {permissions.voidInvoice &&
              invoice.state === 'VOID_REQUESTED' &&
              independentReviewer(employeeId, [invoice.void_requested_by]) ? (
                <button
                  className="btn btn-sm btn-warning"
                  disabled={busy}
                  onClick={() => onCommand(`/invoices/${invoice.record_id}/approve-void`)}
                >
                  Approve unpaid invoice void
                </button>
              ) : null}
              <details className="text-xs">
                <summary className="cursor-pointer">Lines and collections</summary>
                <ul className="mt-2 space-y-1">
                  {invoice.lines.map((line) => (
                    <li key={line.record_id}>
                      Trip <FinanceId identifier={line.trip_id} /> · delivered {line.delivered_on} ·{' '}
                      {formatPeso(line.amount)} · {line.active ? 'Allocated' : 'Released'}
                    </li>
                  ))}
                  {payments
                    .filter((payment) => payment.invoice_id === invoice.record_id)
                    .map((payment) => (
                      <li key={payment.record_id}>
                        {payment.paid_on} · {payment.method} · {payment.reference} ·{' '}
                        {formatPeso(payment.amount)}
                      </li>
                    ))}
                </ul>
              </details>
            </td>
          </tr>
        ))}
      </FinanceTable>
    </div>
  )
}
