// ===== AI GENERATED: accountStore =====
// Purpose: Zustand store holding the backend-confirmed account
// Inputs: results pushed by the useCurrentAccount hook
// Returns: explicit state { loadState, account, failure } and setters
// Flow:
// 1. Roles and capabilities come only from the backend (never the UI)
// 2. No business rules and no API calls live here

import { create } from 'zustand'

export const useAccountStore = create((set) => ({
  loadState: 'idle',
  account: null,
  failure: null,
  markLoading: () => set({ loadState: 'loading', failure: null }),
  markReady: (account) => set({ loadState: 'ready', account, failure: null }),
  markFailed: (failure) => set({ loadState: 'failed', account: null, failure }),
  clearAccount: () => set({ loadState: 'idle', account: null, failure: null }),
}))
