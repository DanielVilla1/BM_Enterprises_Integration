// ===== AI GENERATED: useClients =====
// Purpose: Clients for the clients screen and the order form
// Inputs: none
// Returns: store state plus a create action
// Flow:
// 1. Load clients on mount into the client store
// 2. Create reloads the list

import { useCallback, useEffect } from 'react'
import { createClient, listClients } from '../services/clientService'
import { loadIntoStore } from '../shared/utils/collectionLoader'
import { useClientStore } from '../store/clientStore'
import { useRecordActions } from './useRecordActions'

/**
 * @function useClients
 * @description Clients list and actions.
 * @returns {Object}
 */
export function useClients() {
  const loadState = useClientStore((state) => state.loadState)
  const items = useClientStore((state) => state.items)
  const failure = useClientStore((state) => state.failure)
  const reloadClients = useCallback(() => loadIntoStore(useClientStore, listClients), [])
  const { runAction, actionFailure, isBusy } = useRecordActions(reloadClients)

  useEffect(() => {
    reloadClients()
  }, [reloadClients])

  return {
    loadState,
    clients: items,
    failure,
    actionFailure,
    isBusy,
    submitClient: (clientPayload) => runAction(() => createClient(clientPayload)),
  }
}
