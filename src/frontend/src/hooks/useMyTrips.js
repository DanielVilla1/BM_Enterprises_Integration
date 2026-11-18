// ===== AI GENERATED: useMyTrips =====
// Purpose: A crew member's trips, progress actions, OR upload and receipt confirmation
// Inputs: none
// Returns: state plus progress, upload, confirm and open-document actions
// Flow:
// 1. Load /trips/assigned on mount
// 2. Confirmation keeps one Idempotency-Key per trip until it succeeds, so retries are safe
// 3. Opening a document fetches a short-lived signed URL on demand

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { useCallback, useEffect, useRef } from 'react'
import { confirmReceipt, fetchOrDocumentUrl, uploadOrDocument } from '../services/orService'
import { listAssignedTrips, runTripAction } from '../services/tripService'
import { loadIntoStore } from '../shared/services/collectionLoader'
import { useTripStore } from '../store/tripStore'
import { useRecordActions } from './useRecordActions'

/**
 * @function useMyTrips
 * @description Crew trips and actions.
 * @returns {Object}
 */
export function useMyTrips() {
  const loadState = useTripStore((state) => state.loadState)
  const trips = useTripStore((state) => state.items)
  const failure = useTripStore((state) => state.failure)
  const reloadTrips = useCallback(() => loadIntoStore(useTripStore, listAssignedTrips), [])
  const { runAction, actionFailure, isBusy } = useRecordActions(reloadTrips)
  const confirmationKeys = useRef(new Map())

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
    submitUpload: (tripIdentifier, imageFile, documentKind) =>
      runAction(() => uploadOrDocument(tripIdentifier, imageFile, documentKind)),
    submitConfirmation: async (tripIdentifier, receivedAtIso) => {
      const keys = confirmationKeys.current
      const idempotencyKey = keys.get(tripIdentifier) ?? crypto.randomUUID()
      keys.set(tripIdentifier, idempotencyKey)
      const confirmed = await runAction(() =>
        confirmReceipt(tripIdentifier, receivedAtIso, idempotencyKey),
      )
      if (confirmed) keys.delete(tripIdentifier)
      return confirmed
    },
    openDocument: (tripIdentifier, documentIdentifier) =>
      runAction(async () => {
        const signed = await fetchOrDocumentUrl(tripIdentifier, documentIdentifier)
        window.open(signed.url, '_blank', 'noopener')
      }),
  }
}
