// ===== AI GENERATED: useMyTrips =====
// Purpose: A crew member's trips and the driver's progress actions
// Inputs: none
// Returns: state plus accept, depart and deliver actions
// Flow:
// 1. Load /trips/assigned on mount
// 2. Progress actions reload the list; the backend checks who may act

import { useCallback, useEffect } from 'react'
import { listAssignedTrips, runTripAction } from '../services/tripService'
import { loadIntoStore } from '../shared/utils/collectionLoader'
import { useTripStore } from '../store/tripStore'
import { useRecordActions } from './useRecordActions'

/**
 * @function useMyTrips
 * @description Crew trips and progress actions.
 * @returns {Object}
 */
export function useMyTrips() {
  const loadState = useTripStore((state) => state.loadState)
  const trips = useTripStore((state) => state.items)
  const failure = useTripStore((state) => state.failure)
  const reloadTrips = useCallback(() => loadIntoStore(useTripStore, listAssignedTrips), [])
  const { runAction, actionFailure, isBusy } = useRecordActions(reloadTrips)

  useEffect(() => {
    reloadTrips()
  }, [reloadTrips])

  return {
    loadState,
    trips,
    failure,
    actionFailure,
    isBusy,
    submitProgress: (tripIdentifier, actionName) =>
      runAction(() => runTripAction(tripIdentifier, actionName)),
  }
}
