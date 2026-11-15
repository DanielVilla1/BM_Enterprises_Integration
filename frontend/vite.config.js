// ===== AI GENERATED: createDevelopmentConfiguration =====
// Purpose: Serve the frontend and proxy API calls through one development origin
// Inputs: Public frontend URL from Vite environment variables
// Returns: React/Tailwind plugins, an exact hostname allowlist and the API proxy
// Flow:
// 1. Load public-only settings and allow the configured sharing hostname
// 2. Forward /api/v1 requests to the local FastAPI server
// AI MODIFIED: Keep localhost and public demo requests on the same API path.
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

/**
 * @function createDevelopmentConfiguration
 * @description Configure the development hostname and same-origin API proxy.
 * @param {import('vite').ConfigEnv} configurationEnvironment
 * @returns {import('vite').UserConfig}
 */
function createDevelopmentConfiguration({ mode }) {
  const environment = loadEnv(mode, '.', 'VITE_')
  const publicAddress = environment.VITE_PUBLIC_FRONTEND_URL ?? ''
  const allowedHostnames = publicAddress ? [new URL(publicAddress).hostname] : []
  return {
    plugins: [react(), tailwindcss()],
    server: {
      allowedHosts: allowedHostnames,
      proxy: {
        '/api/v1': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
      },
    },
  }
}

export default defineConfig(createDevelopmentConfiguration)
