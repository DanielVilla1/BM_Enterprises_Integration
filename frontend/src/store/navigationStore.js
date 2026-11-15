// ===== AI GENERATED: navigationStore =====
// Purpose: Which page is open
// Inputs: selections from the navigation bar
// Returns: { activePage, openPage }
// Flow:
// 1. Defaults to the account page, which every user may see

import { create } from 'zustand'

export const useNavigationStore = create((set) => ({
  activePage: 'account',
  openPage: (pageKey) => set({ activePage: pageKey }),
}))
