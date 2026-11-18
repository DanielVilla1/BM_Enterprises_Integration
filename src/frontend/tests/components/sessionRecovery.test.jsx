import { renderToStaticMarkup } from 'react-dom/server'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import permissionMatrix from '../../../backend/src/Data/permission_matrix.json'

const session = vi.hoisted(() => ({
  sessionId: 'session-test',
  email: 'person@example.invalid',
  loadState: 'failed',
  failure: { code: 'AUTH_NO_ACTIVE_EMPLOYEE' },
}))

vi.mock('@clerk/react', () => ({
  ClerkProvider: ({ children }) => children,
  Show: ({ when, children }) => (when === 'signed-in' ? children : null),
  SignIn: () => <span>Sign in</span>,
  UserButton: () => <span>User menu</span>,
  SignOutButton: ({ children, redirectUrl, signOutOptions }) => (
    <span data-session={signOutOptions?.sessionId} data-redirect={redirectUrl}>
      {children}
    </span>
  ),
  useAuth: () => ({ sessionId: session.sessionId, getToken: vi.fn() }),
  useUser: () => ({ user: { primaryEmailAddress: { emailAddress: session.email } } }),
}))
vi.mock('../../src/shared/services/clerkConfig', () => ({
  CLERK_PUBLISHABLE_KEY: 'pk_test_placeholder',
}))
vi.mock('../../src/hooks/useCurrentAccount', () => ({
  useCurrentAccount: () => ({
    loadState: session.loadState,
    failure: session.failure,
    account: null,
  }),
}))
vi.mock('../../src/hooks/useTheme', () => ({
  useTheme: () => ({ theme: 'dark', toggleTheme: vi.fn() }),
}))
vi.mock('../../src/pages/AppPages', () => ({ PageContent: () => <main>Protected workspace</main> }))

import App from '../../src/App'

beforeEach(() => {
  session.loadState = 'failed'
  session.failure = { code: 'AUTH_NO_ACTIVE_EMPLOYEE' }
})

describe('session recovery before an employee account loads', () => {
  it.each(permissionMatrix.roles)(
    'lets an unlinked $code identity sign out of its own session',
    ({ code }) => {
      session.sessionId = `session-${code}`
      session.email = `${code.toLowerCase()}@example.invalid`
      const markup = renderToStaticMarkup(<App />)
      expect(markup).toContain('Your account is not set up yet')
      expect(markup).toContain(`Signed in as ${session.email}`)
      expect(markup).toContain('Try again')
      expect(markup).toContain('Sign out')
      expect(markup).toContain(`data-session="session-${code}"`)
      expect(markup).toContain('data-redirect="/"')
      expect(markup).not.toContain('Protected workspace')
    },
  )

  it.each(['NETWORK_ERROR', 'REQUEST_TIMEOUT', 'HTTP_ERROR'])(
    'retains sign-out for %s failures',
    (code) => {
      session.failure = { code, title: 'Connection failed', detail: 'Please try again.' }
      const markup = renderToStaticMarkup(<App />)
      expect(markup).toContain('Connection failed')
      expect(markup).toContain('Sign out')
      expect(markup).not.toContain('Protected workspace')
    },
  )

  it('allows sign-out during the backend startup wait', () => {
    session.loadState = 'loading'
    session.failure = null
    const markup = renderToStaticMarkup(<App />)
    expect(markup).toContain('Connecting to your workspace')
    expect(markup).toContain('Sign out')
    expect(markup).not.toContain('Protected workspace')
  })

  it('distinguishes an inactive account and displays its own sign-in ID for support', () => {
    session.failure = {
      code: 'AUTH_NO_ACTIVE_EMPLOYEE',
      accountSetup: { reason: 'employee_inactive', clerkUserId: 'user_current_session' },
    }
    const markup = renderToStaticMarkup(<App />)
    expect(markup).toContain('Your employee account is inactive')
    expect(markup).toContain('Sign-in account ID: user_current_session')
    expect(markup).toContain('Sign out')
  })
})
