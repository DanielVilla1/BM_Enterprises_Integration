// ===== AI GENERATED: App =====
// Purpose: Application shell for Sprint 1 (sign-in and account view)
// Inputs: none
// Returns: gated page
// Flow:
// 1. Signed-out visitors get the Clerk sign-in form
// 2. Signed-in users load /me and see roles and capabilities
// 3. A missing publishable key shows a configuration notice

import { AccountSummary } from './components/AccountSummary'
import { useCurrentAccount } from './hooks/useCurrentAccount'
import { CLERK_PUBLISHABLE_KEY } from './shared/services/clerkConfig'
import {
  SessionTokenBridge,
  SignedInGate,
  SignedOutGate,
} from './shared/services/clerkSessionService'

/**
 * @function AccountPage
 * @description Connects the account hook to the presentational component.
 * @returns {import('react').ReactElement}
 */
function AccountPage() {
  const { loadState, account, failure } = useCurrentAccount()
  return <AccountSummary loadState={loadState} account={account} failure={failure} />
}

/**
 * @function App
 * @description Root component.
 * @returns {import('react').ReactElement}
 */
function App() {
  if (!CLERK_PUBLISHABLE_KEY) {
    return (
      <main className="mx-auto max-w-xl p-6">
        <p role="alert">
          Sign-in is not configured. Set VITE_CLERK_PUBLISHABLE_KEY in the environment.
        </p>
      </main>
    )
  }
  return (
    <main className="mx-auto max-w-2xl space-y-6 p-6">
      <h1 className="text-2xl font-bold">BM Enterprises Hauling</h1>
      <SignedOutGate />
      <SignedInGate>
        <SessionTokenBridge />
        <AccountPage />
      </SignedInGate>
    </main>
  )
}

export default App
