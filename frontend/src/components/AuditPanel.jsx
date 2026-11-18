// ===== AI GENERATED: AuditPanel =====
// Purpose: The Owner's audit log: who did what and when
// Inputs: records, paging state and callbacks (props only)
// Returns: page markup
// Flow:
// 1. Newest first, readable sentences, searchable
// 2. Each entry expands to its recorded details; "Load more" fetches the next page

import { useState } from 'react'
import { formatDateTime, shortIdentifier } from '../shared/utils/formatting'
import { describeAuditAction, filterAuditRecords } from '../shared/utils/people'
import { EmptyState } from './EmptyState'
import { ErrorNotice } from './ErrorNotice'
import { ListSkeleton } from './ListSkeleton'
import { PageHeader } from './PageHeader'
import { SearchField } from './SearchField'

/**
 * @function AuditPanel
 * @description Pure UI for the audit log.
 * @param {{loadState: string, records: Array<Object>, hasMore: boolean, failure: Object|null, onLoadMore: function(): void}} componentProps
 * @returns {import('react').ReactElement}
 */
export function AuditPanel({ loadState, records, hasMore, failure, onLoadMore }) {
  const [query, setQuery] = useState('')
  const visibleRecords = filterAuditRecords(records, query)
  return (
    <section className="space-y-5">
      <PageHeader title="Audit log" subtitle="Every important change, with who made it and when. Records cannot be edited or deleted." />
      <ErrorNotice failure={failure} />
      <SearchField value={query} onChange={setQuery} placeholder="Search action, type or reference" />

      {loadState === 'loading' && records.length === 0 ? <ListSkeleton rows={6} /> : null}
      {loadState !== 'loading' && visibleRecords.length === 0 ? (
        <EmptyState icon="shield" title={records.length === 0 ? 'Nothing recorded yet' : 'No entries match'} description="Changes to employees, trips, documents and more appear here as they happen." />
      ) : null}

      {visibleRecords.length > 0 ? (
        <ul className="card card-border divide-y divide-base-300 bg-base-100">
          {visibleRecords.map((record) => {
            const detailEntries = Object.entries(record.details ?? {})
            return (
              <li key={record.audit_id} className="p-4">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="font-semibold">{describeAuditAction(record.action)}</p>
                    <p className="text-xs text-base-content/60">
                      {record.entity_type} {shortIdentifier(record.entity_id)} · by {record.actor_employee_id ? shortIdentifier(record.actor_employee_id) : 'the system'}
                    </p>
                  </div>
                  <time className="text-xs text-base-content/60" dateTime={record.occurred_at}>
                    {formatDateTime(record.occurred_at)}
                  </time>
                </div>
                {detailEntries.length > 0 ? (
                  <div className="collapse collapse-arrow mt-2 rounded-field bg-base-200">
                    <input type="checkbox" aria-label="Show details" />
                    <div className="collapse-title min-h-0 py-2 text-xs font-medium">Details</div>
                    <div className="collapse-content">
                      <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-xs">
                        {detailEntries.map(([name, value]) => (
                          <div key={name} className="contents">
                            <dt className="text-base-content/60">{name}</dt>
                            <dd className="break-words font-mono">{typeof value === 'string' ? value : JSON.stringify(value)}</dd>
                          </div>
                        ))}
                      </dl>
                    </div>
                  </div>
                ) : null}
                {record.trace_id ? <p className="mt-1 font-mono text-[10px] text-base-content/40">trace {record.trace_id}</p> : null}
              </li>
            )
          })}
        </ul>
      ) : null}

      {hasMore ? (
        <div className="flex justify-center">
          <button type="button" className="btn btn-outline" onClick={onLoadMore}>
            Load older entries
          </button>
        </div>
      ) : null}
    </section>
  )
}
