import { describe, expect, it } from 'vitest'
import { hasWriteAccess, visibleNavigation } from './navigation'

describe('visibleNavigation', () => {
  it('shows only the account page when nothing is granted', () => {
    expect(visibleNavigation({}).map((page) => page.key)).toEqual(['account'])
  })

  it('shows orders and clients to a dispatcher and fleet to a view-only truck role', () => {
    const keys = visibleNavigation({
      'delivery_order.manage': 'FULL',
      'truck.manage': 'VIEW',
    }).map((page) => page.key)
    expect(keys).toEqual(['orders', 'clients', 'fleet', 'account'])
  })

  it('hides fleet from a role without truck access', () => {
    const keys = visibleNavigation({ 'delivery_order.manage': 'VIEW' }).map((page) => page.key)
    expect(keys).not.toContain('fleet')
  })
})

describe('hasWriteAccess', () => {
  it('is true only for the FULL level', () => {
    expect(hasWriteAccess({ 'truck.manage': 'FULL' }, 'truck.manage')).toBe(true)
    expect(hasWriteAccess({ 'truck.manage': 'VIEW' }, 'truck.manage')).toBe(false)
    expect(hasWriteAccess({}, 'truck.manage')).toBe(false)
  })
})
