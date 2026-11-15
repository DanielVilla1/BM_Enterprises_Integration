// ===== AI GENERATED: FilterTabs =====
// Purpose: Segmented tabs with counts, used to filter lists
// Inputs: tabs, active key, counts and a change handler (props only)
// Returns: tab strip markup
// Flow:
// 1. One button per tab; the active one is highlighted
// 2. Counts appear as small badges when provided

/**
 * @function FilterTabs
 * @description Pure UI filter tabs.
 * @param {{tabs: Array<{key: string, label: string}>, activeKey: string, counts?: Object<string, number>, onChange: function(string): void, label?: string}} componentProps
 * @returns {import('react').ReactElement}
 */
export function FilterTabs({ tabs, activeKey, counts, onChange, label = 'Filter' }) {
  return (
    <div role="tablist" aria-label={label} className="tabs tabs-box w-fit max-w-full overflow-x-auto bg-base-100">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          type="button"
          role="tab"
          aria-selected={tab.key === activeKey}
          onClick={() => onChange(tab.key)}
          className={`tab gap-2 ${tab.key === activeKey ? 'tab-active' : ''}`}
        >
          {tab.label}
          {counts ? <span className="badge badge-sm badge-ghost">{counts[tab.key] ?? 0}</span> : null}
        </button>
      ))}
    </div>
  )
}
