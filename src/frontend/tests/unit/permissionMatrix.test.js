// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: permissionMatrix.test conventions =====
// Purpose: Preserve this module while standardizing source formatting.
// Inputs: Existing module configuration or test fixtures.
// Returns: Existing exports or regression assertions.
// Flow: Apply the documented frontend conventions without changing behavior.
// AI MODIFIED: Formatting consistency.

import { describe, expect, it } from 'vitest'
import {
  ROLE_ORDER,
  buildMatrix,
  groupCapabilities,
  roleLabel,
} from '../../src/shared/utils/permissionMatrix'

describe('buildMatrix', () => {
  const grants = [
    { capability: 'truck.manage', role_code: 'OWNER', access_level: 'FULL' },
    { capability: 'truck.manage', role_code: 'DISPATCHER', access_level: 'VIEW' },
    { capability: 'dispatch.assign', role_code: 'OWNER', access_level: 'FULL' },
    { capability: 'delivery_order.manage', role_code: 'DISPATCHER', access_level: 'FULL' },
  ]

  it('pivots grants into one row per capability with a cell for every role', () => {
    const matrix = buildMatrix(grants)
    expect(matrix.roles).toEqual(ROLE_ORDER)
    const truck = matrix.rows.find((row) => row.capability === 'truck.manage')
    expect(truck.cells.OWNER).toBe('FULL')
    expect(truck.cells.DISPATCHER).toBe('VIEW')
    expect(truck.cells.DRIVER).toBeNull()
    expect(Object.keys(truck.cells)).toEqual(ROLE_ORDER)
  })

  it('sorts rows by group then capability and labels them', () => {
    const matrix = buildMatrix(grants)
    expect(matrix.rows.map((row) => row.group)).toEqual(['Dispatch', 'Fleet', 'Orders'])
    expect(matrix.rows[0].label).toBe('Dispatch assign')
  })
})

describe('groupCapabilities', () => {
  it('groups a capability map by domain', () => {
    const groups = groupCapabilities({
      'truck.manage': 'FULL',
      'delivery_order.manage': 'VIEW',
      'trip.progress': 'OWN',
      'trip.assignment_view': 'OWN',
    })
    expect(groups.map((entry) => entry.group)).toEqual(['Fleet', 'Orders', 'Trips'])
    expect(groups[2].entries.map((entry) => entry.capability)).toEqual([
      'trip.assignment_view',
      'trip.progress',
    ])
    expect(groups[0].entries[0]).toEqual({
      capability: 'truck.manage',
      label: 'Truck manage',
      level: 'FULL',
    })
  })
})

describe('roleLabel', () => {
  it('names roles and falls back for unknown ones', () => {
    expect(roleLabel('HR_PAYROLL')).toBe('HR & Payroll')
    expect(roleLabel('NEW_ROLE')).toBe('New role')
  })
})
