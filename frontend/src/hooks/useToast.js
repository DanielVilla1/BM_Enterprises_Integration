// ===== AI GENERATED: useToast =====
// Purpose: A short-lived confirmation message after an action succeeds
// Inputs: none
// Returns: { toast, showToast }
// Flow:
// 1. showToast stores the message and hides it after a few seconds
// 2. The timer is cleared on unmount so nothing updates a closed screen

import { useCallback, useEffect, useRef, useState } from 'react'

const TOAST_DURATION_MILLISECONDS = 3500

/**
 * @function useToast
 * @description Local toast state for a screen.
 * @returns {{toast: {message: string, tone: string}|null, showToast: function(string, string=): void}}
 */
export function useToast() {
  const [toast, setToast] = useState(null)
  const timerReference = useRef(null)

  useEffect(() => () => clearTimeout(timerReference.current), [])

  const showToast = useCallback((message, tone = 'success') => {
    clearTimeout(timerReference.current)
    setToast({ message, tone })
    timerReference.current = setTimeout(() => setToast(null), TOAST_DURATION_MILLISECONDS)
  }, [])

  return { toast, showToast }
}
