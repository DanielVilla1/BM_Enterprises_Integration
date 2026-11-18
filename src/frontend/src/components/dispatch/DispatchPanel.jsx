// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: DispatchPanel =====
// Purpose: The dispatch board: assign trips, clear them, change crew or truck, cancel, fail
// Inputs: trips, orders, clients, availability, permissions and callbacks (props only)
// Returns: page markup
// Flow:
// 1. Header stats and a four-column board (scheduled, on the road, paperwork, closed)
// 2. Assign, change-crew and replace-truck open in dialogs; unavailable resources show why
// 3. Cancel, fail and correction ask for a reason; rule failures (capacity, blocked dispatch) show in the dialog

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { useState } from 'react'
import { useToast } from '../../hooks/useToast'
import { describeBlockReason, assignableOrders } from '../../shared/utils/dispatch'
import {
  buildNameLookup,
  groupTripsByStage,
  summarizeDispatch,
  TRIP_STAGES,
} from '../../shared/utils/operations'
import { EmptyState } from '../../shared/components/EmptyState'
import { ErrorNotice } from '../../shared/components/ErrorNotice'
import { FormField } from '../../shared/components/FormField'
import { Icon } from '../../shared/components/Icon'
import { ListSkeleton } from '../../shared/components/ListSkeleton'
import { ModalDialog } from '../../shared/components/ModalDialog'
import { PageHeader } from '../../shared/components/PageHeader'
import { ReasonDialog } from '../../shared/components/ReasonDialog'
import { StatCard } from '../../shared/components/StatCard'
import { Toast } from '../../shared/components/Toast'
import { TripCard } from './TripCard'
import { formatDate, formatTons } from '../../shared/utils/formatting'

const CLOSED_COLUMN_LIMIT = 5

/**
 * @function ResourceOptions
 * @description Option list that disables unavailable resources and says why.
 * @param {{resources: Array<Object>, keepEnabled?: Array<string>}} componentProps
 * @returns {import('react').ReactElement}
 */
function ResourceOptions({ resources, keepEnabled = [] }) {
  return resources.map((resourceRecord) => {
    const usable =
      resourceRecord.can_receive_assignment || keepEnabled.includes(resourceRecord.resource_id)
    return (
      <option
        key={resourceRecord.resource_id}
        value={resourceRecord.resource_id}
        disabled={!usable}
      >
        {resourceRecord.name}
        {resourceRecord.capacity_tons ? ` (${resourceRecord.capacity_tons} t)` : ''}
        {usable ? '' : ` — ${describeBlockReason(resourceRecord.reason)}`}
      </option>
    )
  })
}

/**
 * @function FormActions
 * @description Back and submit buttons for dialog forms.
 * @param {{label: string, isBusy: boolean, onClose: function(): void}} componentProps
 * @returns {import('react').ReactElement}
 */
function FormActions({ label, isBusy, onClose }) {
  return (
    <div className="modal-action sm:col-span-2">
      <button type="button" className="btn btn-ghost" onClick={onClose}>
        Back
      </button>
      <button type="submit" className="btn btn-primary" disabled={isBusy}>
        {label}
      </button>
    </div>
  )
}

/**
 * @function AssignForm
 * @description Form to assign a truck and crew to an order.
 * @param {Object} componentProps Props: orders, clientNames, resources, isBusy, failure, onSubmit, onClose
 * @returns {import('react').ReactElement}
 */
function AssignForm({ orders, clientNames, resources, isBusy, failure, onSubmit, onClose }) {
  return (
    <form
      className="grid gap-x-4 sm:grid-cols-2"
      onSubmit={async (event) => {
        event.preventDefault()
        await onSubmit(Object.fromEntries(new FormData(event.currentTarget)))
      }}
    >
      <FormField label="Order" className="sm:col-span-2">
        <select name="order_id" required defaultValue="" className="select w-full">
          <option value="" disabled>
            Choose an order
          </option>
          {assignableOrders(orders).map((orderRecord) => (
            <option key={orderRecord.order_id} value={orderRecord.order_id}>
              {formatDate(orderRecord.scheduled_date)} ·{' '}
              {clientNames[orderRecord.client_id] ?? 'Client'} → {orderRecord.delivery_location} ·{' '}
              {formatTons(orderRecord.total_weight_tons)}
            </option>
          ))}
        </select>
      </FormField>
      <FormField label="Truck">
        <select name="truck_id" required defaultValue="" className="select w-full">
          <option value="" disabled>
            Choose a truck
          </option>
          <ResourceOptions resources={resources.trucks} />
        </select>
      </FormField>
      <FormField label="Load (metric tons)">
        <input
          name="load_tons"
          type="number"
          required
          min="0.001"
          step="0.001"
          className="input w-full"
        />
      </FormField>
      <FormField label="Driver">
        <select name="driver_id" required defaultValue="" className="select w-full">
          <option value="" disabled>
            Choose a driver
          </option>
          <ResourceOptions resources={resources.drivers} />
        </select>
      </FormField>
      <FormField label="Helper">
        <select name="helper_one" required defaultValue="" className="select w-full">
          <option value="" disabled>
            Choose a helper
          </option>
          <ResourceOptions resources={resources.helpers} />
        </select>
      </FormField>
      <FormField label="Second helper (optional)" className="sm:col-span-2">
        <select name="helper_two" defaultValue="" className="select w-full">
          <option value="">None</option>
          <ResourceOptions resources={resources.helpers} />
        </select>
      </FormField>
      <div className="sm:col-span-2">
        <ErrorNotice failure={failure} />
      </div>
      <FormActions label="Assign trip" isBusy={isBusy} onClose={onClose} />
    </form>
  )
}

/**
 * @function CrewForm
 * @description Form to replace the driver and helpers of a trip that has not departed.
 * @param {Object} componentProps Props: trip, resources, isBusy, failure, onSubmit, onClose
 * @returns {import('react').ReactElement}
 */
function CrewForm({ trip, resources, isBusy, failure, onSubmit, onClose }) {
  const currentCrew = [trip.driver_id, ...trip.helper_ids]
  return (
    <form
      className="grid gap-x-4 sm:grid-cols-2"
      onSubmit={async (event) => {
        event.preventDefault()
        await onSubmit(Object.fromEntries(new FormData(event.currentTarget)))
      }}
    >
      <p className="text-sm text-base-content/70 sm:col-span-2">
        A new driver has to accept the trip again. Changing helpers after clearance means clearing
        it again.
      </p>
      <FormField label="Driver" className="sm:col-span-2">
        <select name="driver_id" required defaultValue={trip.driver_id} className="select w-full">
          <ResourceOptions resources={resources.drivers} keepEnabled={currentCrew} />
        </select>
      </FormField>
      <FormField label="Helper">
        <select
          name="helper_one"
          required
          defaultValue={trip.helper_ids[0]}
          className="select w-full"
        >
          <ResourceOptions resources={resources.helpers} keepEnabled={currentCrew} />
        </select>
      </FormField>
      <FormField label="Second helper (optional)">
        <select name="helper_two" defaultValue={trip.helper_ids[1] ?? ''} className="select w-full">
          <option value="">None</option>
          <ResourceOptions resources={resources.helpers} keepEnabled={currentCrew} />
        </select>
      </FormField>
      <div className="sm:col-span-2">
        <ErrorNotice failure={failure} />
      </div>
      <FormActions label="Save crew" isBusy={isBusy} onClose={onClose} />
    </form>
  )
}

/**
 * @function ReplaceTruckForm
 * @description Form to swap the truck of a trip (breakdown, maintenance).
 * @param {Object} componentProps Props: trip, resources, isBusy, failure, onSubmit, onClose
 * @returns {import('react').ReactElement}
 */
function ReplaceTruckForm({ trip, resources, isBusy, failure, onSubmit, onClose }) {
  const otherTrucks = resources.trucks.filter(
    (truckRecord) => truckRecord.resource_id !== trip.truck_id,
  )
  return (
    <form
      className="grid gap-x-4 sm:grid-cols-2"
      onSubmit={async (event) => {
        event.preventDefault()
        const formData = new FormData(event.currentTarget)
        await onSubmit({
          replacement_truck_id: formData.get('replacement_truck_id'),
          reason: String(formData.get('reason')).trim(),
          original_truck_needs_maintenance: formData.has('original_truck_needs_maintenance'),
        })
      }}
    >
      <p className="text-sm text-base-content/70 sm:col-span-2">
        The trip continues with the new truck. No extra charge or pay is created, and the
        replacement cannot skip the outstanding-OR dispatch rule.
      </p>
      <FormField label="Replacement truck" className="sm:col-span-2">
        <select name="replacement_truck_id" required defaultValue="" className="select w-full">
          <option value="" disabled>
            Choose a truck
          </option>
          <ResourceOptions resources={otherTrucks} />
        </select>
      </FormField>
      <FormField label="Reason" className="sm:col-span-2">
        <textarea
          name="reason"
          required
          minLength={3}
          maxLength={500}
          rows={2}
          className="textarea w-full"
          placeholder="Engine overheating, flat tires…"
        />
      </FormField>
      <label className="label cursor-pointer justify-start gap-3 sm:col-span-2">
        <input
          type="checkbox"
          name="original_truck_needs_maintenance"
          className="checkbox checkbox-warning"
        />
        <span>The original truck needs maintenance (it stays out of service)</span>
      </label>
      <div className="sm:col-span-2">
        <ErrorNotice failure={failure} />
      </div>
      <FormActions label="Replace truck" isBusy={isBusy} onClose={onClose} />
    </form>
  )
}

/**
 * @function DispatchPanel
 * @description Pure UI for dispatching.
 * @param {Object} componentProps Props: loadState, trips, orders, clients, resources, failure, actionFailure, isBusy, canWrite, canCorrect, onAssign, onClear, onClose, onChangeCrew, onReplaceTruck, onCorrect, onOpenDocument
 * @returns {import('react').ReactElement}
 */
export function DispatchPanel({
  loadState,
  trips,
  orders,
  clients,
  resources,
  failure,
  actionFailure,
  isBusy,
  canWrite,
  canCorrect,
  onAssign,
  onClear,
  onClose,
  onChangeCrew,
  onReplaceTruck,
  onCorrect,
  onOpenDocument,
}) {
  const [assignOpen, setAssignOpen] = useState(false)
  const [crewTrip, setCrewTrip] = useState(null)
  const [truckTrip, setTruckTrip] = useState(null)
  const [reasonRequest, setReasonRequest] = useState(null)
  const { toast, showToast } = useToast()

  const lookup = buildNameLookup(resources)
  const clientNames = Object.fromEntries(
    clients.map((clientRecord) => [clientRecord.client_id, clientRecord.name]),
  )
  const orderLookup = Object.fromEntries(
    orders.map((orderRecord) => [orderRecord.order_id, orderRecord]),
  )
  const stages = groupTripsByStage(trips)
  const summary = summarizeDispatch(trips, resources)
  const modalIsOpen =
    assignOpen || crewTrip !== null || truckTrip !== null || reasonRequest !== null

  const submitAssignment = async (values) => {
    const helperIds = [values.helper_one, values.helper_two].filter(Boolean)
    const succeeded = await onAssign(values.order_id, {
      truck_id: values.truck_id,
      driver_id: values.driver_id,
      helper_ids: helperIds,
      load_tons: Number(values.load_tons),
    })
    if (succeeded) {
      setAssignOpen(false)
      showToast('Trip assigned')
    }
  }

  const submitCrew = async (values) => {
    const helperIds = [values.helper_one, values.helper_two].filter(Boolean)
    const succeeded = await onChangeCrew(crewTrip.trip_id, {
      driver_id: values.driver_id,
      helper_ids: helperIds,
    })
    if (succeeded) {
      setCrewTrip(null)
      showToast('Crew updated')
    }
  }

  const submitTruck = async (replacement) => {
    const succeeded = await onReplaceTruck(truckTrip.trip_id, replacement)
    if (succeeded) {
      setTruckTrip(null)
      showToast('Truck replaced')
    }
  }

  const askReason = (tripRecord, kind) => {
    const details = {
      cancel: {
        title: 'Cancel this trip?',
        description: 'Only possible before the truck departs. The load returns to the order.',
        confirmLabel: 'Cancel trip',
        done: 'Trip cancelled',
      },
      fail: {
        title: 'Mark this trip as failed?',
        description:
          'Use this when the trip could not be completed. The load returns to the order.',
        confirmLabel: 'Mark as failed',
        done: 'Trip marked as failed',
      },
      correct: {
        title: 'Correct the receipt confirmation?',
        description:
          'Reopens the trip so the driver can confirm again. Not possible once a later trip has departed.',
        confirmLabel: 'Reopen trip',
        done: 'Confirmation reopened',
      },
    }[kind]
    setReasonRequest({
      title: details.title,
      description: details.description,
      confirmLabel: details.confirmLabel,
      onConfirm: async (reason) => {
        const succeeded =
          kind === 'correct'
            ? await onCorrect(tripRecord.trip_id, reason)
            : await onClose(tripRecord.trip_id, kind, reason)
        if (succeeded) showToast(details.done)
        return succeeded
      },
    })
  }

  const cardFor = (tripRecord) => {
    const orderRecord = orderLookup[tripRecord.order_id]
    return (
      <TripCard
        key={tripRecord.trip_id}
        trip={tripRecord}
        clientName={orderRecord ? (clientNames[orderRecord.client_id] ?? 'Client') : 'Client'}
        lookup={lookup}
        canWrite={canWrite}
        canCorrect={canCorrect}
        isBusy={isBusy}
        handlers={{
          clear: async () => {
            if (await onClear(tripRecord.trip_id)) showToast('Trip cleared for dispatch')
          },
          changeCrew: () => setCrewTrip(tripRecord),
          replaceTruck: () => setTruckTrip(tripRecord),
          cancel: () => askReason(tripRecord, 'cancel'),
          fail: () => askReason(tripRecord, 'fail'),
          correct: () => askReason(tripRecord, 'correct'),
          openDocument: (documentIdentifier) =>
            onOpenDocument(tripRecord.trip_id, documentIdentifier),
        }}
      />
    )
  }

  return (
    <section className="space-y-5">
      <PageHeader
        title="Dispatch board"
        subtitle="Assign trucks and crews, clear trips and follow them to completion"
        actions={
          canWrite ? (
            <button type="button" className="btn btn-primary" onClick={() => setAssignOpen(true)}>
              <Icon name="plus" className="h-4 w-4" /> Assign trip
            </button>
          ) : null
        }
      />
      <ErrorNotice failure={failure} />
      {!modalIsOpen ? <ErrorNotice failure={actionFailure} /> : null}

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatCard
          label="To clear for dispatch"
          value={summary.awaitingClearance}
          icon="check"
          tone="warning"
          hint="Accepted by the driver"
        />
        <StatCard label="On the road" value={summary.onRoad} icon="truck" tone="primary" />
        <StatCard
          label="Paperwork"
          value={summary.paperwork}
          icon="document"
          tone="info"
          hint="OR not yet received"
        />
        <StatCard
          label="Unavailable"
          value={summary.blocked}
          icon="alert"
          tone="neutral"
          hint="Trucks and crew"
        />
      </div>

      {loadState === 'loading' && trips.length === 0 ? <ListSkeleton /> : null}
      {loadState !== 'loading' && trips.length === 0 ? (
        <EmptyState
          icon="route"
          title="No trips yet"
          description="Assign a truck and crew to a delivery order to create the first trip."
          action={
            canWrite ? (
              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={() => setAssignOpen(true)}
              >
                Assign a trip
              </button>
            ) : null
          }
        />
      ) : null}

      {trips.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {TRIP_STAGES.map((stage) => {
            const stageTrips = stages[stage.key]
            const shown =
              stage.key === 'closed' ? stageTrips.slice(0, CLOSED_COLUMN_LIMIT) : stageTrips
            return (
              <div key={stage.key} className="space-y-3">
                <div>
                  <div className="flex items-center justify-between">
                    <h2 className="font-semibold">{stage.label}</h2>
                    <span className="badge badge-ghost">{stageTrips.length}</span>
                  </div>
                  <p className="text-xs text-base-content/60">{stage.hint}</p>
                </div>
                {shown.length === 0 ? (
                  <p className="rounded-box border border-dashed border-base-300 p-4 text-center text-sm text-base-content/50">
                    Nothing here
                  </p>
                ) : (
                  shown.map(cardFor)
                )}
                {stageTrips.length > shown.length ? (
                  <p className="text-center text-xs text-base-content/50">
                    + {stageTrips.length - shown.length} older closed trips
                  </p>
                ) : null}
              </div>
            )
          })}
        </div>
      ) : null}

      <ModalDialog
        title="Assign a trip"
        isOpen={assignOpen}
        onClose={() => setAssignOpen(false)}
        wide
      >
        <AssignForm
          orders={orders}
          clientNames={clientNames}
          resources={resources}
          isBusy={isBusy}
          failure={actionFailure}
          onSubmit={submitAssignment}
          onClose={() => setAssignOpen(false)}
        />
      </ModalDialog>
      <ModalDialog
        title="Change crew"
        isOpen={crewTrip !== null}
        onClose={() => setCrewTrip(null)}
        wide
      >
        {crewTrip ? (
          <CrewForm
            trip={crewTrip}
            resources={resources}
            isBusy={isBusy}
            failure={actionFailure}
            onSubmit={submitCrew}
            onClose={() => setCrewTrip(null)}
          />
        ) : null}
      </ModalDialog>
      <ModalDialog
        title="Replace truck"
        isOpen={truckTrip !== null}
        onClose={() => setTruckTrip(null)}
        wide
      >
        {truckTrip ? (
          <ReplaceTruckForm
            trip={truckTrip}
            resources={resources}
            isBusy={isBusy}
            failure={actionFailure}
            onSubmit={submitTruck}
            onClose={() => setTruckTrip(null)}
          />
        ) : null}
      </ModalDialog>
      <ReasonDialog
        request={reasonRequest}
        isBusy={isBusy}
        failure={actionFailure}
        onClose={() => setReasonRequest(null)}
      />
      <Toast toast={toast} />
    </section>
  )
}
