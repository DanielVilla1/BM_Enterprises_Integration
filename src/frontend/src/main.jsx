// ===== AI GENERATED: main =====
// Purpose: React entry point
// Inputs: #root element
// Returns: mounted app inside the session provider
// Flow:
// 1. Apply the saved colour theme before the first paint (no flash)
// 2. Wrap App with the Clerk-backed SessionProvider
// 3. Render in StrictMode

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { SessionProvider } from './shared/services/clerkSessionService'
import { applyTheme, readStoredTheme } from './shared/utils/theme'

applyTheme(readStoredTheme())

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <SessionProvider>
      <App />
    </SessionProvider>
  </StrictMode>,
)
