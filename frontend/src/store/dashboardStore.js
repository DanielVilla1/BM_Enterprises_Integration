// ===== AI GENERATED: dashboardStore =====
// Purpose: Everything the dashboard summarizes (orders, trips, trucks, resources)
// Inputs: results from useDashboard
// Returns: { loadState, snapshot, failure } and setters
// Flow:
// 1. snapshot is raw API data; numbers are derived in shared/utils/operations

import { create } from 'zustand'

const EMPTY_SNAPSHOT = {
  orders: [],
  trips: [],
  trucks: [],
  resources: { trucks: [], drivers: [], helpers: [] },
}

export const useDashboardStore = create((set) => ({
  loadState: 'idle',
  snapshot: EMPTY_SNAPSHOT,
  failure: null,
  markLoading: () => set({ loadState: 'loading', failure: null }),
  markReady: (snapshot) => set({ loadState: 'ready', snapshot, failure: null }),
  markFailed: (failure) => set({ loadState: 'failed', failure }),
}))
