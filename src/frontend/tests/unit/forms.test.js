// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: forms.test conventions =====
// Purpose: Preserve this module while standardizing source formatting.
// Inputs: Existing module configuration or test fixtures.
// Returns: Existing exports or regression assertions.
// Flow: Apply the documented frontend conventions without changing behavior.
// AI MODIFIED: Formatting consistency.

import { describe, expect, it } from 'vitest'
import {
  buildChanges,
  compactPayload,
  isUploadTooLarge,
  localInputToIso,
  toLocalInputValue,
} from '../../src/shared/utils/forms'

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

  // AI MODIFIED: A receipt recorded after delivery must not round back before it.
  it('preserves the actual receipt instant when delivery occurred in the same minute', () => {
    const deliveredAt = new Date(2026, 10, 18, 9, 5, 42, 100)
    const receivedAt = new Date(2026, 10, 18, 9, 5, 45, 321)
    const inputValue = toLocalInputValue(receivedAt, 'milliseconds')
    const submittedAt = new Date(localInputToIso(inputValue))
    expect(submittedAt.getTime()).toBe(receivedAt.getTime())
    expect(submittedAt.getTime()).toBeGreaterThan(deliveredAt.getTime())
  })

  it('converts a local input value to an ISO string with an offset', () => {
    const iso = localInputToIso('2026-11-14T09:05')
    expect(iso.endsWith('Z')).toBe(true)
    expect(new Date(iso).getTime()).toBe(new Date(2026, 10, 14, 9, 5).getTime())
  })
})

describe('buildChanges', () => {
  const record = { name: 'Acme', address: null, weight: 48.5, phone: '123' }

  it('returns only changed fields and turns empty text into null', () => {
    const changes = buildChanges(record, { name: 'Acme', address: '  Plant Road ', phone: '' }, [
      'name',
      'address',
      'phone',
    ])
    expect(changes).toEqual({ address: 'Plant Road', phone: null })
  })

  it('compares numeric fields as numbers', () => {
    expect(buildChanges(record, { weight: '48.50' }, ['weight'], ['weight'])).toEqual({})
    expect(buildChanges(record, { weight: '60' }, ['weight'], ['weight'])).toEqual({ weight: 60 })
  })

  it('ignores fields missing from the form', () => {
    expect(buildChanges(record, {}, ['name'])).toEqual({})
  })
})
