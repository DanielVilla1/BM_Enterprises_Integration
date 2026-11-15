// ===== AI GENERATED: RowMenu =====
// Purpose: A three-dots menu for the actions of one list row or card
// Inputs: accessible label and a list of items (props only)
// Returns: dropdown markup, or nothing when there are no items
// Flow:
// 1. Items run their handler and close the menu
// 2. Destructive items are tinted red

import { Icon } from './Icon'

/**
 * @function RowMenu
 * @description Pure UI action menu.
 * @param {{label: string, items: Array<{label: string, onSelect: function(): void, danger?: boolean}>}} componentProps
 * @returns {import('react').ReactElement|null}
 */
export function RowMenu({ label, items }) {
  if (items.length === 0) return null
  return (
    <div className="dropdown dropdown-end">
      <button type="button" tabIndex={0} className="btn btn-ghost btn-sm btn-square" aria-label={label}>
        <Icon name="dots" />
      </button>
      <ul tabIndex={0} className="menu dropdown-content z-20 w-52 rounded-box border border-base-300 bg-base-100 p-2 shadow-lg">
        {items.map((menuItem) => (
          <li key={menuItem.label}>
            <button
              type="button"
              className={menuItem.danger ? 'text-error' : ''}
              onClick={() => {
                document.activeElement?.blur()
                menuItem.onSelect()
              }}
            >
              {menuItem.label}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
