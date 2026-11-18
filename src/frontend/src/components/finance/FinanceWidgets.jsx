// ===== AI GENERATED: FinanceWidgets =====
// Purpose: Accessible reusable financial forms and tables within the existing design system.
// Inputs: Field descriptors, records and callbacks; no network or calculation logic.
// Returns: Responsive labelled controls, record references and empty states.
// Flow: Submit unrounded form strings and leave financial validation to the API.

import { FormField } from '../../shared/components/FormField'
import { financeReference } from '../../shared/utils/finance'

/** @param {{title:string,fields:Array<Object>,onSubmit:Function,busy:boolean,submitLabel?:string}} props @returns {import('react').ReactElement} */
export function FinanceForm({ title, fields, onSubmit, busy, submitLabel = 'Save' }) {
  return (
    <details className="rounded-box border border-base-300 bg-base-100 p-4">
      <summary className="cursor-pointer font-semibold">{title}</summary>
      <form
        className="mt-3 grid gap-3 sm:grid-cols-2"
        onSubmit={async (event) => {
          event.preventDefault()
          const form = event.currentTarget
          const payload = Object.fromEntries(new FormData(form))
          for (const field of fields)
            if (field.multiple) payload[field.name] = new FormData(form).getAll(field.name)
          if (await onSubmit(payload)) form.reset()
        }}
      >
        {fields.map((field) => (
          <FormField key={field.name} label={field.label} hint={field.hint}>
            {field.options ? (
              <select
                className="select select-bordered w-full"
                name={field.name}
                defaultValue={field.value ?? (field.multiple ? [] : '')}
                required={field.required !== false}
                multiple={field.multiple}
                size={field.multiple ? 5 : undefined}
              >
                {!field.multiple ? <option value="">Choose…</option> : null}
                {field.options.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            ) : (
              <input
                className="input input-bordered w-full"
                name={field.name}
                type={field.type ?? 'text'}
                defaultValue={field.value ?? ''}
                required={field.required !== false}
                min={field.min}
                max={field.max}
                step={field.step}
                inputMode={field.money ? 'decimal' : undefined}
                pattern={field.money ? '[0-9]+([.][0-9]{1,2})?' : undefined}
                maxLength={field.money ? 13 : 1000}
              />
            )}
          </FormField>
        ))}
        <div className="flex items-end sm:col-span-2">
          <button className="btn btn-primary btn-sm" type="submit" disabled={busy}>
            {busy ? 'Saving…' : submitLabel}
          </button>
        </div>
      </form>
    </details>
  )
}

/** @param {{columns:Array<string>,children:import('react').ReactNode,empty:boolean}} props @returns {import('react').ReactElement} */
export function FinanceTable({ columns, children, empty }) {
  return (
    <div className="overflow-x-auto rounded-box border border-base-300 bg-base-100">
      <table className="table table-sm">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {empty ? (
            <tr>
              <td colSpan={columns.length} className="py-8 text-center text-base-content/60">
                No records on this page.
              </td>
            </tr>
          ) : (
            children
          )}
        </tbody>
      </table>
    </div>
  )
}

/** @param {{identifier:string}} props @returns {import('react').ReactElement} */
export function FinanceId({ identifier }) {
  return (
    <span className="font-mono text-xs" title={identifier}>
      {financeReference(identifier)}
    </span>
  )
}
