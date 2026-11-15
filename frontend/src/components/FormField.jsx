// ===== AI GENERATED: FormField =====
// Purpose: A labelled form control with optional hint text
// Inputs: label, hint and the control itself (props only)
// Returns: fieldset markup
// Flow:
// 1. The label wraps the control so clicking it focuses the field

/**
 * @function FormField
 * @description Pure UI form field wrapper.
 * @param {{label: string, hint?: string, className?: string, children: import('react').ReactNode}} componentProps
 * @returns {import('react').ReactElement}
 */
export function FormField({ label, hint, className = '', children }) {
  return (
    <label className={`fieldset ${className}`}>
      <span className="fieldset-legend">{label}</span>
      {children}
      {hint ? <span className="label text-xs">{hint}</span> : null}
    </label>
  )
}
