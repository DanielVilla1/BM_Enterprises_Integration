import { describe, expect, it } from 'vitest'
import {
  assignableOrders,
  crewProgressAction,
  describeBlockReason,
  dispatcherActions,
} from './dispatch'

describe('assignableOrders', () => {
  it('drops cancelled and completed orders', () => {
    const orders = [
      { status: 'PENDING' },
      { status: 'PARTIALLY_ASSIGNED' },
      { status: 'IN_PROGRESS' },
      { status: 'CANCELLED' },
      { status: 'COMPLETED' },
    ]
    expect(assignableOrders(orders).map((orderRecord) => orderRecord.status)).toEqual([
      'PENDING',
      'PARTIALLY_ASSIGNED',
      'IN_PROGRESS',
    ])
  })
})

describe('crewProgressAction', () => {
  const trip = (status) => ({ status, driver_id: 'driver-1' })

  it('offers the next step only to the assigned driver', () => {
    expect(crewProgressAction(trip('SCHEDULED'), 'driver-1').name).toBe('accept')
    expect(crewProgressAction(trip('CLEARED_FOR_DISPATCH'), 'driver-1').name).toBe('depart')
    expect(crewProgressAction(trip('IN_TRANSIT'), 'driver-1').name).toBe('deliver')
    expect(crewProgressAction(trip('SCHEDULED'), 'helper-1')).toBeNull()
  })

  it('offers nothing when no step belongs to the driver', () => {
    expect(crewProgressAction(trip('ACCEPTED'), 'driver-1')).toBeNull()
    expect(crewProgressAction(trip('DELIVERED_OR_PENDING'), 'driver-1')).toBeNull()
    expect(crewProgressAction(trip('COMPLETED'), 'driver-1')).toBeNull()
  })
})

describe('dispatcherActions', () => {
  it('allows clearing only accepted trips', () => {
    expect(dispatcherActions({ status: 'ACCEPTED' }).canClear).toBe(true)
    expect(dispatcherActions({ status: 'SCHEDULED' }).canClear).toBe(false)
  })

  it('allows cancelling before departure and failing after it', () => {
    expect(dispatcherActions({ status: 'CLEARED_FOR_DISPATCH' })).toEqual({
      canClear: false,
      canCancel: true,
      canFail: false,
    })
    expect(dispatcherActions({ status: 'IN_TRANSIT' })).toEqual({
      canClear: false,
      canCancel: false,
      canFail: true,
    })
    expect(dispatcherActions({ status: 'COMPLETED' })).toEqual({
      canClear: false,
      canCancel: false,
      canFail: false,
    })
  })
})

describe('describeBlockReason', () => {
  it('maps known codes and falls back for unknown ones', () => {
    expect(describeBlockReason('MAINTENANCE')).toBe('in maintenance')
    expect(describeBlockReason('SOMETHING_NEW')).toBe('unavailable')
    expect(describeBlockReason(null)).toBe('')
  })
})
