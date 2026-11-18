// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: workflow rendering regression tests =====
// Purpose: Verify restricted API projections render without privileged controls
// Inputs: Fake limited employee and assigned-trip responses
// Returns: Assertions on server-rendered React markup
// Flow: Render the real screens; check hidden fields and conditional actions.

import { renderToStaticMarkup } from 'react-dom/server'
import { describe, expect, it } from 'vitest'
import { MyTripsPanel } from '../../src/components/trips/MyTripsPanel'
import { PeoplePanel } from '../../src/components/administration/PeoplePanel'

const assignedTrip = {
  trip_id: 'trip-one',
  driver_id: 'driver-one',
  helper_ids: ['helper-one'],
  status: 'OR_UPLOADED',
  scheduled_date: '2026-11-18',
  load_tons: 20,
  pickup_location: 'Example plant',
  delivery_location: 'Example depot',
  documents: [
    { document_id: 'document-one', kind: 'SIGNED_OR', uploaded_at: '2026-11-18T00:00:00Z' },
  ],
}

describe('role-specific workflow screens', () => {
  it('renders limited employee records without claiming missing account or role information', () => {
    const markup = renderToStaticMarkup(
      <PeoplePanel
        loadState="ready"
        employees={[{ employee_id: 'employee-one', full_name: 'Example Driver', is_active: true }]}
        permissions={{
          canEdit: false,
          canManageAccounts: false,
          canActivate: false,
          canViewLicense: true,
          canEditLicense: true,
        }}
        handlers={{}}
      />,
    )
    expect(markup).toContain('Example Driver')
    expect(markup).toContain('Driver license')
    expect(markup).not.toContain('Add employee')
    expect(markup).not.toContain('No sign-in yet')
    expect(markup).not.toContain('No role yet')
  })

  it('does not render disabled helper upload, document or confirmation controls', () => {
    const markup = renderToStaticMarkup(
      <MyTripsPanel
        loadState="ready"
        trips={[assignedTrip]}
        employeeIdentifier="helper-one"
        capabilities={{}}
      />,
    )
    expect(markup).not.toContain('type="file"')
    expect(markup).not.toContain('Confirm receipt')
    expect(markup).not.toContain('Signed OR</div>')
  })

  it('renders upload and receipt actions for the assigned driver with backend grants', () => {
    const markup = renderToStaticMarkup(
      <MyTripsPanel
        loadState="ready"
        trips={[assignedTrip]}
        employeeIdentifier="driver-one"
        capabilities={{ 'or.upload': 'OWN', 'or.view_files': 'OWN', 'or.confirm_receipt': 'OWN' }}
      />,
    )
    expect(markup).toContain('type="file"')
    expect(markup).toContain('Confirm receipt')
    expect(markup).toContain('Signed OR')
  })
})
