// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: App =====
// Purpose: Application root: sign-in, then the workspace with navigation and pages
// Inputs: none
// Returns: gated workspace
// Flow:
// 1. Missing setup or signed-out visitors get a branded notice or sign-in screen
// 2. Signed-in users load /me; navigation shows only the pages their roles allow
// 3. The shell frames whichever page is open

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { AppShell } from './shared/components/AppShell'
import { FullPageNotice } from './shared/components/FullPageNotice'
import { SignInScreen } from './shared/components/SignInScreen'
import { PageContent } from './pages/AppPages'
import { useCurrentAccount } from './hooks/useCurrentAccount'
import { useTheme } from './hooks/useTheme'
import { CLERK_PUBLISHABLE_KEY } from './shared/services/clerkConfig'
import {
  SessionSignIn,
  SessionTokenBridge,
  SessionUserButton,
  SignedInGate,
  SignedOutGate,
} from './shared/services/clerkSessionService'
import { resolveActivePage, visibleNavigation } from './shared/utils/navigation'
import { roleLabel } from './shared/utils/permissionMatrix'
import { useNavigationStore } from './store/navigationStore'

/**
 * @function Workspace
 * @description Signed-in area: loads the account, then shows the shell and the active page.
 * @returns {import('react').ReactElement}
 */
function Workspace() {
  const { loadState, account, failure } = useCurrentAccount()
  const activePage = useNavigationStore((state) => state.activePage)
  const openPage = useNavigationStore((state) => state.openPage)
  const { theme, toggleTheme } = useTheme()

  if (loadState === 'failed') {
    const notLinked = failure?.code === 'AUTH_NO_ACTIVE_EMPLOYEE'
    return (
      <FullPageNotice
        tone={notLinked ? 'warning' : 'error'}
        title={
          notLinked ? 'Your account is not set up yet' : (failure?.title ?? 'Something went wrong')
        }
        message={
          notLinked
            ? 'You are signed in, but not linked to an active employee record. Ask the Owner to activate your account, then refresh this page.'
            : failure?.detail
        }
      >
        {failure?.traceIdentifier ? (
          <p className="text-xs text-base-content/50">Reference: {failure.traceIdentifier}</p>
        ) : null}
        <button
          type="button"
          className="btn btn-primary btn-sm mt-2"
          onClick={() => window.location.reload()}
        >
          Try again
        </button>
      </FullPageNotice>
    )
  }
  if (loadState !== 'ready')
    return <FullPageNotice busy title="Loading your workspace" message="One moment…" />

  const pages = visibleNavigation(account.capabilities)
  const shownPage = resolveActivePage(pages, activePage)
  return (
    <AppShell
      pages={pages}
      activePage={shownPage}
      onSelect={openPage}
      userName={account.full_name}
      roleLabel={account.role_codes.map(roleLabel).join(' · ') || 'No role yet'}
      userSlot={<SessionUserButton />}
      theme={theme}
      onToggleTheme={toggleTheme}
    >
      <PageContent pageKey={shownPage} account={account} openPage={openPage} />
    </AppShell>
  )
}

/**
 * @function App
 * @description Root component.
 * @returns {import('react').ReactElement}
 */
function App() {
  if (!CLERK_PUBLISHABLE_KEY) {
    return (
      <FullPageNotice
        tone="warning"
        title="Sign-in is not configured"
        message="Add VITE_CLERK_PUBLISHABLE_KEY to frontend/.env and restart the dev server. To explore the screens without signing in, open /preview.html."
      />
    )
  }
  return (
    <>
      <SignedOutGate>
        <SignInScreen>
          <SessionSignIn />
        </SignInScreen>
      </SignedOutGate>
      <SignedInGate>
        <SessionTokenBridge />
        <Workspace />
      </SignedInGate>
    </>
  )
}

export default App
