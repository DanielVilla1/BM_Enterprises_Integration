// ===== AI GENERATED: clerkSessionService =====
// Purpose: The only module that touches the Clerk SDK
// Inputs: VITE_CLERK_PUBLISHABLE_KEY
// Returns: provider, gates, sign-in form, user menu and a token bridge for the rest of the app
// Flow:
// 1. Wrap ClerkProvider with the publishable key (public by design)
// 2. Expose signed-in / signed-out gates, the sign-in form and the account menu (with sign-out)
// 3. Bridge getToken into the http client

// AI MODIFIED: Use the supported Core 3 SDK and its Show authentication gates.
// AI MODIFIED: Add the user menu and let the signed-out gate wrap a branded layout.
import {
  ClerkProvider,
  Show,
  SignIn,
  SignOutButton,
  UserButton,
  useAuth,
  useUser,
} from '@clerk/react'
import { useEffect } from 'react'
import { CLERK_PUBLISHABLE_KEY } from './clerkConfig'
import { registerSessionTokenProvider } from './httpClient'

/**
 * @function SessionProvider
 * @description Wrap the app with the identity provider.
 * @param {{children: import('react').ReactNode}} componentProps
 * @returns {import('react').ReactElement}
 */
export function SessionProvider({ children }) {
  return <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>{children}</ClerkProvider>
}

/**
 * @function SessionTokenBridge
 * @description Registers the session token getter with the http client.
 * @returns {null}
 */
export function SessionTokenBridge() {
  const { getToken } = useAuth()
  useEffect(() => {
    registerSessionTokenProvider(() => getToken())
  }, [getToken])
  return null
}

/**
 * @function SignedInGate
 * @description Render children only for a signed-in user.
 * @param {{children: import('react').ReactNode}} componentProps
 * @returns {import('react').ReactElement}
 */
export function SignedInGate({ children }) {
  return <Show when="signed-in">{children}</Show>
}

/**
 * @function SignedOutGate
 * @description Render children only for a signed-out visitor.
 * @param {{children: import('react').ReactNode}} componentProps
 * @returns {import('react').ReactElement}
 */
export function SignedOutGate({ children }) {
  return <Show when="signed-out">{children}</Show>
}

/**
 * @function SessionSignIn
 * @description The identity provider's sign-in form.
 * @returns {import('react').ReactElement}
 */
export function SessionSignIn() {
  return <SignIn routing="hash" />
}

/**
 * @function SessionUserButton
 * @description The account menu (profile, sign out).
 * @returns {import('react').ReactElement}
 */
export function SessionUserButton() {
  return <UserButton />
}

/** @returns {import('react').ReactElement} Recovery before an employee account can load. */
export function SessionSignOutButton() {
  const { sessionId } = useAuth()
  return (
    <SignOutButton redirectUrl="/" signOutOptions={{ sessionId: sessionId ?? undefined }}>
      <button type="button" className="btn btn-ghost btn-sm mt-2">
        Sign out
      </button>
    </SignOutButton>
  )
}

/** @returns {import('react').ReactElement|null} Identify the signed-in account on recovery screens. */
export function SessionIdentity() {
  const { user } = useUser()
  const email = user?.primaryEmailAddress?.emailAddress
  return email ? <p className="text-sm text-base-content/70">Signed in as {email}</p> : null
}
