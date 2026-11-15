// ===== AI GENERATED: usePermissionMatrix =====
// Purpose: Load the permission matrix for the Owner's table
// Inputs: none
// Returns: { loadState, grants, failure }
// Flow:
// 1. Load once on mount

import { useEffect } from 'react'
import { fetchPermissionGrants } from '../services/administrationService'
import { usePermissionStore } from '../store/permissionStore'

/**
 * @function usePermissionMatrix
 * @description Permission matrix state.
 * @returns {{loadState: string, grants: Array<Object>, failure: Object|null}}
 */
export function usePermissionMatrix() {
  const loadState = usePermissionStore((state) => state.loadState)
  const grants = usePermissionStore((state) => state.grants)
  const failure = usePermissionStore((state) => state.failure)

  useEffect(() => {
    const { markLoading, markReady, markFailed } = usePermissionStore.getState()
    markLoading()
    fetchPermissionGrants().then(markReady).catch(markFailed)
  }, [])

  return { loadState, grants, failure }
}
