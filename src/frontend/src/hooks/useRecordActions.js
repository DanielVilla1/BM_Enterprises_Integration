// ===== AI GENERATED: useRecordActions =====
// Purpose: Run a mutation, reload the list, and expose the failure to the UI
// Inputs: a reload function
// Returns: { runAction, actionFailure, isBusy }
// Flow:
// 1. Run the mutation, then reload the list
// 2. Keep the normalized failure so the form can show it

import { useCallback, useState } from 'react'

/**
 * @function useRecordActions
 * @description Shared mutation runner for list screens.
 * @param {function(): Promise<void>} reloadFunction Reloads the list after success
 * @returns {{runAction: function(function(): Promise<Object>): Promise<boolean>, actionFailure: Object|null, isBusy: boolean}}
 */
export function useRecordActions(reloadFunction) {
  const [actionFailure, setActionFailure] = useState(null)
  const [isBusy, setIsBusy] = useState(false)

  const runAction = useCallback(
    async (mutationFunction) => {
      setIsBusy(true)
      setActionFailure(null)
      try {
        await mutationFunction()
        await reloadFunction()
        return true
      } catch (requestFailure) {
        setActionFailure(requestFailure)
        return false
      } finally {
        setIsBusy(false)
      }
    },
    [reloadFunction],
  )

  return { runAction, actionFailure, isBusy }
}
