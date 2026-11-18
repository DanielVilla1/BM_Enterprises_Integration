// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: DeliveryOrdersPanel =====
// Purpose: Delivery orders: search, filter, record, edit and cancel
// Inputs: list state, clients, permissions and callbacks (props only)
// Returns: page markup
// Flow:
// 1. Tabs and search narrow the list; each row shows date, client, route, weight and status
// 2. New and edit open in a dialog; cancelling asks for a reason
// 3. Success shows a toast; failures stay visible in the dialog

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { useState } from 'react'
import { useToast } from '../../hooks/useToast'
import { buildChanges, compactPayload, toLocalInputValue } from '../../shared/utils/forms'
import { dateBlock, formatTons } from '../../shared/utils/formatting'
import { ORDER_TABS, countOrdersByTab, filterOrders } from '../../shared/utils/operations'
import { EmptyState } from '../../shared/components/EmptyState'
import { ErrorNotice } from '../../shared/components/ErrorNotice'
import { FilterTabs } from '../../shared/components/FilterTabs'
import { FormField } from '../../shared/components/FormField'
import { Icon } from '../../shared/components/Icon'
import { ListSkeleton } from '../../shared/components/ListSkeleton'
import { ModalDialog } from '../../shared/components/ModalDialog'
import { PageHeader } from '../../shared/components/PageHeader'
import { ReasonDialog } from '../../shared/components/ReasonDialog'
import { RowMenu } from '../../shared/components/RowMenu'
import { SearchField } from '../../shared/components/SearchField'
import { StatusBadge } from '../../shared/components/StatusBadge'
import { Toast } from '../../shared/components/Toast'

const EDITABLE_FIELDS = [
  'client_reference',
  'pickup_location',
  'delivery_location',
  'scheduled_date',
  'total_weight_tons',
  'notes',
]

/**
 * @function OrderForm
 * @description Create or edit form for an order.
 * @param {Object} componentProps Props: clients, order, isBusy, failure, onSubmit, onClose
 * @returns {import('react').ReactElement}
 */
function OrderForm({ clients, order, isBusy, failure, onSubmit, onClose }) {
  const isEdit = order !== null
  const today = toLocalInputValue(new Date()).slice(0, 10)
  const clientName =
    clients.find((clientRecord) => clientRecord.client_id === order?.client_id)?.name ?? ''
  return (
    <form
      className="grid gap-x-4 sm:grid-cols-2"
      onSubmit={async (event) => {
        event.preventDefault()
        await onSubmit(Object.fromEntries(new FormData(event.currentTarget)))
      }}
    >
      <FormField label="Client" className="sm:col-span-2">
        {isEdit ? (
          <input className="input w-full" value={clientName} disabled readOnly />
        ) : (
          <select name="client_id" required defaultValue="" className="select w-full">
            <option value="" disabled>
              Choose a client
            </option>
            {clients
              .filter((clientRecord) => clientRecord.is_active)
              .map((clientRecord) => (
                <option key={clientRecord.client_id} value={clientRecord.client_id}>
                  {clientRecord.name}
                </option>
              ))}
          </select>
        )}
      </FormField>
      <FormField label="Pickup location" className="sm:col-span-2">
        <input
          name="pickup_location"
          required
          minLength={3}
          maxLength={300}
          defaultValue={order?.pickup_location}
          className="input w-full"
          placeholder="Where the steel is loaded"
        />
      </FormField>
      <FormField label="Delivery location" className="sm:col-span-2">
        <input
          name="delivery_location"
          required
          minLength={3}
          maxLength={300}
          defaultValue={order?.delivery_location}
          className="input w-full"
          placeholder="Where it is delivered"
        />
      </FormField>
      <FormField label="Scheduled date">
        <input
          name="scheduled_date"
          type="date"
          required
          min={isEdit ? undefined : today}
          defaultValue={order?.scheduled_date}
          className="input w-full"
        />
      </FormField>
      <FormField label="Weight (metric tons)">
        <input
          name="total_weight_tons"
          type="number"
          required
          min="0.001"
          max="100000"
          step="0.001"
          defaultValue={order?.total_weight_tons}
          className="input w-full"
        />
      </FormField>
      <FormField label="Client reference (optional)">
        <input
          name="client_reference"
          maxLength={64}
          defaultValue={order?.client_reference ?? ''}
          className="input w-full"
          placeholder="Their PO number"
        />
      </FormField>
      <FormField label="Notes (optional)">
        <input
          name="notes"
          maxLength={1000}
          defaultValue={order?.notes ?? ''}
          className="input w-full"
        />
      </FormField>
      <div className="sm:col-span-2">
        <ErrorNotice failure={failure} />
      </div>
      <div className="modal-action sm:col-span-2">
        <button type="button" className="btn btn-ghost" onClick={onClose}>
          Back
        </button>
        <button type="submit" className="btn btn-primary" disabled={isBusy}>
          {isEdit ? 'Save changes' : 'Record order'}
        </button>
      </div>
    </form>
  )
}

/**
 * @function DeliveryOrdersPanel
 * @description Pure UI for delivery orders.
 * @param {Object} componentProps Props: loadState, orders, clients, failure, actionFailure, isBusy, canWrite, onCreate, onUpdate, onCancel
 * @returns {import('react').ReactElement}
 */
export function DeliveryOrdersPanel({
  loadState,
  orders,
  clients,
  failure,
  actionFailure,
  isBusy,
  canWrite,
  onCreate,
  onUpdate,
  onCancel,
}) {
  const [tabKey, setTabKey] = useState('open')
  const [query, setQuery] = useState('')
  const [formState, setFormState] = useState(null)
  const [reasonRequest, setReasonRequest] = useState(null)
  const { toast, showToast } = useToast()

  const clientNames = Object.fromEntries(
    clients.map((clientRecord) => [clientRecord.client_id, clientRecord.name]),
  )
  const visibleOrders = filterOrders(orders, clients, tabKey, query)
  const counts = countOrdersByTab(orders)
  const modalIsOpen = formState !== null || reasonRequest !== null

  const submitForm = async (values) => {
    const editing = formState.order
    let succeeded
    if (editing) {
      const changes = buildChanges(editing, values, EDITABLE_FIELDS, ['total_weight_tons'])
      succeeded =
        Object.keys(changes).length === 0 ? true : await onUpdate(editing.order_id, changes)
    } else {
      succeeded = await onCreate(
        compactPayload({ ...values, total_weight_tons: Number(values.total_weight_tons) }),
      )
    }
    if (succeeded) {
      setFormState(null)
      showToast(editing ? 'Order updated' : 'Order recorded')
    }
  }

  return (
    <section className="space-y-5">
      <PageHeader
        title="Delivery orders"
        subtitle={`${orders.length} orders recorded`}
        actions={
          canWrite ? (
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setFormState({ order: null })}
            >
              <Icon name="plus" className="h-4 w-4" /> New order
            </button>
          ) : null
        }
      />
      <ErrorNotice failure={failure} />
      {!modalIsOpen ? <ErrorNotice failure={actionFailure} /> : null}

      <div className="flex flex-wrap items-center justify-between gap-3">
        <FilterTabs
          tabs={ORDER_TABS}
          activeKey={tabKey}
          counts={counts}
          onChange={setTabKey}
          label="Order status"
        />
        <SearchField
          value={query}
          onChange={setQuery}
          placeholder="Search client, reference, place"
        />
      </div>

      {loadState === 'loading' && orders.length === 0 ? <ListSkeleton /> : null}
      {loadState !== 'loading' && visibleOrders.length === 0 ? (
        <EmptyState
          icon="clipboard"
          title={orders.length === 0 ? 'No delivery orders yet' : 'No orders match'}
          description={
            orders.length === 0
              ? 'Record the first order from the steel company to start planning trips.'
              : 'Try another tab or clear the search.'
          }
          action={
            canWrite && orders.length === 0 ? (
              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={() => setFormState({ order: null })}
              >
                Record an order
              </button>
            ) : null
          }
        />
      ) : null}

      {visibleOrders.length > 0 ? (
        <ul className="list card card-border bg-base-100">
          {visibleOrders.map((orderRecord) => {
            const { month, day } = dateBlock(orderRecord.scheduled_date)
            const menuItems =
              canWrite && orderRecord.status === 'PENDING'
                ? [
                    { label: 'Edit order', onSelect: () => setFormState({ order: orderRecord }) },
                    {
                      label: 'Cancel order',
                      danger: true,
                      onSelect: () =>
                        setReasonRequest({
                          title: 'Cancel this order?',
                          description: 'The order stays on record as cancelled.',
                          confirmLabel: 'Cancel order',
                          onConfirm: async (reason) => {
                            const succeeded = await onCancel(orderRecord.order_id, reason)
                            if (succeeded) showToast('Order cancelled')
                            return succeeded
                          },
                        }),
                    },
                  ]
                : []
            return (
              <li key={orderRecord.order_id} className="list-row items-center">
                <div className="flex h-12 w-12 flex-col items-center justify-center rounded-box bg-base-200 leading-none">
                  <span className="text-[10px] font-bold text-primary">{month}</span>
                  <span className="text-lg font-bold">{day}</span>
                </div>
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-semibold">
                      {clientNames[orderRecord.client_id] ?? 'Client'}
                    </span>
                    {orderRecord.client_reference ? (
                      <span className="badge badge-ghost badge-sm">
                        {orderRecord.client_reference}
                      </span>
                    ) : null}
                  </div>
                  <p className="truncate text-sm text-base-content/70">
                    {orderRecord.pickup_location} → {orderRecord.delivery_location}
                  </p>
                  {orderRecord.cancellation_reason ? (
                    <p className="truncate text-xs text-base-content/50">
                      Cancelled: {orderRecord.cancellation_reason}
                    </p>
                  ) : null}
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span className="font-semibold tabular-nums">
                    {formatTons(orderRecord.total_weight_tons)}
                  </span>
                  <StatusBadge kind="order" status={orderRecord.status} />
                </div>
                {menuItems.length > 0 ? (
                  <RowMenu label="Order actions" items={menuItems} />
                ) : (
                  <span className="w-8" />
                )}
              </li>
            )
          })}
        </ul>
      ) : null}

      <ModalDialog
        title={formState?.order ? 'Edit order' : 'Record a delivery order'}
        isOpen={formState !== null}
        onClose={() => setFormState(null)}
        wide
      >
        <OrderForm
          clients={clients}
          order={formState?.order ?? null}
          isBusy={isBusy}
          failure={actionFailure}
          onSubmit={submitForm}
          onClose={() => setFormState(null)}
        />
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
