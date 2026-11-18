// ===== AI GENERATED: useTheme =====
// Purpose: Read and toggle the colour theme
// Inputs: none
// Returns: { theme, toggleTheme }
// Flow:
// 1. Applies the stored theme once on mount
// 2. Toggling is handled by the theme store

import { useEffect } from 'react'
import { applyTheme } from '../shared/utils/theme'
import { useThemeStore } from '../store/themeStore'

/**
 * @function useTheme
 * @description Current theme and a toggle function.
 * @returns {{theme: string, toggleTheme: function(): void}}
 */
export function useTheme() {
  const theme = useThemeStore((state) => state.theme)
  const toggleTheme = useThemeStore((state) => state.toggleTheme)

  useEffect(() => {
    applyTheme(theme)
  }, [theme])

  return { theme, toggleTheme }
}
