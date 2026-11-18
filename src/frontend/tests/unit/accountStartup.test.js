import axios from 'axios'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import permissionMatrix from '../../../backend/src/Data/permission_matrix.json'
import { financePermissions } from '../../src/shared/utils/finance'
import { visibleNavigation } from '../../src/shared/utils/navigation'

let handleRequest
let fetchCurrentAccount
let apiClient
let registerSessionTokenProvider

function reply(config, data) {
  return { config, data, status: 200, statusText: 'OK', headers: {} }
}

beforeEach(async () => {
  vi.resetModules()
  const createClient = axios.create.bind(axios)
  vi.spyOn(axios, 'create').mockImplementation((configuration) =>
    createClient({ ...configuration, adapter: (config) => handleRequest(config) }),
  )
  ;({ fetchCurrentAccount } = await import('../../src/services/accountService'))
  ;({ apiClient, registerSessionTokenProvider } =
    await import('../../src/shared/services/httpClient'))
})

afterEach(() => vi.restoreAllMocks())

const ROLE_CASES = [
  {
    role: 'OWNER',
    pages: [
      'dashboard',
      'dispatch',
      'orders',
      'clients',
      'fleet',
      'expenses',
      'payroll',
      'advances',
      'billing',
      'reports',
      'people',
      'audit',
      'permissions',
      'account',
    ],
    actions: [
      'enter',
      'review',
      'charge',
      'calculate',
      'rates',
      'reverse',
      'adjust',
      'approveAdjustment',
      'approveAdvance',
      'delegate',
      'voidInvoice',
    ],
  },
  {
    role: 'DISPATCHER',
    pages: [
      'dashboard',
      'dispatch',
      'orders',
      'clients',
      'fleet',
      'expenses',
      'reports',
      'people',
      'account',
    ],
    actions: ['enter'],
  },
  { role: 'FLEET_MANAGER', pages: ['fleet', 'reports', 'people', 'account'], actions: [] },
  {
    role: 'DRIVER',
    pages: ['trips', 'expenses', 'payroll', 'advances', 'reports', 'account'],
    actions: ['enter', 'request'],
  },
  {
    role: 'HELPER',
    pages: ['trips', 'payroll', 'advances', 'reports', 'account'],
    actions: ['request'],
  },
  {
    role: 'HR_PAYROLL',
    pages: ['payroll', 'advances', 'reports', 'people', 'account'],
    actions: [
      'calculate',
      'prepare',
      'adjust',
      'creditAdjustment',
      'pay',
      'request',
      'approveAdvance',
      'release',
    ],
  },
  {
    role: 'ACCOUNTING',
    pages: ['orders', 'clients', 'expenses', 'billing', 'reports', 'account'],
    actions: ['review', 'charge', 'bill'],
  },
]

describe.each([false, true])('all roles with delayed startup = %s', (delayed) => {
  it.each(ROLE_CASES)(
    'retains $role account scope, menus and financial actions',
    async ({ role, pages, actions }) => {
      const capabilities = Object.fromEntries(
        permissionMatrix.capabilities
          .filter((entry) => entry.grants[role] && !entry.conditional?.[role])
          .map((entry) => [entry.capability, entry.grants[role]]),
      )
      const expectedAccount = {
        employee_id: `employee-${role}`,
        full_name: `Test ${role}`,
        role_codes: [role],
        capabilities,
      }
      let releaseHealth
      const ready = delayed
        ? new Promise((resolve) => {
            releaseHealth = resolve
          })
        : Promise.resolve()
      const getToken = vi.fn(async () => `test-session-${role}`)
      registerSessionTokenProvider(getToken)
      const requests = []
      handleRequest = async (config) => {
        requests.push(config)
        if (config.url === '/health') {
          await ready
          return reply(config, { status: 'ok' })
        }
        return reply(config, expectedAccount)
      }

      const pending = fetchCurrentAccount()
      if (delayed) {
        await vi.waitFor(() => expect(requests).toHaveLength(1))
        expect(getToken).not.toHaveBeenCalled()
        releaseHealth()
      }
      const account = await pending
      expect(account).toEqual(expectedAccount)
      expect(requests.map((request) => request.url)).toEqual(['/health', '/me'])
      expect(requests[0].headers.get('Authorization')).toBeUndefined()
      expect(requests[1].headers.get('Authorization')).toBe(`Bearer test-session-${role}`)
      const navigation = visibleNavigation(account.capabilities)
      expect(navigation.map((page) => page.key)).toEqual(pages)
      expect(navigation.some((page) => page.preview)).toBe(false)
      const enabledActions = Object.entries(financePermissions(account.capabilities))
        .filter(([, enabled]) => enabled)
        .map(([name]) => name)
      expect(enabledActions.sort()).toEqual([...actions].sort())
    },
  )
})

it('includes every business role declared by the backend seed', () => {
  expect(ROLE_CASES.map(({ role }) => role).sort()).toEqual(
    permissionMatrix.roles.map(({ code }) => code).sort(),
  )
})

describe('hosted account startup', () => {
  it('waits for public health before obtaining a token and reading the account', async () => {
    let releaseHealth
    const healthReady = new Promise((resolve) => {
      releaseHealth = resolve
    })
    const requests = []
    const getToken = vi.fn(async () => 'test-session-token')
    registerSessionTokenProvider(getToken)
    handleRequest = async (config) => {
      requests.push(config)
      if (config.url === '/health') {
        await healthReady
        return reply(config, { status: 'ok' })
      }
      return reply(config, { employee_id: 'hosted-owner' })
    }

    const account = fetchCurrentAccount()
    await vi.waitFor(() => expect(requests).toHaveLength(1))
    expect(requests[0].url).toBe('/health')
    expect(requests[0].timeout).toBe(90000)
    expect(requests[0].headers.get('Authorization')).toBeUndefined()
    expect(getToken).not.toHaveBeenCalled()

    releaseHealth()
    await expect(account).resolves.toEqual({ employee_id: 'hosted-owner' })
    expect(requests.map((request) => request.url)).toEqual(['/health', '/me'])
    expect(requests[1].headers.get('Authorization')).toBe('Bearer test-session-token')
    expect(requests[1].timeout).toBe(10000)
  })

  it('keeps a gateway failure distinct from a network failure and skips the account read', async () => {
    const requests = []
    handleRequest = async (config) => {
      requests.push(config.url)
      throw { response: { status: 503, data: '<html>starting</html>' } }
    }
    await expect(fetchCurrentAccount()).rejects.toMatchObject({ code: 'HTTP_ERROR', status: 503 })
    expect(requests).toEqual(['/health'])
  })

  it('reports a bounded startup timeout and does not request an account', async () => {
    const requests = []
    handleRequest = async (config) => {
      requests.push(config.url)
      throw { code: 'ECONNABORTED' }
    }
    await expect(fetchCurrentAccount()).rejects.toMatchObject({ code: 'REQUEST_TIMEOUT' })
    expect(requests).toEqual(['/health'])
  })

  it('rejects an HTML health response instead of sending an account token', async () => {
    const getToken = vi.fn()
    registerSessionTokenProvider(getToken)
    handleRequest = async (config) => reply(config, '<html>wrong deployment</html>')
    await expect(fetchCurrentAccount()).rejects.toMatchObject({ code: 'UNEXPECTED_RESPONSE' })
    expect(getToken).not.toHaveBeenCalled()
  })

  it('preserves the short timeout and sends financial writes only once', async () => {
    const requests = []
    handleRequest = async (config) => {
      requests.push(config)
      throw { code: 'ECONNABORTED' }
    }
    await expect(apiClient.post('/finance/invoices')).rejects.toMatchObject({
      code: 'REQUEST_TIMEOUT',
    })
    expect(requests).toHaveLength(1)
    expect(requests[0].timeout).toBe(10000)
    expect(requests[0].method).toBe('post')
  })
})
