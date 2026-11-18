import axios from 'axios'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

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
