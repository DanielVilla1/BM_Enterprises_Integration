// ===== AI GENERATED: permissionStore =====
// Purpose: The permission matrix grants for the Owner's table
// Inputs: results from usePermissionMatrix
// Returns: { loadState, grants, failure } and setters
// Flow:
// 1. Read-only view of what the backend enforces

import { create } from 'zustand'

export const usePermissionStore = create((set) => ({
  loadState: 'idle',
  grants: [],
  failure: null,
  markLoading: () => set({ loadState: 'loading', failure: null }),
  markReady: (grants) => set({ loadState: 'ready', grants, failure: null }),
  markFailed: (failure) => set({ loadState: 'failed', failure }),
}))
