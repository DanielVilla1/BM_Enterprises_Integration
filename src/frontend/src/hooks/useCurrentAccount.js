// ===== AI GENERATED: useCurrentAccount =====
// Purpose: Load the signed-in account into the store once on mount
// Inputs: none
// Returns: { loadState, account, failure }
// Flow:
// 1. Mark loading, call accountService
// 2. Store the account or the normalized failure
// 3. Ignore results that arrive after unmount

import { useEffect } from 'react'
import { fetchCurrentAccount } from '../services/accountService'
import { useAccountStore } from '../store/accountStore'

/**
 * @function useCurrentAccount
 * @description Hook that keeps the account store in sync with GET /me.
 * @returns {{loadState: string, account: Object|null, failure: Object|null}}
 */
export function useCurrentAccount() {
  const loadState = useAccountStore((state) => state.loadState)
  const account = useAccountStore((state) => state.account)
  const failure = useAccountStore((state) => state.failure)

  useEffect(() => {
    let isCancelled = false
    const { markLoading, markReady, markFailed, clearAccount } = useAccountStore.getState()
    markLoading()
    fetchCurrentAccount()
      .then((loadedAccount) => {
        if (!isCancelled) markReady(loadedAccount)
      })
      .catch((requestFailure) => {
        if (!isCancelled) markFailed(requestFailure)
      })
    return () => {
      isCancelled = true
      clearAccount()
    }
  }, [])

  return { loadState, account, failure }
}
