// ===== AI GENERATED: financial_workspace_stores =====
// Purpose: Separate account-scoped stores for expenses, payroll, advances, billing and reports.
// Inputs: Hook-controlled query state and retry identities.
// Returns: Domain stores; no API calls or financial rules.
// Flow: Clear prior account data before loading; keep failed-command keys for safe retries.

import { create } from 'zustand'

/** @returns {Object} An independent financial workspace store. */
function createFinanceStore() {
  return create((set) => ({
    ownerId: null,
    snapshot: null,
    loadState: 'idle',
    failure: null,
    retryKeys: {},
    offset: 0,
    beginLoad: (ownerId, offset) =>
      set((state) => ({
        ownerId,
        offset,
        loadState: 'loading',
        failure: null,
        snapshot: state.ownerId === ownerId ? state.snapshot : null,
        retryKeys: state.ownerId === ownerId ? state.retryKeys : {},
      })),
    finishLoad: (snapshot) => set({ snapshot, loadState: 'ready', failure: null }),
    failLoad: (failure) => set({ loadState: 'failed', failure, snapshot: null }),
    rememberRetry: (identity, retryKey) =>
      set((state) => ({ retryKeys: { ...state.retryKeys, [identity]: retryKey } })),
    forgetRetry: (identity) =>
      set((state) => ({
        retryKeys: Object.fromEntries(
          Object.entries(state.retryKeys).filter(([key]) => key !== identity),
        ),
      })),
  }))
}

export const useExpenseFinanceStore = createFinanceStore()
export const usePayrollFinanceStore = createFinanceStore()
export const useAdvanceFinanceStore = createFinanceStore()
export const useBillingFinanceStore = createFinanceStore()
export const useReportsFinanceStore = createFinanceStore()
