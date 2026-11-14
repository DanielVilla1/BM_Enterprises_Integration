import { describe, expect, it } from 'vitest'
import { compactPayload, isUploadTooLarge, localInputToIso, toLocalInputValue } from './forms'

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

describe('upload and date helpers', () => {
  it('flags files over 5 MB only', () => {
    expect(isUploadTooLarge({ size: 5 * 1024 * 1024 })).toBe(false)
    expect(isUploadTooLarge({ size: 5 * 1024 * 1024 + 1 })).toBe(true)
  })

  it('formats a local date for datetime-local inputs', () => {
    expect(toLocalInputValue(new Date(2026, 10, 14, 9, 5))).toBe('2026-11-14T09:05')
  })

  it('converts a local input value to an ISO string with an offset', () => {
    const iso = localInputToIso('2026-11-14T09:05')
    expect(iso.endsWith('Z')).toBe(true)
    expect(new Date(iso).getTime()).toBe(new Date(2026, 10, 14, 9, 5).getTime())
  })
})
