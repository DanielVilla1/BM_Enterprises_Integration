import { describe, expect, it } from 'vitest'
import {
  assignableOrders,
  canConfirmReceipt,
  canCorrectConfirmation,
  canUploadSignedOr,
  canUploadStampedCopy,
  describeDocumentKind,
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

describe('OR actions', () => {
  const trip = (status) => ({ status, driver_id: 'driver-1', helper_ids: ['helper-1'] })

  it('lets crew upload the signed OR only between delivery and confirmation', () => {
    expect(canUploadSignedOr(trip('DELIVERED_OR_PENDING'), 'helper-1')).toBe(true)
    expect(canUploadSignedOr(trip('OR_UPLOADED'), 'driver-1')).toBe(true)
    expect(canUploadSignedOr(trip('IN_TRANSIT'), 'driver-1')).toBe(false)
    expect(canUploadSignedOr(trip('COMPLETED'), 'driver-1')).toBe(false)
    expect(canUploadSignedOr(trip('OR_UPLOADED'), 'someone-else')).toBe(false)
  })

  it('allows the stamped copy after the signed OR', () => {
    expect(canUploadStampedCopy(trip('OR_UPLOADED'), 'helper-1')).toBe(true)
    expect(canUploadStampedCopy(trip('COMPLETED'), 'driver-1')).toBe(true)
    expect(canUploadStampedCopy(trip('DELIVERED_OR_PENDING'), 'driver-1')).toBe(false)
  })

  it('lets only the driver confirm receipt once the OR is uploaded', () => {
    expect(canConfirmReceipt(trip('OR_UPLOADED'), 'driver-1')).toBe(true)
    expect(canConfirmReceipt(trip('OR_UPLOADED'), 'helper-1')).toBe(false)
    expect(canConfirmReceipt(trip('DELIVERED_OR_PENDING'), 'driver-1')).toBe(false)
  })

  it('offers correction only for completed trips', () => {
    expect(canCorrectConfirmation({ status: 'COMPLETED' })).toBe(true)
    expect(canCorrectConfirmation({ status: 'OR_UPLOADED' })).toBe(false)
  })

  it('names document kinds', () => {
    expect(describeDocumentKind('SIGNED_OR')).toBe('Signed OR')
    expect(describeDocumentKind('STAMPED_COPY')).toBe('Stamped copy')
  })
})
