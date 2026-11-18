// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: SearchField =====
// Purpose: A search box with an icon
// Inputs: value, placeholder and a change handler (props only)
// Returns: input markup
// Flow:
// 1. Controlled input; the parent filters the list

import { Icon } from './Icon'

/**
 * @function SearchField
 * @description Pure UI search input.
 * @param {{value: string, onChange: function(string): void, placeholder?: string}} componentProps
 * @returns {import('react').ReactElement}
 */
export function SearchField({ value, onChange, placeholder = 'Search' }) {
  return (
    <label className="input w-full sm:w-72">
      <Icon name="search" className="h-4 w-4 opacity-60" />
      <input
        type="search"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        aria-label={placeholder}
      />
    </label>
  )
}
