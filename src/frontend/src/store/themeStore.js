// ===== AI GENERATED: themeStore =====
// Purpose: The chosen colour theme, remembered between visits
// Inputs: toggles from the shell
// Returns: { theme, toggleTheme }
// Flow:
// 1. Starts from the saved preference (dark by default)
// 2. Toggling saves it and applies it to the page

import { create } from 'zustand'
import { applyTheme, nextTheme, readStoredTheme, storeTheme } from '../shared/utils/theme'

export const useThemeStore = create((set, get) => ({
  theme: readStoredTheme(),
  toggleTheme: () => {
    const chosen = nextTheme(get().theme)
    storeTheme(chosen)
    applyTheme(chosen)
    set({ theme: chosen })
  },
}))
