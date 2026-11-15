// ===== AI GENERATED: useTrucks =====
// Purpose: Trucks for the fleet screen
// Inputs: none
// Returns: store state plus create / maintenance actions
// Flow:
// 1. Load trucks on mount into the truck store
// 2. Mutations reload the list

import { useCallback, useEffect } from 'react'
import {
  completeMaintenance,
  createTruck,
  listMaintenance,
  listTrucks,
  startMaintenance,
  updateTruck,
} from '../services/truckService'
import { loadIntoStore } from '../shared/utils/collectionLoader'
import { useTruckStore } from '../store/truckStore'
import { useRecordActions } from './useRecordActions'

/**
 * @function useTrucks
 * @description Trucks list and actions.
 * @returns {Object}
 */
export function useTrucks() {
  const loadState = useTruckStore((state) => state.loadState)
  const items = useTruckStore((state) => state.items)
  const failure = useTruckStore((state) => state.failure)
  const reloadTrucks = useCallback(() => loadIntoStore(useTruckStore, listTrucks), [])
  const { runAction, actionFailure, isBusy } = useRecordActions(reloadTrucks)

  const loadMaintenance = useCallback(async (truckIdentifier) => {
    try {
      return { records: await listMaintenance(truckIdentifier), failure: null }
    } catch (requestFailure) {
      return { records: [], failure: requestFailure }
    }
  }, [])

  useEffect(() => {
    reloadTrucks()
  }, [reloadTrucks])

  return {
    loadState,
    trucks: items,
    failure,
    actionFailure,
    isBusy,
    submitTruck: (truckPayload) => runAction(() => createTruck(truckPayload)),
    submitUpdate: (truckIdentifier, changes) => runAction(() => updateTruck(truckIdentifier, changes)),
    loadMaintenance,
    submitMaintenanceStart: (truckIdentifier, maintenanceReason) =>
      runAction(() => startMaintenance(truckIdentifier, maintenanceReason)),
    submitMaintenanceComplete: (truckIdentifier) =>
      runAction(() => completeMaintenance(truckIdentifier)),
  }
}
