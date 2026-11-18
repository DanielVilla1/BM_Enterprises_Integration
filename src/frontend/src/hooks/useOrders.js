// ===== AI GENERATED: useOrders =====
// Purpose: Delivery orders for the orders screen
// Inputs: none
// Returns: store state plus create / cancel actions
// Flow:
// 1. Load orders on mount into the order store
// 2. Mutations reload the list

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { useCallback, useEffect } from 'react'
import { cancelOrder, createOrder, listOrders, updateOrder } from '../services/orderService'
import { loadIntoStore } from '../shared/services/collectionLoader'
import { useOrderStore } from '../store/orderStore'
import { useRecordActions } from './useRecordActions'

/**
 * @function useOrders
 * @description Orders list and actions.
 * @returns {Object}
 */
export function useOrders() {
  const loadState = useOrderStore((state) => state.loadState)
  const items = useOrderStore((state) => state.items)
  const failure = useOrderStore((state) => state.failure)
  const reloadOrders = useCallback(() => loadIntoStore(useOrderStore, listOrders), [])
  const { runAction, actionFailure, isBusy } = useRecordActions(reloadOrders)

  useEffect(() => {
    reloadOrders()
  }, [reloadOrders])

  return {
    loadState,
    orders: items,
    failure,
    actionFailure,
    isBusy,
    submitOrder: (orderPayload) => runAction(() => createOrder(orderPayload)),
    submitUpdate: (orderIdentifier, changes) =>
      runAction(() => updateOrder(orderIdentifier, changes)),
    submitCancel: (orderIdentifier, cancelReason) =>
      runAction(() => cancelOrder(orderIdentifier, cancelReason)),
  }
}
