// ===== AI GENERATED: useDashboard =====
// Purpose: Load everything the dashboard summarizes, in parallel
// Inputs: none
// Returns: { loadState, snapshot, failure, reload }
// Flow:
// 1. Orders, trips, trucks and dispatch resources are fetched together
// 2. Any failure shows one error; partial data is never shown as complete

import { useCallback, useEffect } from 'react'
import { listOrders } from '../services/orderService'
import { fetchDispatchResources, listTrips } from '../services/tripService'
import { listTrucks } from '../services/truckService'
import { useDashboardStore } from '../store/dashboardStore'

/**
 * @function useDashboard
 * @description Dashboard data and a reload function.
 * @returns {{loadState: string, snapshot: Object, failure: Object|null, reload: function(): Promise<void>}}
 */
export function useDashboard() {
  const loadState = useDashboardStore((state) => state.loadState)
  const snapshot = useDashboardStore((state) => state.snapshot)
  const failure = useDashboardStore((state) => state.failure)

  const reload = useCallback(async () => {
    const { markLoading, markReady, markFailed } = useDashboardStore.getState()
    markLoading()
    try {
      const [orders, trips, trucks, resources] = await Promise.all([
        listOrders(),
        listTrips(),
        listTrucks(),
        fetchDispatchResources(),
      ])
      markReady({ orders, trips, trucks, resources })
    } catch (requestFailure) {
      markFailed(requestFailure)
    }
  }, [])

  useEffect(() => {
    reload()
  }, [reload])

  return { loadState, snapshot, failure, reload }
}
