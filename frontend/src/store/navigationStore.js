// ===== AI GENERATED: navigationStore =====
// Purpose: Which page is open
// Inputs: selections from the navigation
// Returns: { activePage, openPage }
// Flow:
// 1. null means "no choice yet": the app opens the user's first allowed page

import { create } from 'zustand'

export const useNavigationStore = create((set) => ({
  activePage: null,
  openPage: (pageKey) => set({ activePage: pageKey }),
}))
