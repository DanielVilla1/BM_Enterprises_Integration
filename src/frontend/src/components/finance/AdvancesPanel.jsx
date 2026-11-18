// ===== AI GENERATED: AdvancesPanel =====
// Purpose: Real personal/operating advances, approvals, releases and funding reconciliation.
// Inputs: Authorized DTOs, permission hints and command callback.
// Returns: Pure forms and exact ledger balances from the API.
// Flow: Request; independently approve; record actual releases; inspect movements.

import { FinanceForm, FinanceId, FinanceTable } from './FinanceWidgets'
import { StatusBadge } from '../../shared/components/StatusBadge'
import { formatPeso } from '../../shared/utils/formatting'
import { financialPerson, financialToday, independentReviewer } from '../../shared/utils/finance'

/** @param {{snapshot:Object,permissions:Object,employeeId:string,busy:boolean,onCommand:Function}} props @returns {import('react').ReactElement} */
export function AdvancesPanel({ snapshot, permissions, employeeId, busy, onCommand }) {
  const { advances, people, trips, delegations } = snapshot
  const personOptions = people.map((person) => ({ value: person.record_id, label: person.name }))
  return (
    <div className="space-y-5">
      <p className="text-sm text-base-content/70">
        Approval creates no debt. Only released personal funds enter the repayment balance.
        Operating funds remain a separate trip ledger and never become personal debt automatically.
      </p>
      <div className="grid gap-3 lg:grid-cols-2">
        {permissions.request ? (
          <FinanceForm
            title="Request personal advance"
            busy={busy}
            fields={[
              { name: 'employee_id', label: 'Employee', options: personOptions, value: employeeId },
              { name: 'amount', label: 'Requested amount (PHP)', money: true },
              { name: 'reason', label: 'Reason' },
            ]}
            onSubmit={(payload) => onCommand('/advances', { ...payload, kind: 'PERSONAL' })}
          />
        ) : null}
        {permissions.release ? (
          <FinanceForm
            title="Request trip operating funds"
            busy={busy}
            fields={[
              { name: 'employee_id', label: 'Assigned crew custodian', options: personOptions },
              {
                name: 'trip_id',
                label: 'Trip',
                options: trips.map((trip) => ({
                  value: trip.trip_id,
                  label: `${trip.trip_id.slice(0, 8)} · ${trip.status}`,
                })),
              },
              { name: 'amount', label: 'Operating funds (PHP)', money: true },
              { name: 'reason', label: 'Funding purpose' },
            ]}
            onSubmit={(payload) => onCommand('/advances', { ...payload, kind: 'OPERATING' })}
          />
        ) : null}
        {permissions.delegate ? (
          <FinanceForm
            title="Delegate advance approval"
            busy={busy}
            fields={[
              { name: 'employee_id', label: 'Authorized HR approver', options: personOptions },
              { name: 'expires_on', label: 'Expiry date (Manila)', type: 'date' },
              { name: 'reason', label: 'Delegation reason' },
            ]}
            onSubmit={(payload) => onCommand('/advance-delegations', payload)}
          />
        ) : null}
      </div>
      <FinanceTable
        columns={['Employee / type', 'Request', 'Released', 'Balance', 'State', 'Workflow']}
        empty={!advances.length}
      >
        {advances.map((advance) => (
          <tr key={advance.record_id}>
            <td>
              {financialPerson(people, advance.employee_id)}
              <p className="text-xs">
                {advance.kind} · <FinanceId identifier={advance.record_id} />
              </p>
            </td>
            <td>
              {formatPeso(advance.amount)}
              <p className="text-xs opacity-60">{advance.reason}</p>
            </td>
            <td>{formatPeso(advance.released)}</td>
            <td>{formatPeso(advance.balance)}</td>
            <td>
              <StatusBadge kind="advance" status={advance.state} />
            </td>
            <td className="min-w-64 space-y-2">
              {permissions.approveAdvance &&
              advance.state === 'REQUESTED' &&
              independentReviewer(employeeId, [advance.employee_id, advance.requested_by]) ? (
                <FinanceForm
                  title="Approve arrangement"
                  busy={busy}
                  fields={[
                    {
                      name: 'amount',
                      label: 'Approved maximum (PHP)',
                      money: true,
                      value: advance.amount,
                    },
                    {
                      name: 'installment',
                      label: 'Agreed personal installment per period (PHP)',
                      money: true,
                      hint: 'For operating funds this value is unused; they are not payroll debt.',
                    },
                    {
                      name: 'start_on',
                      label: 'Repayment start period (1st or 16th)',
                      type: 'date',
                    },
                    {
                      name: 'acknowledgment',
                      label: 'Employee agreement / acknowledgment reference',
                    },
                    { name: 'reason', label: 'Approval reason' },
                  ]}
                  onSubmit={(payload) =>
                    onCommand(`/advances/${advance.record_id}/approve`, payload)
                  }
                />
              ) : null}
              {permissions.release &&
              ['APPROVED', 'RELEASED'].includes(advance.state) &&
              independentReviewer(employeeId, [advance.approved_by, advance.employee_id]) ? (
                <FinanceForm
                  title="Record actual release"
                  busy={busy}
                  fields={[
                    { name: 'amount', label: 'Released amount (PHP)', money: true },
                    {
                      name: 'occurred_on',
                      label: 'Actual release date',
                      type: 'date',
                      value: financialToday(),
                    },
                    { name: 'reference', label: 'Release and acknowledgment reference' },
                  ]}
                  onSubmit={(payload) =>
                    onCommand(`/advances/${advance.record_id}/release`, payload)
                  }
                />
              ) : null}
              {permissions.release &&
              advance.kind === 'OPERATING' &&
              advance.state === 'RELEASED' ? (
                <FinanceForm
                  title="Record unused operating funds returned"
                  busy={busy}
                  fields={[
                    { name: 'amount', label: 'Returned amount (PHP)', money: true },
                    {
                      name: 'occurred_on',
                      label: 'Return date',
                      type: 'date',
                      value: financialToday(),
                    },
                    { name: 'reference', label: 'Return reference' },
                  ]}
                  onSubmit={(payload) =>
                    onCommand(`/advances/${advance.record_id}/return`, payload)
                  }
                />
              ) : null}
              {permissions.delegate &&
              advance.kind === 'OPERATING' &&
              ['RELEASED', 'REVIEW_REQUIRED'].includes(advance.state) ? (
                <FinanceForm
                  title="Review operating reconciliation"
                  busy={busy}
                  fields={[{ name: 'reason', label: 'Independent review reference' }]}
                  onSubmit={(payload) =>
                    onCommand(`/advances/${advance.record_id}/reconcile`, payload)
                  }
                />
              ) : null}
              <details className="text-xs">
                <summary className="cursor-pointer">Movement history</summary>
                <ul className="mt-2 space-y-1">
                  {advance.movements.map((movement) => (
                    <li key={movement.record_id}>
                      {movement.occurred_on} · {movement.kind} · {formatPeso(movement.amount)} ·{' '}
                      {movement.reference}
                    </li>
                  ))}
                </ul>
              </details>
            </td>
          </tr>
        ))}
      </FinanceTable>
      {permissions.delegate && delegations.length ? (
        <FinanceTable columns={['Approver', 'Expires', 'Reason', 'Action']} empty={false}>
          {delegations.map((delegation) => (
            <tr key={delegation.record_id}>
              <td>{financialPerson(people, delegation.employee_id)}</td>
              <td>{delegation.expires_on}</td>
              <td>{delegation.reason}</td>
              <td>
                {delegation.revoked !== 'true' ? (
                  <FinanceForm
                    title="Revoke delegation"
                    busy={busy}
                    fields={[{ name: 'reason', label: 'Revocation reason' }]}
                    onSubmit={(payload) =>
                      onCommand(`/advance-delegations/${delegation.record_id}/revoke`, payload)
                    }
                  />
                ) : (
                  'Revoked'
                )}
              </td>
            </tr>
          ))}
        </FinanceTable>
      ) : null}
    </div>
  )
}
