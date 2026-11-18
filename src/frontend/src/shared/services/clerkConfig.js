// ===== AI GENERATED: clerkConfig =====
// Purpose: Public Clerk publishable key from the environment
// Inputs: VITE_CLERK_PUBLISHABLE_KEY
// Returns: CLERK_PUBLISHABLE_KEY (empty string when unset)
// Flow:
// 1. Read the key; it is public by design, secrets never reach the frontend

export const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY ?? ''
