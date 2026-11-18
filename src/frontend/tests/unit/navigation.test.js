// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: navigation.test conventions =====
// Purpose: Preserve this module while standardizing source formatting.
// Inputs: Existing module configuration or test fixtures.
// Returns: Existing exports or regression assertions.
// Flow: Apply the documented frontend conventions without changing behavior.
// AI MODIFIED: Formatting consistency.

import { describe, expect, it } from 'vitest'
import {
  groupNavigation,
  hasWriteAccess,
  resolveActivePage,
  visibleNavigation,
} from '../../src/shared/utils/navigation'

const pageKeys = (capabilities) => visibleNavigation(capabilities).map((page) => page.key)

describe('visibleNavigation', () => {
  it('shows only the account page when nothing is granted', () => {
    expect(pageKeys({})).toEqual(['account'])
  })

  it('gives a dispatcher the operations pages plus the preview finance and report pages', () => {
    const keys = pageKeys({
      'dispatch.assign': 'FULL',
      'delivery_order.manage': 'FULL',
      'truck.manage': 'VIEW',
      'trip.assignment_view': 'VIEW',
      'expense.view': 'FULL',
      'report.view': 'FULL',
    })
    expect(keys).toEqual([
      'dashboard',
      'dispatch',
      'orders',
      'clients',
      'fleet',
      'expenses',
      'reports',
      'account',
    ])
  })

  it('shows My trips only at the OWN level (crew members)', () => {
    expect(pageKeys({ 'trip.assignment_view': 'OWN' })).toEqual(['trips', 'account'])
    expect(pageKeys({ 'trip.assignment_view': 'VIEW' })).toEqual(['account'])
  })

  it('lets limited employee viewers reach license actions without account management', () => {
    expect(pageKeys({ 'employee.manage': 'FULL' })).toContain('people')
    expect(pageKeys({ 'employee.manage': 'LTD' })).toContain('people')
    expect(pageKeys({ 'employee.manage': 'OWN' })).not.toContain('people')
  })

  it('shows audit log and permissions to the Owner capability only', () => {
    const keys = pageKeys({ 'audit_user.manage': 'FULL' })
    expect(keys).toEqual(['audit', 'permissions', 'account'])
  })

  it('shows ownership-scoped reports to crew and accepts any matching capability', () => {
    expect(pageKeys({ 'report.view': 'OWN' })).toContain('reports')
    expect(pageKeys({ 'payroll.view': 'OWN' })).toContain('payroll')
    expect(pageKeys({ 'cash_advance.view': 'OWN' })).toContain('advances')
  })

  it('hides fleet from a role without truck access', () => {
    expect(pageKeys({ 'delivery_order.manage': 'VIEW' })).not.toContain('fleet')
  })

  it('shows implemented finance and report pages without Soon indicators', () => {
    const preview = visibleNavigation({ 'billing.manage': 'FULL', 'report.view': 'FULL' }).filter(
      (page) => page.preview,
    )
    expect(preview).toEqual([])
  })
})

describe('groupNavigation', () => {
  it('groups pages by sidebar section in order', () => {
    const groups = groupNavigation(
      visibleNavigation({ 'dispatch.assign': 'FULL', 'employee.manage': 'FULL' }),
    )
    expect(groups.map((entry) => entry.group)).toEqual(['Operations', 'Administration', 'Account'])
    expect(groups[0].items.map((page) => page.key)).toEqual(['dashboard', 'dispatch'])
  })
})

describe('resolveActivePage', () => {
  it('keeps an allowed page and otherwise falls back to the first one', () => {
    const items = visibleNavigation({ 'dispatch.assign': 'FULL' })
    expect(resolveActivePage(items, 'dispatch')).toBe('dispatch')
    expect(resolveActivePage(items, 'people')).toBe('dashboard')
    expect(resolveActivePage(items, null)).toBe('dashboard')
  })
})

describe('hasWriteAccess', () => {
  it('is true only for the FULL level', () => {
    expect(hasWriteAccess({ 'truck.manage': 'FULL' }, 'truck.manage')).toBe(true)
    expect(hasWriteAccess({ 'truck.manage': 'VIEW' }, 'truck.manage')).toBe(false)
    expect(hasWriteAccess({}, 'truck.manage')).toBe(false)
  })
})
