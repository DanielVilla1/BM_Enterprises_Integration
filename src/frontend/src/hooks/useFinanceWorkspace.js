// ===== AI GENERATED: useFinanceWorkspace =====
// Purpose: Account-scoped finance queries and safe command orchestration.
// Inputs: Domain section and authenticated employee identifier.
// Returns: Workspace, paging, errors and command callback.
// Flow: Abort stale loads; retain retry keys after ambiguous outcomes; refresh after commands.

import { useCallback, useEffect, useRef, useState } from 'react'
import { readFinanceWorkspace, submitFinanceCommand } from '../services/financeService'
import {
  useAdvanceFinanceStore,
  useBillingFinanceStore,
  useExpenseFinanceStore,
  usePayrollFinanceStore,
  useReportsFinanceStore,
} from '../store/financeStores'

const DOMAIN_STORES = {
  expenses: useExpenseFinanceStore,
  payroll: usePayrollFinanceStore,
  advances: useAdvanceFinanceStore,
  billing: useBillingFinanceStore,
  reports: useReportsFinanceStore,
}

/**
 * @param {string} section Domain section.
 * @param {string} employeeId Verified employee identifier.
 * @returns {Object} Authorized query state and actions.
 */
export function useFinanceWorkspace(section, employeeId) {
  const useDomainStore = DOMAIN_STORES[section]
  const workspaceState = useDomainStore()
  const [offset, setOffset] = useState(0)
  const [isBusy, setIsBusy] = useState(false)
  const [actionFailure, setActionFailure] = useState(null)
  const [notice, setNotice] = useState('')
  const pending = useRef(false)
  const active = useRef(false)
  const reload = useCallback(
    async (signal) => {
      useDomainStore.getState().beginLoad(employeeId, offset)
      try {
        const snapshot = await readFinanceWorkspace(section, offset, signal)
        if (!signal?.aborted && useDomainStore.getState().ownerId === employeeId)
          useDomainStore.getState().finishLoad(snapshot)
        return snapshot
      } catch (failure) {
        if (!signal?.aborted && useDomainStore.getState().ownerId === employeeId)
          useDomainStore.getState().failLoad(failure)
        throw failure
      }
    },
    [employeeId, offset, section, useDomainStore],
  )

  useEffect(() => {
    active.current = true
    const controller = new AbortController()
    reload(controller.signal).catch(() => {})
    return () => {
      active.current = false
      controller.abort()
    }
  }, [reload])

  const runCommand = useCallback(
    async (path, payload = {}) => {
      if (pending.current) return false
      pending.current = true
      setIsBusy(true)
      setActionFailure(null)
      setNotice('')
      const identity = `${employeeId}:${path}:${JSON.stringify(payload)}`
      const retryKey = useDomainStore.getState().retryKeys[identity] ?? crypto.randomUUID()
      useDomainStore.getState().rememberRetry(identity, retryKey)
      try {
        const result = await submitFinanceCommand(path, payload, retryKey)
        if (!active.current) return false
        await reload()
        if (!active.current) return false
        useDomainStore.getState().forgetRetry(identity)
        setNotice(
          result.state === 'HELD'
            ? 'Saved on hold. An independent financial review is required.'
            : 'Saved successfully.',
        )
        return true
      } catch (failure) {
        setActionFailure(failure)
        return false
      } finally {
        pending.current = false
        setIsBusy(false)
      }
    },
    [employeeId, reload, useDomainStore],
  )

  return {
    ...workspaceState,
    snapshot: workspaceState.ownerId === employeeId ? workspaceState.snapshot : null,
    isBusy,
    actionFailure,
    notice,
    runCommand,
    refresh: () => reload().catch(() => {}),
    previousPage: () => setOffset(Math.max(0, offset - 50)),
    nextPage: () => setOffset(offset + 50),
    offset,
  }
}
