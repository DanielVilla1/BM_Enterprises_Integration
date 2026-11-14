import { describe, expect, it } from 'vitest'
import { compactPayload } from './forms'

describe('compactPayload', () => {
  it('drops empty and whitespace-only values and trims the rest', () => {
    expect(compactPayload({ name: '  Acme  ', address: '', phone: '   ', weight: 0 })).toEqual({
      name: 'Acme',
      weight: 0,
    })
  })

  it('drops null and undefined but keeps false', () => {
    expect(compactPayload({ a: null, b: undefined, c: false })).toEqual({ c: false })
  })
})
