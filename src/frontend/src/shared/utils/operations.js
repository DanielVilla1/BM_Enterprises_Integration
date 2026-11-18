// ===== AI GENERATED: operations =====
// Purpose: Pure summaries, filters and groupings for orders, trips and trucks
// Inputs: records already loaded from the API
// Returns: counts, filtered lists, board columns, attention items, name lookups
// Flow:
// 1. Everything here only derives from what the backend returned; no rules are decided here
// 2. Used by the dashboard, the dispatch board and the list screens

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

/** Order status tabs for the orders list. */
export const ORDER_TABS = [
  { key: 'all', label: 'All', statuses: null },
  {
    key: 'open',
    label: 'Open',
    statuses: ['PENDING', 'PARTIALLY_ASSIGNED', 'SCHEDULED', 'IN_PROGRESS'],
  },
  { key: 'completed', label: 'Completed', statuses: ['COMPLETED'] },
  { key: 'cancelled', label: 'Cancelled', statuses: ['CANCELLED'] },
]

/** Columns of the dispatch board, left to right. */
export const TRIP_STAGES = [
  {
    key: 'scheduled',
    label: 'Scheduled',
    hint: 'Waiting for the driver or for clearance',
    statuses: ['SCHEDULED', 'ACCEPTED'],
  },
  {
    key: 'road',
    label: 'On the road',
    hint: 'Cleared or in transit',
    statuses: ['CLEARED_FOR_DISPATCH', 'IN_TRANSIT'],
  },
  {
    key: 'paperwork',
    label: 'Paperwork',
    hint: 'Delivered, OR not yet received by the steel company',
    statuses: ['DELIVERED_OR_PENDING', 'OR_UPLOADED'],
  },
  {
    key: 'closed',
    label: 'Closed',
    hint: 'Completed, failed or cancelled',
    statuses: ['COMPLETED', 'FAILED', 'CANCELLED'],
  },
]

/**
 * @function matchesQuery
 * @description Case-insensitive match of a search text against several values.
 * @param {Array<string|null|undefined>} values Values to search in
 * @param {string} query Search text
 * @returns {boolean}
 */
export function matchesQuery(values, query) {
  const needle = query.trim().toLowerCase()
  if (!needle) return true
  return values.some((value) =>
    String(value ?? '')
      .toLowerCase()
      .includes(needle),
  )
}

/**
 * @function filterOrders
 * @description Orders for a status tab and a search text (client, reference, locations).
 * @param {Array<Object>} orders Delivery orders
 * @param {Array<Object>} clients Clients, to search by client name
 * @param {string} tabKey One of ORDER_TABS keys
 * @param {string} query Search text
 * @returns {Array<Object>}
 */
export function filterOrders(orders, clients, tabKey, query) {
  const tab = ORDER_TABS.find((entry) => entry.key === tabKey) ?? ORDER_TABS[0]
  const names = Object.fromEntries(
    clients.map((clientRecord) => [clientRecord.client_id, clientRecord.name]),
  )
  return orders.filter(
    (orderRecord) =>
      (!tab.statuses || tab.statuses.includes(orderRecord.status)) &&
      matchesQuery(
        [
          names[orderRecord.client_id],
          orderRecord.client_reference,
          orderRecord.pickup_location,
          orderRecord.delivery_location,
        ],
        query,
      ),
  )
}

/**
 * @function countOrdersByTab
 * @description How many orders each tab holds.
 * @param {Array<Object>} orders Delivery orders
 * @returns {Object<string, number>}
 */
export function countOrdersByTab(orders) {
  return Object.fromEntries(
    ORDER_TABS.map((tab) => [
      tab.key,
      tab.statuses
        ? orders.filter((orderRecord) => tab.statuses.includes(orderRecord.status)).length
        : orders.length,
    ]),
  )
}

/**
 * @function summarizeTrucks
 * @description Fleet counts for the stat cards.
 * @param {Array<Object>} trucks Trucks
 * @returns {{total: number, available: number, working: number, maintenance: number, retired: number}}
 */
export function summarizeTrucks(trucks) {
  const active = trucks.filter((truckRecord) => truckRecord.is_active)
  return {
    total: active.length,
    available: active.filter((truckRecord) => truckRecord.status === 'AVAILABLE').length,
    working: active.filter((truckRecord) => ['ASSIGNED', 'IN_TRANSIT'].includes(truckRecord.status))
      .length,
    maintenance: active.filter((truckRecord) => truckRecord.status === 'MAINTENANCE').length,
    retired: trucks.length - active.length,
  }
}

/**
 * @function groupTripsByStage
 * @description Split trips into the dispatch board columns.
 * @param {Array<Object>} trips Trips
 * @returns {Object<string, Array<Object>>}
 */
export function groupTripsByStage(trips) {
  return Object.fromEntries(
    TRIP_STAGES.map((stage) => [
      stage.key,
      trips.filter((tripRecord) => stage.statuses.includes(tripRecord.status)),
    ]),
  )
}

/**
 * @function buildNameLookup
 * @description Id-to-name maps from the dispatch resources response.
 * @param {{trucks: Array<Object>, drivers: Array<Object>, helpers: Array<Object>}} resources Resources
 * @returns {{trucks: Object<string, string>, people: Object<string, string>}}
 */
export function buildNameLookup(resources) {
  const toPairs = (records) => records.map((record) => [record.resource_id, record.name])
  return {
    trucks: Object.fromEntries(toPairs(resources.trucks)),
    people: Object.fromEntries([...toPairs(resources.drivers), ...toPairs(resources.helpers)]),
  }
}

/**
 * @function attentionItems
 * @description Trips that need a person to act, with what to do.
 * @param {Array<Object>} trips Trips
 * @returns {Array<{trip: Object, kind: string, message: string}>}
 */
export function attentionItems(trips) {
  const items = []
  for (const tripRecord of trips) {
    if (tripRecord.status === 'ACCEPTED') {
      items.push({
        trip: tripRecord,
        kind: 'clear',
        message: 'Accepted by the driver: clear for dispatch',
      })
    } else if (tripRecord.status === 'DELIVERED_OR_PENDING') {
      items.push({
        trip: tripRecord,
        kind: 'upload',
        message: 'Delivered: waiting for the signed OR photo',
      })
    } else if (tripRecord.status === 'OR_UPLOADED') {
      items.push({
        trip: tripRecord,
        kind: 'receipt',
        message: 'Waiting for the driver to confirm the steel company received the OR',
      })
    }
  }
  return items
}

/**
 * @function summarizeOperations
 * @description Numbers for the dashboard stat cards.
 * @param {{orders: Array<Object>, trips: Array<Object>, trucks: Array<Object>, resources: Object}} operations Loaded records
 * @returns {Object<string, number>}
 */
export function summarizeOperations({ orders, trips, trucks, resources }) {
  const trucksSummary = summarizeTrucks(trucks)
  const countTrips = (...statuses) =>
    trips.filter((tripRecord) => statuses.includes(tripRecord.status)).length
  const blocked = [...resources.trucks, ...resources.drivers, ...resources.helpers].filter(
    (record) => !record.can_receive_assignment,
  ).length
  return {
    pendingOrders: orders.filter((orderRecord) =>
      ['PENDING', 'PARTIALLY_ASSIGNED'].includes(orderRecord.status),
    ).length,
    activeTrips: countTrips(
      'SCHEDULED',
      'ACCEPTED',
      'CLEARED_FOR_DISPATCH',
      'IN_TRANSIT',
      'DELIVERED_OR_PENDING',
      'OR_UPLOADED',
    ),
    inTransit: countTrips('IN_TRANSIT'),
    awaitingClearance: countTrips('ACCEPTED'),
    awaitingReceipt: countTrips('DELIVERED_OR_PENDING', 'OR_UPLOADED'),
    availableTrucks: trucksSummary.available,
    maintenanceTrucks: trucksSummary.maintenance,
    blockedResources: blocked,
  }
}

/** Status tabs for the fleet screen. */
export const TRUCK_TABS = [
  { key: 'all', label: 'All' },
  { key: 'available', label: 'Available' },
  { key: 'working', label: 'On a trip' },
  { key: 'maintenance', label: 'Maintenance' },
  { key: 'retired', label: 'Retired' },
]

/**
 * @function truckMatchesTab
 * @description Whether a truck belongs to a fleet tab.
 * @param {Object} truckRecord Truck
 * @param {string} tabKey One of TRUCK_TABS keys
 * @returns {boolean}
 */
function truckMatchesTab(truckRecord, tabKey) {
  if (tabKey === 'retired') return !truckRecord.is_active
  if (!truckRecord.is_active) return false
  if (tabKey === 'available') return truckRecord.status === 'AVAILABLE'
  if (tabKey === 'working') return ['ASSIGNED', 'IN_TRANSIT'].includes(truckRecord.status)
  if (tabKey === 'maintenance') return truckRecord.status === 'MAINTENANCE'
  return true
}

/**
 * @function filterTrucks
 * @description Trucks for a fleet tab and a search over plate and description.
 * @param {Array<Object>} trucks Trucks
 * @param {string} tabKey One of TRUCK_TABS keys
 * @param {string} query Search text
 * @returns {Array<Object>}
 */
export function filterTrucks(trucks, tabKey, query) {
  return trucks.filter(
    (truckRecord) =>
      truckMatchesTab(truckRecord, tabKey) &&
      matchesQuery([truckRecord.plate_number, truckRecord.description], query),
  )
}

/**
 * @function countTrucksByTab
 * @description How many trucks each fleet tab holds.
 * @param {Array<Object>} trucks Trucks
 * @returns {Object<string, number>}
 */
export function countTrucksByTab(trucks) {
  return Object.fromEntries(
    TRUCK_TABS.map((tab) => [
      tab.key,
      trucks.filter((truckRecord) => truckMatchesTab(truckRecord, tab.key)).length,
    ]),
  )
}

/**
 * @function summarizeDispatch
 * @description Counts for the dispatch board header.
 * @param {Array<Object>} trips Trips
 * @param {{trucks: Array<Object>, drivers: Array<Object>, helpers: Array<Object>}} resources Dispatch resources
 * @returns {{awaitingClearance: number, onRoad: number, paperwork: number, blocked: number}}
 */
export function summarizeDispatch(trips, resources) {
  const groups = groupTripsByStage(trips)
  const blocked = [...resources.trucks, ...resources.drivers, ...resources.helpers].filter(
    (record) => !record.can_receive_assignment,
  ).length
  return {
    awaitingClearance: trips.filter((tripRecord) => tripRecord.status === 'ACCEPTED').length,
    onRoad: groups.road.length,
    paperwork: groups.paperwork.length,
    blocked,
  }
}
