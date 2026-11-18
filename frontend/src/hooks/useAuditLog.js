// ===== AI GENERATED: useAuditLog =====
// Purpose: The Owner's audit log with "load more"
// Inputs: none
// Returns: { loadState, records, hasMore, failure, loadMore }
// Flow:
// 1. Load the first page on mount
// 2. loadMore appends the next page; a short page means there is no more

import { useCallback, useEffect } from 'react'
import { AUDIT_PAGE_SIZE, fetchAuditPage } from '../services/administrationService'
import { useAuditStore } from '../store/auditStore'

/**
 * @function useAuditLog
 * @description Audit log state and paging.
 * @returns {{loadState: string, records: Array<Object>, hasMore: boolean, failure: Object|null, loadMore: function(): Promise<void>}}
 */
export function useAuditLog() {
  const loadState = useAuditStore((state) => state.loadState)
  const records = useAuditStore((state) => state.records)
  const hasMore = useAuditStore((state) => state.hasMore)
  const failure = useAuditStore((state) => state.failure)

  useEffect(() => {
    const { markLoading, markReady, markFailed } = useAuditStore.getState()
    markLoading()
    fetchAuditPage(0)
      .then((page) => markReady(page, page.length === AUDIT_PAGE_SIZE))
      .catch(markFailed)
  }, [])

  const loadMore = useCallback(async () => {
    const { appendRecords, markFailed } = useAuditStore.getState()
    try {
      const page = await fetchAuditPage(useAuditStore.getState().records.length)
      appendRecords(page, page.length === AUDIT_PAGE_SIZE)
    } catch (requestFailure) {
      markFailed(requestFailure)
    }
  }, [])

  return { loadState, records, hasMore, failure, loadMore }
}
