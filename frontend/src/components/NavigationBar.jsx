// ===== AI GENERATED: NavigationBar =====
// Purpose: Page tabs for the pages the backend allows
// Inputs: items, activePage, onSelect (props only)
// Returns: nav markup
// Flow:
// 1. One button per visible page
// 2. Report the chosen page key to the parent

/**
 * @function NavigationBar
 * @description Pure UI navigation.
 * @param {{items: Array<{key: string, label: string}>, activePage: string, onSelect: function(string): void}} componentProps
 * @returns {import('react').ReactElement}
 */
export function NavigationBar({ items, activePage, onSelect }) {
  return (
    <nav aria-label="Main" className="flex flex-wrap gap-2 border-b pb-2">
      {items.map((navigationItem) => (
        <button
          key={navigationItem.key}
          type="button"
          aria-current={navigationItem.key === activePage ? 'page' : undefined}
          onClick={() => onSelect(navigationItem.key)}
          className={`rounded px-3 py-1 ${
            navigationItem.key === activePage ? 'bg-gray-900 text-white' : 'bg-gray-100'
          }`}
        >
          {navigationItem.label}
        </button>
      ))}
    </nav>
  )
}
