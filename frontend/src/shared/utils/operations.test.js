import { describe, expect, it } from 'vitest'
import {
  attentionItems,
  buildNameLookup,
  countOrdersByTab,
  countTrucksByTab,
  filterOrders,
  filterTrucks,
  groupTripsByStage,
  matchesQuery,
  summarizeOperations,
  summarizeDispatch,
  summarizeTrucks,
} from './operations'

const clients = [
  { client_id: 'c1', name: 'Luzon Steel' },
  { client_id: 'c2', name: 'Visayas Rebar' },
]
const orders = [
  { order_id: 'o1', client_id: 'c1', status: 'PENDING', client_reference: 'PO-1', pickup_location: 'Plant', delivery_location: 'Subic' },
  { order_id: 'o2', client_id: 'c2', status: 'IN_PROGRESS', client_reference: null, pickup_location: 'Mill', delivery_location: 'Cebu' },
  { order_id: 'o3', client_id: 'c1', status: 'COMPLETED', client_reference: null, pickup_location: 'Plant', delivery_location: 'Manila' },
  { order_id: 'o4', client_id: 'c1', status: 'CANCELLED', client_reference: null, pickup_location: 'Plant', delivery_location: 'Manila' },
]

describe('matchesQuery', () => {
  it('matches case-insensitively across values and accepts an empty query', () => {
    expect(matchesQuery(['Luzon Steel', null], 'luz')).toBe(true)
    expect(matchesQuery(['Luzon Steel'], 'cebu')).toBe(false)
    expect(matchesQuery(['x'], '   ')).toBe(true)
  })
})

describe('filterOrders', () => {
  it('filters by status tab', () => {
    expect(filterOrders(orders, clients, 'open', '').map((entry) => entry.order_id)).toEqual(['o1', 'o2'])
    expect(filterOrders(orders, clients, 'completed', '')).toHaveLength(1)
    expect(filterOrders(orders, clients, 'all', '')).toHaveLength(4)
  })

  it('searches by client name, reference and location', () => {
    expect(filterOrders(orders, clients, 'all', 'visayas')).toHaveLength(1)
    expect(filterOrders(orders, clients, 'all', 'po-1')).toHaveLength(1)
    expect(filterOrders(orders, clients, 'all', 'manila')).toHaveLength(2)
  })

  it('counts orders per tab', () => {
    expect(countOrdersByTab(orders)).toEqual({ all: 4, open: 2, completed: 1, cancelled: 1 })
  })
})

describe('summarizeTrucks', () => {
  it('counts active trucks by state and retired ones apart', () => {
    const trucks = [
      { is_active: true, status: 'AVAILABLE' },
      { is_active: true, status: 'ASSIGNED' },
      { is_active: true, status: 'IN_TRANSIT' },
      { is_active: true, status: 'MAINTENANCE' },
      { is_active: false, status: 'AVAILABLE' },
    ]
    expect(summarizeTrucks(trucks)).toEqual({ total: 4, available: 1, working: 2, maintenance: 1, retired: 1 })
  })
})

describe('dispatch board helpers', () => {
  const trips = [
    { trip_id: 't1', status: 'SCHEDULED' },
    { trip_id: 't2', status: 'ACCEPTED' },
    { trip_id: 't3', status: 'IN_TRANSIT' },
    { trip_id: 't4', status: 'OR_UPLOADED' },
    { trip_id: 't5', status: 'DELIVERED_OR_PENDING' },
    { trip_id: 't6', status: 'COMPLETED' },
    { trip_id: 't7', status: 'FAILED' },
  ]

  it('groups trips into board columns', () => {
    const groups = groupTripsByStage(trips)
    expect(groups.scheduled.map((entry) => entry.trip_id)).toEqual(['t1', 't2'])
    expect(groups.road.map((entry) => entry.trip_id)).toEqual(['t3'])
    expect(groups.paperwork.map((entry) => entry.trip_id)).toEqual(['t4', 't5'])
    expect(groups.closed.map((entry) => entry.trip_id)).toEqual(['t6', 't7'])
  })

  it('lists what needs a person to act', () => {
    expect(attentionItems(trips).map((entry) => [entry.trip.trip_id, entry.kind])).toEqual([
      ['t2', 'clear'],
      ['t4', 'receipt'],
      ['t5', 'upload'],
    ])
  })

  it('builds id-to-name lookups for trucks and people', () => {
    const lookup = buildNameLookup({
      trucks: [{ resource_id: 'k1', name: 'ABC 123' }],
      drivers: [{ resource_id: 'd1', name: 'Juan' }],
      helpers: [{ resource_id: 'h1', name: 'Mario' }],
    })
    expect(lookup.trucks.k1).toBe('ABC 123')
    expect(lookup.people).toEqual({ d1: 'Juan', h1: 'Mario' })
  })

  it('summarizes operations for the dashboard', () => {
    const summary = summarizeOperations({
      orders,
      trips,
      trucks: [{ is_active: true, status: 'AVAILABLE' }, { is_active: true, status: 'MAINTENANCE' }],
      resources: {
        trucks: [{ can_receive_assignment: false }],
        drivers: [{ can_receive_assignment: true }],
        helpers: [{ can_receive_assignment: false }],
      },
    })
    expect(summary).toEqual({
      pendingOrders: 1,
      activeTrips: 5,
      inTransit: 1,
      awaitingClearance: 1,
      awaitingReceipt: 2,
      availableTrucks: 1,
      maintenanceTrucks: 1,
      blockedResources: 2,
    })
  })
})

describe('fleet helpers', () => {
  const fleet = [
    { plate_number: 'AAA 111', description: 'Wing van', is_active: true, status: 'AVAILABLE' },
    { plate_number: 'BBB 222', description: null, is_active: true, status: 'IN_TRANSIT' },
    { plate_number: 'CCC 333', description: null, is_active: true, status: 'MAINTENANCE' },
    { plate_number: 'DDD 444', description: null, is_active: false, status: 'AVAILABLE' },
  ]

  it('filters trucks by tab, keeping retired trucks out of the other tabs', () => {
    expect(filterTrucks(fleet, 'available', '')).toHaveLength(1)
    expect(filterTrucks(fleet, 'working', '')).toHaveLength(1)
    expect(filterTrucks(fleet, 'maintenance', '')).toHaveLength(1)
    expect(filterTrucks(fleet, 'retired', '')).toHaveLength(1)
    expect(filterTrucks(fleet, 'all', '')).toHaveLength(3)
  })

  it('searches plate and description and counts tabs', () => {
    expect(filterTrucks(fleet, 'all', 'wing')).toHaveLength(1)
    expect(filterTrucks(fleet, 'all', 'bbb')).toHaveLength(1)
    expect(countTrucksByTab(fleet)).toEqual({ all: 3, available: 1, working: 1, maintenance: 1, retired: 1 })
  })

  it('summarizes the dispatch board', () => {
    const summary = summarizeDispatch(
      [{ status: 'ACCEPTED' }, { status: 'IN_TRANSIT' }, { status: 'CLEARED_FOR_DISPATCH' }, { status: 'OR_UPLOADED' }],
      {
        trucks: [{ can_receive_assignment: false }],
        drivers: [{ can_receive_assignment: true }],
        helpers: [],
      },
    )
    expect(summary).toEqual({ awaitingClearance: 1, onRoad: 2, paperwork: 1, blocked: 1 })
  })
})
