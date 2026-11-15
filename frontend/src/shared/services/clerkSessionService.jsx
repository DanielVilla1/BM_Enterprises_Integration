// ===== AI GENERATED: clerkSessionService =====
// Purpose: The only module that touches the Clerk SDK
// Inputs: VITE_CLERK_PUBLISHABLE_KEY
// Returns: provider, gates and a token bridge for the rest of the app
// Flow:
// 1. Wrap ClerkProvider with the publishable key (public by design)
// 2. Expose signed-in / signed-out gates and the sign-in form
// 3. Bridge getToken into the http client

// AI MODIFIED: Use the supported Core 3 SDK and its Show authentication gates.
import {
  ClerkProvider,
  Show,
  SignIn,
  useAuth,
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
 * @description Render the sign-in form for a signed-out visitor.
 * @returns {import('react').ReactElement}
 */
export function SignedOutGate() {
  return (
    <Show when="signed-out">
      <SignIn routing="hash" />
    </Show>
  )
}
