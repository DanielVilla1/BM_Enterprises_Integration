// ===== AI GENERATED: AccountSummary =====
// Purpose: The signed-in employee's profile and what their roles allow
// Inputs: loadState, account, failure (props only)
// Returns: page markup
// Flow:
// 1. Profile card with initials and role badges
// 2. Capabilities grouped by area, each with its access level and a legend

import { initialsOf } from '../shared/utils/formatting'
import { groupCapabilities, roleLabel } from '../shared/utils/permissionMatrix'
import { ErrorNotice } from './ErrorNotice'
import { ListSkeleton } from './ListSkeleton'
import { PageHeader } from './PageHeader'

const LEVEL_STYLE = {
  FULL: { label: 'Full access', className: 'badge-success' },
  VIEW: { label: 'View only', className: 'badge-info' },
  LTD: { label: 'Limited', className: 'badge-warning' },
  OWN: { label: 'Own records', className: 'badge-accent' },
}

/**
 * @function AccountSummary
 * @description Pure UI for the current account; makes no API calls.
 * @param {{loadState: string, account: Object|null, failure: Object|null}} componentProps
 * @returns {import('react').ReactElement}
 */
export function AccountSummary({ loadState, account, failure }) {
  if (loadState === 'failed') return <ErrorNotice failure={failure} />
  if (loadState === 'idle' || loadState === 'loading' || !account) return <ListSkeleton rows={2} />
  const groups = groupCapabilities(account.capabilities)
  return (
    <section className="space-y-5">
      <PageHeader title="My account" subtitle="Your profile and what your role allows you to do" />
      <div className="card card-border bg-base-100">
        <div className="card-body flex-row items-center gap-4">
          <div className="avatar avatar-placeholder">
            <div className="w-16 rounded-full bg-primary text-primary-content">
              <span className="text-xl font-bold">{initialsOf(account.full_name)}</span>
            </div>
          </div>
          <div>
            <h2 className="text-xl font-bold">{account.full_name}</h2>
            <div className="mt-1 flex flex-wrap gap-2">
              {account.role_codes.length === 0 ? (
                <span className="badge badge-ghost">No role assigned</span>
              ) : (
                account.role_codes.map((roleCode) => (
                  <span key={roleCode} className="badge badge-primary badge-soft">
                    {roleLabel(roleCode)}
                  </span>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 text-xs text-base-content/70">
        {Object.entries(LEVEL_STYLE).map(([level, style]) => (
          <span key={level} className={`badge badge-soft ${style.className}`}>
            {style.label}
          </span>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {groups.map((group) => (
          <div key={group.group} className="card card-border bg-base-100">
            <div className="card-body gap-2 p-5">
              <h3 className="font-semibold">{group.group}</h3>
              <ul className="divide-y divide-base-300">
                {group.entries.map((entry) => (
                  <li key={entry.capability} className="flex items-center justify-between gap-3 py-2 text-sm">
                    <span>{entry.label}</span>
                    <span className={`badge badge-soft ${LEVEL_STYLE[entry.level]?.className ?? 'badge-ghost'}`}>
                      {LEVEL_STYLE[entry.level]?.label ?? entry.level}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
