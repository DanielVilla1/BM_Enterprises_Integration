// ===== AI GENERATED: httpClient =====
// Purpose: Single axios instance for the /api/v1 contract
// Inputs: VITE_API_BASE_URL, a registered session-token provider
// Returns: apiClient with bearer auth and normalized errors
// Flow:
// 1. Attach the Clerk session token to every request
// 2. Reject with a normalized ApiFailure, never a raw network error

import axios from 'axios'
import { normalizeApiError } from '../utils/problemDetails'

const API_ORIGIN = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const REQUEST_TIMEOUT_MS = 10000

// Wake a sleeping demo API before requesting a short-lived sign-in token.
// This client is for the public health endpoint and has no token interceptor.
const startupClient = axios.create({
  baseURL: `${API_ORIGIN}/api/v1`,
  timeout: 90000,
})

/** @returns {Promise<void>} Wait for API startup without replaying business commands. */
export async function waitForApiStartup() {
  try {
    const response = await startupClient.get('/health')
    if (response.data?.status !== 'ok') {
      throw { response: { status: response.status, data: null } }
    }
  } catch (failure) {
    throw normalizeApiError(failure)
  }
}

/** @type {function(): Promise<string|null>} */
let sessionTokenProvider = async () => null

/**
 * @function registerSessionTokenProvider
 * @description Register the function that returns the current session token.
 * @param {function(): Promise<string|null>} providerFunction
 * @returns {void}
 */
export function registerSessionTokenProvider(providerFunction) {
  sessionTokenProvider = providerFunction
}

export const apiClient = axios.create({
  baseURL: `${API_ORIGIN}/api/v1`,
  timeout: REQUEST_TIMEOUT_MS,
})

apiClient.interceptors.request.use(async (requestConfig) => {
  const sessionToken = await sessionTokenProvider()
  if (sessionToken) {
    requestConfig.headers.Authorization = `Bearer ${sessionToken}`
  }
  return requestConfig
})

apiClient.interceptors.response.use(
  (response) => response,
  (requestError) => Promise.reject(normalizeApiError(requestError)),
)
