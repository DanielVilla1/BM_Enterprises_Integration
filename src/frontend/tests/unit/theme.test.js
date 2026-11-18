// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: theme.test conventions =====
// Purpose: Preserve this module while standardizing source formatting.
// Inputs: Existing module configuration or test fixtures.
// Returns: Existing exports or regression assertions.
// Flow: Apply the documented frontend conventions without changing behavior.
// AI MODIFIED: Formatting consistency.

import { describe, expect, it } from 'vitest'
import { applyTheme, nextTheme, readStoredTheme, storeTheme } from '../../src/shared/utils/theme'

const memoryStorage = () => {
  const values = new Map()
  return {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value),
  }
}

describe('theme', () => {
  it('toggles between dark and light', () => {
    expect(nextTheme('bm-dark')).toBe('bm-light')
    expect(nextTheme('bm-light')).toBe('bm-dark')
  })

  it('defaults to dark and remembers the light choice', () => {
    const storage = memoryStorage()
    expect(readStoredTheme(storage)).toBe('bm-dark')
    storeTheme('bm-light', storage)
    expect(readStoredTheme(storage)).toBe('bm-light')
  })

  it('survives unavailable or broken storage', () => {
    const broken = {
      getItem: () => {
        throw new Error('blocked')
      },
      setItem: () => {
        throw new Error('blocked')
      },
    }
    expect(readStoredTheme(broken)).toBe('bm-dark')
    expect(() => storeTheme('bm-light', broken)).not.toThrow()
    expect(readStoredTheme(undefined)).toBe('bm-dark')
  })

  it('applies the theme to the root element', () => {
    const calls = []
    applyTheme('bm-light', { setAttribute: (name, value) => calls.push([name, value]) })
    expect(calls).toEqual([['data-theme', 'bm-light']])
  })
})
