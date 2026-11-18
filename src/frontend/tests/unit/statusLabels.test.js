// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: statusLabels.test conventions =====
// Purpose: Preserve this module while standardizing source formatting.
// Inputs: Existing module configuration or test fixtures.
// Returns: Existing exports or regression assertions.
// Flow: Apply the documented frontend conventions without changing behavior.
// AI MODIFIED: Formatting consistency.

import { describe, expect, it } from 'vitest'
import { describeStatus, humanizeCode, tripStepIndex } from '../../src/shared/utils/statusLabels'

describe('describeStatus', () => {
  it('labels known statuses with a tone', () => {
    expect(describeStatus('trip', 'IN_TRANSIT')).toEqual({ label: 'In transit', tone: 'primary' })
    expect(describeStatus('order', 'PENDING')).toEqual({ label: 'Pending', tone: 'warning' })
    expect(describeStatus('truck', 'MAINTENANCE').tone).toBe('warning')
    expect(describeStatus('license', 'EXPIRED').tone).toBe('error')
  })

  it('falls back to a readable label for unknown codes', () => {
    expect(describeStatus('trip', 'SOMETHING_NEW')).toEqual({
      label: 'Something new',
      tone: 'neutral',
    })
    expect(describeStatus('nothing', 'X_Y')).toEqual({ label: 'X y', tone: 'neutral' })
  })
})

describe('humanizeCode', () => {
  it('handles underscores, dots and empty input', () => {
    expect(humanizeCode('DELIVERED_OR_PENDING')).toBe('Delivered or pending')
    expect(humanizeCode('employee.roles_changed')).toBe('Employee roles changed')
    expect(humanizeCode(null)).toBe('')
  })
})

describe('tripStepIndex', () => {
  it('orders the normal flow and rejects closed-out trips', () => {
    expect(tripStepIndex('SCHEDULED')).toBe(0)
    expect(tripStepIndex('COMPLETED')).toBe(6)
    expect(tripStepIndex('FAILED')).toBe(-1)
    expect(tripStepIndex('CANCELLED')).toBe(-1)
  })
})
