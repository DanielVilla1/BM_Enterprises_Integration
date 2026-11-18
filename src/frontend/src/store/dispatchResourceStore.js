// ===== AI GENERATED: dispatchResourceStore =====
// Purpose: Trucks and crew availability for the assignment form
// Inputs: results from useDispatch
// Returns: { loadState, resources, failure } and setters
// Flow:
// 1. Backend decides availability; the store only holds the answer

import { create } from 'zustand'

export const useDispatchResourceStore = create((set) => ({
  loadState: 'idle',
  resources: { trucks: [], drivers: [], helpers: [] },
  failure: null,
  markLoading: () => set({ loadState: 'loading', failure: null }),
  markReady: (resources) => set({ loadState: 'ready', resources, failure: null }),
  markFailed: (failure) => set({ loadState: 'failed', failure }),
}))
