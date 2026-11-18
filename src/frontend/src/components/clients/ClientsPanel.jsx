// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: ClientsPanel =====
// Purpose: Clients: search, add, edit, activate and deactivate
// Inputs: list state, permissions and callbacks (props only)
// Returns: page markup
// Flow:
// 1. Searchable list with contact details
// 2. New and edit open in a dialog; deactivating is a one-click toggle with a toast

// AI MODIFIED: Standardize formatting and workflow documentation conventions.

import { useState } from 'react'
import { useToast } from '../../hooks/useToast'
import { buildChanges, compactPayload } from '../../shared/utils/forms'
import { initialsOf } from '../../shared/utils/formatting'
import { matchesQuery } from '../../shared/utils/operations'
import { EmptyState } from '../../shared/components/EmptyState'
import { ErrorNotice } from '../../shared/components/ErrorNotice'
import { FormField } from '../../shared/components/FormField'
import { Icon } from '../../shared/components/Icon'
import { ListSkeleton } from '../../shared/components/ListSkeleton'
import { ModalDialog } from '../../shared/components/ModalDialog'
import { PageHeader } from '../../shared/components/PageHeader'
import { RowMenu } from '../../shared/components/RowMenu'
import { SearchField } from '../../shared/components/SearchField'
import { Toast } from '../../shared/components/Toast'

const EDITABLE_FIELDS = ['name', 'address', 'contact_person', 'contact_phone']

/**
 * @function ClientForm
 * @description Create or edit form for a client.
 * @param {Object} componentProps Props: client, isBusy, failure, onSubmit, onClose
 * @returns {import('react').ReactElement}
 */
function ClientForm({ client, isBusy, failure, onSubmit, onClose }) {
  return (
    <form
      className="grid gap-x-4 sm:grid-cols-2"
      onSubmit={async (event) => {
        event.preventDefault()
        await onSubmit(Object.fromEntries(new FormData(event.currentTarget)))
      }}
    >
      <FormField label="Company name" className="sm:col-span-2">
        <input
          name="name"
          required
          maxLength={160}
          defaultValue={client?.name}
          className="input w-full"
        />
      </FormField>
      <FormField label="Address (optional)" className="sm:col-span-2">
        <input
          name="address"
          maxLength={300}
          defaultValue={client?.address ?? ''}
          className="input w-full"
        />
      </FormField>
      <FormField label="Contact person (optional)">
        <input
          name="contact_person"
          maxLength={120}
          defaultValue={client?.contact_person ?? ''}
          className="input w-full"
        />
      </FormField>
      <FormField label="Contact phone (optional)">
        <input
          name="contact_phone"
          maxLength={32}
          defaultValue={client?.contact_phone ?? ''}
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
          {client ? 'Save changes' : 'Add client'}
        </button>
      </div>
    </form>
  )
}

/**
 * @function ClientsPanel
 * @description Pure UI for clients.
 * @param {Object} componentProps Props: loadState, clients, failure, actionFailure, isBusy, canWrite, onCreate, onUpdate
 * @returns {import('react').ReactElement}
 */
export function ClientsPanel({
  loadState,
  clients,
  failure,
  actionFailure,
  isBusy,
  canWrite,
  onCreate,
  onUpdate,
}) {
  const [query, setQuery] = useState('')
  const [formState, setFormState] = useState(null)
  const { toast, showToast } = useToast()
  const visibleClients = clients.filter((clientRecord) =>
    matchesQuery(
      [
        clientRecord.name,
        clientRecord.contact_person,
        clientRecord.contact_phone,
        clientRecord.address,
      ],
      query,
    ),
  )

  const submitForm = async (values) => {
    const editing = formState.client
    let succeeded
    if (editing) {
      const changes = buildChanges(editing, values, EDITABLE_FIELDS)
      succeeded =
        Object.keys(changes).length === 0 ? true : await onUpdate(editing.client_id, changes)
    } else {
      succeeded = await onCreate(compactPayload(values))
    }
    if (succeeded) {
      setFormState(null)
      showToast(editing ? 'Client updated' : 'Client added')
    }
  }

  const toggleActive = async (clientRecord) => {
    const succeeded = await onUpdate(clientRecord.client_id, { is_active: !clientRecord.is_active })
    if (succeeded) showToast(clientRecord.is_active ? 'Client deactivated' : 'Client activated')
  }

  return (
    <section className="space-y-5">
      <PageHeader
        title="Clients"
        subtitle={`${clients.length} clients`}
        actions={
          canWrite ? (
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setFormState({ client: null })}
            >
              <Icon name="plus" className="h-4 w-4" /> New client
            </button>
          ) : null
        }
      />
      <ErrorNotice failure={failure} />
      {formState === null ? <ErrorNotice failure={actionFailure} /> : null}
      <SearchField value={query} onChange={setQuery} placeholder="Search name, contact, phone" />

      {loadState === 'loading' && clients.length === 0 ? <ListSkeleton /> : null}
      {loadState !== 'loading' && visibleClients.length === 0 ? (
        <EmptyState
          icon="building"
          title={clients.length === 0 ? 'No clients yet' : 'No clients match'}
          description={
            clients.length === 0
              ? 'Add the steel company you haul for to start recording orders.'
              : 'Try a different search.'
          }
          action={
            canWrite && clients.length === 0 ? (
              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={() => setFormState({ client: null })}
              >
                Add a client
              </button>
            ) : null
          }
        />
      ) : null}

      {visibleClients.length > 0 ? (
        <ul className="list card card-border bg-base-100">
          {visibleClients.map((clientRecord) => (
            <li key={clientRecord.client_id} className="list-row items-center">
              <div className="avatar avatar-placeholder">
                <div className="w-11 rounded-box bg-secondary/20 text-secondary">
                  <span className="font-bold">{initialsOf(clientRecord.name)}</span>
                </div>
              </div>
              <div className="min-w-0">
                <p className="font-semibold">{clientRecord.name}</p>
                <p className="truncate text-sm text-base-content/70">
                  {[clientRecord.contact_person, clientRecord.contact_phone]
                    .filter(Boolean)
                    .join(' · ') || 'No contact on file'}
                </p>
                {clientRecord.address ? (
                  <p className="truncate text-xs text-base-content/50">{clientRecord.address}</p>
                ) : null}
              </div>
              {clientRecord.is_active ? null : (
                <span className="badge badge-outline border-base-content/40 text-base-content/70">
                  Inactive
                </span>
              )}
              {canWrite ? (
                <RowMenu
                  label="Client actions"
                  items={[
                    {
                      label: 'Edit details',
                      onSelect: () => setFormState({ client: clientRecord }),
                    },
                    {
                      label: clientRecord.is_active ? 'Deactivate' : 'Activate',
                      danger: clientRecord.is_active,
                      onSelect: () => toggleActive(clientRecord),
                    },
                  ]}
                />
              ) : (
                <span className="w-8" />
              )}
            </li>
          ))}
        </ul>
      ) : null}

      <ModalDialog
        title={formState?.client ? 'Edit client' : 'Add a client'}
        isOpen={formState !== null}
        onClose={() => setFormState(null)}
        wide
      >
        <ClientForm
          client={formState?.client ?? null}
          isBusy={isBusy}
          failure={actionFailure}
          onSubmit={submitForm}
          onClose={() => setFormState(null)}
        />
      </ModalDialog>
      <Toast toast={toast} />
    </section>
  )
}
