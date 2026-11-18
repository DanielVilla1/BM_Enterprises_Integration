// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: problemDetails.test conventions =====
// Purpose: Preserve this module while standardizing source formatting.
// Inputs: Existing module configuration or test fixtures.
// Returns: Existing exports or regression assertions.
// Flow: Apply the documented frontend conventions without changing behavior.
// AI MODIFIED: Formatting consistency.

import { describe, expect, it } from 'vitest'
import { normalizeApiError } from '../../src/shared/utils/problemDetails'

describe('normalizeApiError', () => {
  it('reads an RFC 9457 problem body', () => {
    const failure = normalizeApiError({
      response: {
        status: 409,
        data: {
          code: 'CAPACITY_EXCEEDED',
          title: 'Conflict',
          detail: 'Too heavy.',
          trace_id: 'abc123',
        },
      },
    })
    expect(failure).toEqual({
      status: 409,
      code: 'CAPACITY_EXCEEDED',
      title: 'Conflict',
      detail: 'Too heavy.',
      traceIdentifier: 'abc123',
      fieldErrors: [],
    })
  })

  it('keeps field errors for validation failures', () => {
    const failure = normalizeApiError({
      response: {
        status: 422,
        data: { code: 'VALIDATION_ERROR', errors: [{ field: 'body.email', message: 'invalid' }] },
      },
    })
    expect(failure.fieldErrors).toEqual([{ field: 'body.email', message: 'invalid' }])
  })

  it('maps an unreachable server to a network error', () => {
    const failure = normalizeApiError(new Error('Network Error'))
    expect(failure.status).toBe(0)
    expect(failure.code).toBe('NETWORK_ERROR')
  })

  it('never throws on a non-object body', () => {
    const failure = normalizeApiError({
      response: { status: 502, data: '<html>bad gateway</html>' },
    })
    expect(failure.code).toBe('HTTP_ERROR')
    expect(failure.status).toBe(502)
    expect(failure.title).toBe('Service temporarily unavailable')
    expect(failure.detail).not.toContain('<html>')
  })

  it.each(['ECONNABORTED', 'ETIMEDOUT'])(
    'distinguishes a %s timeout from network failures',
    (code) => {
      const failure = normalizeApiError({ code })
      expect(failure.code).toBe('REQUEST_TIMEOUT')
      expect(failure.title).toBe('Connection timed out')
    },
  )

  it('rejects an HTML success response without claiming the network was unreachable', () => {
    const failure = normalizeApiError({
      response: { status: 200, data: '<html>wrong site</html>' },
    })
    expect(failure.code).toBe('UNEXPECTED_RESPONSE')
    expect(failure.status).toBe(200)
  })
})
