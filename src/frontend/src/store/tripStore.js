// ===== AI GENERATED: tripStore =====
// Purpose: Trip list store (dispatcher view and crew view share the shape)
// Inputs: results from useDispatch and useMyTrips
// Returns: useTripStore
// Flow:
// 1. One store per domain; each page reloads it on mount

import { createCollectionStore } from './collectionStore'

export const useTripStore = createCollectionStore()
