// ===== AI GENERATED: design_preview_main =====
// Purpose: Entry point of the design preview (dev only, not part of the production build)
// Inputs: #root element in preview.html
// Returns: the PreviewApp rendered with sample data
// Flow:
// 1. Load the same Tailwind + daisyUI styles as the real app and apply the saved theme
// 2. Render PreviewApp; no Clerk, no backend

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '../src/index.css'
import { applyTheme, readStoredTheme } from '../src/shared/utils/theme'
import { PreviewApp } from './PreviewApp.jsx'

applyTheme(readStoredTheme())

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <PreviewApp />
  </StrictMode>,
)
