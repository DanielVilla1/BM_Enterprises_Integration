// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: PermissionsPanel =====
// Purpose: The Owner's read-only view of who can do what (the permission matrix)
// Inputs: grants from the backend (props only)
// Returns: page markup
// Flow:
// 1. Rows are capabilities grouped by area; columns are the seven roles
// 2. Cells show the access level; the first column stays visible when scrolling sideways

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { useState } from 'react'
import { matchesQuery } from '../../shared/utils/operations'
import { buildMatrix, roleLabel } from '../../shared/utils/permissionMatrix'
import { EmptyState } from '../../shared/components/EmptyState'
import { ErrorNotice } from '../../shared/components/ErrorNotice'
import { ListSkeleton } from '../../shared/components/ListSkeleton'
import { PageHeader } from '../../shared/components/PageHeader'
import { SearchField } from '../../shared/components/SearchField'

const LEVEL_CELL = {
  FULL: { label: 'Full', className: 'badge-success' },
  VIEW: { label: 'View', className: 'badge-info' },
  LTD: { label: 'Limited', className: 'badge-warning' },
  OWN: { label: 'Own', className: 'badge-accent' },
}

/**
 * @function PermissionsPanel
 * @description Pure UI for the permission matrix.
 * @param {{loadState: string, grants: Array<Object>, failure: Object|null}} componentProps
 * @returns {import('react').ReactElement}
 */
export function PermissionsPanel({ loadState, grants, failure }) {
  const [query, setQuery] = useState('')
  const matrix = buildMatrix(grants)
  const rows = matrix.rows.filter((row) =>
    matchesQuery([row.label, row.group, row.capability], query),
  )
  return (
    <section className="space-y-5">
      <PageHeader
        title="Permissions"
        subtitle="What each role can do. The server enforces these rules on every request."
      />
      <ErrorNotice failure={failure} />
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2 text-xs">
          <span className="badge badge-soft badge-success">Full: create, view and edit</span>
          <span className="badge badge-soft badge-info">View: read only</span>
          <span className="badge badge-soft badge-warning">Limited: some fields only</span>
          <span className="badge badge-soft badge-accent">Own: only their own records</span>
        </div>
        <SearchField value={query} onChange={setQuery} placeholder="Search a capability" />
      </div>

      {(loadState === 'loading' || loadState === 'idle') && grants.length === 0 ? (
        <ListSkeleton rows={6} />
      ) : null}
      {loadState === 'ready' && rows.length === 0 ? (
        <EmptyState icon="key" title="No capabilities match" />
      ) : null}

      {rows.length > 0 ? (
        <div className="card card-border overflow-x-auto bg-base-100">
          <table className="table table-pin-rows">
            <thead>
              <tr>
                <th className="sticky left-0 z-10 bg-base-100">Capability</th>
                {matrix.roles.map((roleCode) => (
                  <th key={roleCode} className="text-center text-xs">
                    {roleLabel(roleCode)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, position) => (
                <tr key={row.capability} className="hover:bg-base-200/50">
                  <th className="sticky left-0 z-10 bg-base-100 font-medium">
                    {position === 0 || rows[position - 1].group !== row.group ? (
                      <span className="mb-0.5 block text-[10px] font-bold uppercase tracking-wider text-primary">
                        {row.group}
                      </span>
                    ) : null}
                    {row.label}
                  </th>
                  {matrix.roles.map((roleCode) => {
                    const level = row.cells[roleCode]
                    return (
                      <td key={roleCode} className="text-center">
                        {level ? (
                          <span
                            className={`badge badge-soft badge-sm ${LEVEL_CELL[level]?.className ?? 'badge-ghost'}`}
                          >
                            {LEVEL_CELL[level]?.label ?? level}
                          </span>
                        ) : (
                          <span className="text-base-content/30" aria-label="No access">
                            —
                          </span>
                        )}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  )
}
