// ===== AI GENERATED: finance_ui_acceptance =====
// Purpose: Keep finance visibility and form strings consistent with the backend matrix.
// Inputs: Confirmed capability grants, decimal strings and account changes.
// Returns: Regression checks for Owner/HR boundaries and sensitive cached data.
// Flow: Verify menu/read alignment, exact payload values and account isolation.

import { describe, expect, it } from 'vitest'
import {
  expenseLinePayload,
  financePermissions,
  independentReviewer,
} from '../../src/shared/utils/finance'
import { visibleNavigation } from '../../src/shared/utils/navigation'
import { useExpenseFinanceStore } from '../../src/store/financeStores'

describe('financial permissions', () => {
  it('lets Owner enter/review and inspect payroll while reserving payments for HR', () => {
    const permissions = financePermissions({
      'expense.enter': 'FULL',
      'expense.approve': 'FULL',
      'payroll.view': 'FULL',
      'billing.manage': 'VIEW',
      'earning_percentage.set': 'FULL',
      'deduction.record': 'FULL',
    })
    expect(permissions.enter).toBe(true)
    expect(permissions.review).toBe(true)
    expect(permissions.pay).toBe(false)
    expect(permissions.bill).toBe(false)
    expect(permissions.creditAdjustment).toBe(false)
  })

  it('hides a workspace unless its actual read endpoint capability is granted', () => {
    expect(visibleNavigation({ 'expense.enter': 'FULL' }).map((entry) => entry.key)).not.toContain(
      'expenses',
    )
    const pages = visibleNavigation({ 'expense.view': 'FULL', 'billing.manage': 'VIEW' })
    expect(pages.map((entry) => entry.key)).toEqual(['expenses', 'billing', 'account'])
    expect(pages.some((entry) => entry.preview)).toBe(false)
  })

  it('treats every contributor and beneficiary as excluded from independent approval', () => {
    expect(independentReviewer('owner-1', ['driver-1', 'owner-1'])).toBe(false)
    expect(independentReviewer('owner-2', ['driver-1', 'owner-1'])).toBe(true)
  })
})

describe('expense serialization', () => {
  it('retains decimal strings and existing receipt lines without calculating with floats', () => {
    const first = { amount: '5500.01', category: 'FUEL', evidence: 'DEMO-1' }
    const payload = expenseLinePayload(
      {
        trip_id: 'trip-1',
        reason: 'Add actual toll',
        amount: '100.10',
        category: 'TOLL',
        evidence: 'DEMO-2',
      },
      [{ trip_id: 'trip-1', lines: [first] }],
    )
    expect(payload.lines.map((line) => line.amount)).toEqual(['5500.01', '100.10'])
    expect(payload).not.toHaveProperty('trip_id')
    expect(payload.declared_zero).toBe(false)
  })
})

describe('account-scoped financial state', () => {
  it('clears another account’s records and retry keys before loading', () => {
    const state = useExpenseFinanceStore.getState()
    state.beginLoad('account-1', 0)
    state.finishLoad({ expenses: [{ amount: '1000.00' }] })
    state.rememberRetry('account-1:command', 'retry-1')
    state.beginLoad('account-2', 0)
    expect(useExpenseFinanceStore.getState().snapshot).toBeNull()
    expect(useExpenseFinanceStore.getState().retryKeys).toEqual({})
  })

  it('removes financial snapshots after an authorization failure', () => {
    const state = useExpenseFinanceStore.getState()
    state.beginLoad('account-1', 0)
    state.finishLoad({ expenses: [{ amount: '1000.00' }] })
    state.failLoad({ code: 'PERMISSION_DENIED' })
    expect(useExpenseFinanceStore.getState().snapshot).toBeNull()
  })
})
