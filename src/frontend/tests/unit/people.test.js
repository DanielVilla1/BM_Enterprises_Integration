// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: people.test conventions =====
// Purpose: Preserve this module while standardizing source formatting.
// Inputs: Existing module configuration or test fixtures.
// Returns: Existing exports or regression assertions.
// Flow: Apply the documented frontend conventions without changing behavior.
// AI MODIFIED: Formatting consistency.

import { describe, expect, it } from 'vitest'
import {
  describeAuditAction,
  filterAuditRecords,
  filterEmployees,
} from '../../src/shared/utils/people'

const employees = [
  {
    employee_id: 'e1',
    full_name: 'Juan Santos',
    email: 'juan@example.com',
    is_active: true,
    role_codes: ['DRIVER'],
  },
  {
    employee_id: 'e2',
    full_name: 'Alma Accounting',
    email: 'alma@example.com',
    is_active: false,
    role_codes: ['ACCOUNTING'],
  },
  {
    employee_id: 'e3',
    full_name: 'Hana Hernandez',
    email: 'hana@example.com',
    is_active: true,
    role_codes: ['HR_PAYROLL'],
  },
]

describe('filterEmployees', () => {
  it('supports limited employee records without exposing missing private fields', () => {
    const limited = [{ employee_id: 'driver-id', full_name: 'Limited Driver', is_active: true }]
    expect(filterEmployees(limited, 'active', 'driver')).toEqual(limited)
    expect(filterEmployees(limited, 'all', 'accounting')).toEqual([])
  })
  it('filters by status tab', () => {
    expect(filterEmployees(employees, 'active', '')).toHaveLength(2)
    expect(filterEmployees(employees, 'inactive', '').map((entry) => entry.employee_id)).toEqual([
      'e2',
    ])
    expect(filterEmployees(employees, 'all', '')).toHaveLength(3)
  })

  it('searches name, email and readable role names', () => {
    expect(filterEmployees(employees, 'all', 'juan')).toHaveLength(1)
    expect(filterEmployees(employees, 'all', 'alma@')).toHaveLength(1)
    expect(filterEmployees(employees, 'all', 'hr &')).toHaveLength(1)
    expect(filterEmployees(employees, 'all', 'driver')).toHaveLength(1)
  })
})

describe('describeAuditAction', () => {
  it('uses sentences for known actions and humanizes unknown ones', () => {
    expect(describeAuditAction('trip.receipt_confirmed')).toBe('Receipt confirmed, trip completed')
    expect(describeAuditAction('brand.new_action')).toBe('Brand new action')
  })
})

describe('filterAuditRecords', () => {
  const records = [
    { action: 'trip.created', entity_type: 'trip', trace_id: 'abc123' },
    { action: 'client.created', entity_type: 'client', trace_id: 'def456' },
  ]

  it('searches the readable action, entity and trace id', () => {
    expect(filterAuditRecords(records, 'assigned')).toHaveLength(1)
    expect(filterAuditRecords(records, 'client')).toHaveLength(1)
    expect(filterAuditRecords(records, 'def4')).toHaveLength(1)
    expect(filterAuditRecords(records, '')).toHaveLength(2)
  })
})
