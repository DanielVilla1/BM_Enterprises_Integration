// ===== AI GENERATED: loadIntoStore =====
// Purpose: One way to load a list into a collection store
// Inputs: a Zustand store hook and an async loader function
// Returns: Promise resolved after the store holds the result
// Flow:
// 1. Mark loading, call the loader
// 2. Store items or the normalized failure

// AI MODIFIED: Keep asynchronous loading and store writes in the service layer.

/**
 * @function loadIntoStore
 * @description Fill a collection store from an async loader.
 * @param {Object} storeHook Zustand store created by createCollectionStore
 * @param {function(): Promise<Array<Object>>} loaderFunction Fetches the items
 * @returns {Promise<void>}
 */
export async function loadIntoStore(storeHook, loaderFunction) {
  const { markLoading, markReady, markFailed } = storeHook.getState()
  markLoading()
  try {
    markReady(await loaderFunction())
  } catch (requestFailure) {
    markFailed(requestFailure)
  }
}
