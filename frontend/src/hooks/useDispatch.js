// ===== AI GENERATED: useDispatch =====
// Purpose: Trips, resource availability and dispatcher actions
// Inputs: none
// Returns: state plus assign, clear, cancel and fail actions
// Flow:
// 1. Load trips and resources on mount
// 2. Every mutation reloads both so blocked resources update

import { useCallback, useEffect } from 'react'
import { correctConfirmation, fetchOrDocumentUrl } from '../services/orService'
import {
  assignTrip,
  closeTrip,
  fetchDispatchResources,
  listTrips,
  runTripAction,
} from '../services/tripService'
import { loadIntoStore } from '../shared/utils/collectionLoader'
import { useDispatchResourceStore } from '../store/dispatchResourceStore'
import { useTripStore } from '../store/tripStore'
import { useRecordActions } from './useRecordActions'

/**
 * @function useDispatch
 * @description Dispatcher state and actions.
 * @returns {Object}
 */
export function useDispatch() {
  const loadState = useTripStore((state) => state.loadState)
  const trips = useTripStore((state) => state.items)
  const failure = useTripStore((state) => state.failure)
  const resources = useDispatchResourceStore((state) => state.resources)

  const reloadAll = useCallback(async () => {
    const { markLoading, markReady, markFailed } = useDispatchResourceStore.getState()
    markLoading()
    try {
      markReady(await fetchDispatchResources())
    } catch (requestFailure) {
      markFailed(requestFailure)
    }
    await loadIntoStore(useTripStore, listTrips)
  }, [])
  const { runAction, actionFailure, isBusy } = useRecordActions(reloadAll)

  useEffect(() => {
    reloadAll()
  }, [reloadAll])

  return {
    loadState,
    trips,
    failure,
    resources,
    actionFailure,
    isBusy,
    submitAssignment: (orderIdentifier, assignment) =>
      runAction(() => assignTrip(orderIdentifier, assignment)),
    submitClearance: (tripIdentifier) => runAction(() => runTripAction(tripIdentifier, 'clear-dispatch')),
    submitClose: (tripIdentifier, closeAction, closeReason) =>
      runAction(() => closeTrip(tripIdentifier, closeAction, closeReason)),
    submitCorrection: (tripIdentifier, correctionReason) =>
      runAction(() => correctConfirmation(tripIdentifier, correctionReason)),
    openDocument: (tripIdentifier, documentIdentifier) =>
      runAction(async () => {
        const signed = await fetchOrDocumentUrl(tripIdentifier, documentIdentifier)
        window.open(signed.url, '_blank', 'noopener')
      }),
  }
}
