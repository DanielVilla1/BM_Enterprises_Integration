import { describe, expect, it } from 'vitest'
import { hasWriteAccess, visibleNavigation } from './navigation'

const pageKeys = (capabilities) => visibleNavigation(capabilities).map((page) => page.key)

describe('visibleNavigation', () => {
  it('shows only the account page when nothing is granted', () => {
    expect(pageKeys({})).toEqual(['account'])
  })

  it('shows dispatch, orders, clients and fleet to a dispatcher', () => {
    const keys = pageKeys({
      'dispatch.assign': 'FULL',
      'delivery_order.manage': 'FULL',
      'truck.manage': 'VIEW',
      'trip.assignment_view': 'VIEW',
    })
    expect(keys).toEqual(['dispatch', 'orders', 'clients', 'fleet', 'account'])
  })

  it('shows My trips only at the OWN level (crew members)', () => {
    expect(pageKeys({ 'trip.assignment_view': 'OWN' })).toEqual(['trips', 'account'])
    expect(pageKeys({ 'trip.assignment_view': 'VIEW' })).toEqual(['account'])
  })

  it('hides fleet from a role without truck access', () => {
    expect(pageKeys({ 'delivery_order.manage': 'VIEW' })).not.toContain('fleet')
  })
})

describe('hasWriteAccess', () => {
  it('is true only for the FULL level', () => {
    expect(hasWriteAccess({ 'truck.manage': 'FULL' }, 'truck.manage')).toBe(true)
    expect(hasWriteAccess({ 'truck.manage': 'VIEW' }, 'truck.manage')).toBe(false)
    expect(hasWriteAccess({}, 'truck.manage')).toBe(false)
  })
})
