// ===== AI GENERATED: main =====
// Purpose: React entry point
// Inputs: #root element
// Returns: mounted app inside the session provider
// Flow:
// 1. Wrap App with the Clerk-backed SessionProvider
// 2. Render in StrictMode

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { SessionProvider } from './shared/services/clerkSessionService'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <SessionProvider>
      <App />
    </SessionProvider>
  </StrictMode>,
)
