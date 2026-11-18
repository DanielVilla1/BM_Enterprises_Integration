// ===== AI GENERATED: auditStore =====
// Purpose: Audit log pages, appended as the Owner loads more
// Inputs: pages pushed by the useAuditLog hook
// Returns: { loadState, records, hasMore, failure } and setters
// Flow:
// 1. First page replaces the list; further pages are appended
// 2. hasMore tells the screen whether another page may exist

import { create } from 'zustand'

export const useAuditStore = create((set) => ({
  loadState: 'idle',
  records: [],
  hasMore: false,
  failure: null,
  markLoading: () => set({ loadState: 'loading', failure: null }),
  markReady: (records, hasMore) => set({ loadState: 'ready', records, hasMore, failure: null }),
  appendRecords: (moreRecords, hasMore) =>
    set((state) => ({ loadState: 'ready', records: [...state.records, ...moreRecords], hasMore })),
  markFailed: (failure) => set({ loadState: 'failed', failure }),
}))
