// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: SignInScreen =====
// Purpose: Branded full-page layout around the Clerk sign-in form
// Inputs: the sign-in form as children (props only)
// Returns: split layout markup
// Flow:
// 1. Brand panel with the product promise (hidden on small screens)
// 2. The identity provider's form centred on the right

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { Icon } from './Icon'

const HIGHLIGHTS = [
  'Assign trucks and crews with capacity and license checks built in',
  'Drivers upload the signed OR from their phone',
  'One record of every delivery, from order to completion',
]

/**
 * @function SignInScreen
 * @description Pure UI sign-in page frame.
 * @param {{children: import('react').ReactNode}} componentProps
 * @returns {import('react').ReactElement}
 */
export function SignInScreen({ children }) {
  return (
    <div className="grid min-h-screen bg-base-200 lg:grid-cols-2">
      <section className="relative hidden flex-col justify-between overflow-hidden bg-base-300 p-12 lg:flex">
        <div className="pointer-events-none absolute -right-24 -top-24 h-96 w-96 rounded-full bg-primary/20 blur-3xl" />
        <div className="flex items-center gap-3">
          <span className="flex h-12 w-12 items-center justify-center rounded-box bg-primary text-primary-content">
            <Icon name="truck" className="h-7 w-7" />
          </span>
          <span className="text-xl font-extrabold tracking-tight">BM Enterprises</span>
        </div>
        <div className="space-y-6">
          <h1 className="text-4xl font-extrabold leading-tight tracking-tight">
            Every load, every crew,
            <br />
            <span className="text-primary">one clear picture.</span>
          </h1>
          <ul className="space-y-3 text-base-content/80">
            {HIGHLIGHTS.map((highlight) => (
              <li key={highlight} className="flex items-start gap-3">
                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/20 text-primary">
                  <Icon name="check" className="h-4 w-4" />
                </span>
                {highlight}
              </li>
            ))}
          </ul>
        </div>
        <p className="text-xs text-base-content/50">
          Subcontracted steel hauling · internal system
        </p>
      </section>
      <section className="flex flex-col items-center justify-center gap-6 p-6">
        <div className="flex items-center gap-3 lg:hidden">
          <span className="flex h-11 w-11 items-center justify-center rounded-box bg-primary text-primary-content">
            <Icon name="truck" className="h-6 w-6" />
          </span>
          <span className="text-lg font-extrabold tracking-tight">BM Enterprises</span>
        </div>
        {children}
      </section>
    </div>
  )
}
