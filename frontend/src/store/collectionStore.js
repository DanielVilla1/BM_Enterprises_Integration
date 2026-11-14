// ===== AI GENERATED: createCollectionStore =====
// Purpose: Factory for per-domain list stores with identical shape
// Inputs: none
// Returns: a Zustand store { loadState, items, failure } with setters
// Flow:
// 1. Each domain (orders, trucks, clients) creates its own instance
// 2. No business rules and no API calls here

import { create } from 'zustand'

/**
 * @function createCollectionStore
 * @description Create an independent collection store for one domain.
 * @returns {Object} Zustand store hook
 */
export function createCollectionStore() {
  return create((set) => ({
    loadState: 'idle',
    items: [],
    failure: null,
    markLoading: () => set({ loadState: 'loading', failure: null }),
    markReady: (items) => set({ loadState: 'ready', items, failure: null }),
    markFailed: (failure) => set({ loadState: 'failed', failure }),
  }))
}
