// AI MODIFIED: Place modules in their owning folders and update relative imports.
// ===== AI GENERATED: MyTripsPanel =====
// Purpose: A crew member's trips, built for a phone: one big next-step button per trip
// Inputs: trips, employee id, callbacks (props only)
// Returns: page markup
// Flow:
// 1. Each trip is a card with route, load, progress steps and your role on it
// 2. Only the assigned driver gets accept / depart / deliver and confirm-receipt
// 3. OR upload, stamped copy and receipt confirmation are collapsible sections

// AI MODIFIED: Hide actions and document controls when backend grants are absent.

import { useToast } from '../../hooks/useToast'
import { crewTripActions } from '../../shared/utils/dispatch'
import { formatDate, formatTons } from '../../shared/utils/formatting'
import { ConfirmReceiptForm } from './ConfirmReceiptForm'
import { DocumentLinks } from '../../shared/components/DocumentLinks'
import { EmptyState } from '../../shared/components/EmptyState'
import { ErrorNotice } from '../../shared/components/ErrorNotice'
import { ListSkeleton } from '../../shared/components/ListSkeleton'
import { OrUploadForm } from './OrUploadForm'
import { PageHeader } from '../../shared/components/PageHeader'
import { StatusBadge } from '../../shared/components/StatusBadge'
import { Toast } from '../../shared/components/Toast'
import { TripSteps } from './TripSteps'

const PROGRESS_MESSAGES = {
  accept: 'Trip accepted',
  depart: 'Departure recorded. Drive safe!',
  deliver: 'Delivery recorded. Upload the signed OR next.',
}

/**
 * @function Section
 * @description A collapsible block inside a trip card.
 * @param {{title: string, open?: boolean, children: import('react').ReactNode}} componentProps
 * @returns {import('react').ReactElement}
 */
function Section({ title, open = false, children }) {
  return (
    <div className="collapse collapse-arrow rounded-box bg-base-200">
      <input type="checkbox" defaultChecked={open} aria-label={title} />
      <div className="collapse-title font-semibold">{title}</div>
      <div className="collapse-content space-y-3">{children}</div>
    </div>
  )
}

/**
 * @function MyTripsPanel
 * @description Pure UI for a crew member's trips.
 * @param {Object} componentProps Props: loadState, trips, employeeIdentifier, capabilities, failure, actionFailure, isBusy, onProgress, onUpload, onConfirm, onOpenDocument
 * @returns {import('react').ReactElement}
 */
export function MyTripsPanel({
  loadState,
  trips,
  employeeIdentifier,
  capabilities = {},
  failure,
  actionFailure,
  isBusy,
  onProgress,
  onUpload,
  onConfirm,
  onOpenDocument,
}) {
  const { toast, showToast } = useToast()

  return (
    <section className="mx-auto max-w-2xl space-y-5">
      <PageHeader title="My trips" subtitle="Your assigned deliveries" />
      <ErrorNotice failure={failure} />
      <ErrorNotice failure={actionFailure} />
      {loadState === 'loading' && trips.length === 0 ? <ListSkeleton rows={2} /> : null}
      {loadState === 'ready' && trips.length === 0 ? (
        <EmptyState
          icon="route"
          title="No trips assigned"
          description="When the dispatcher assigns you to a delivery it shows up here."
        />
      ) : null}

      <div className="space-y-4">
        {trips.map((tripRecord) => {
          const actions = crewTripActions(tripRecord, employeeIdentifier, capabilities)
          const nextAction = actions.progress
          const isDriver = tripRecord.driver_id === employeeIdentifier
          const { uploadSigned, uploadStamped, confirmReceipt } = actions
          const visibleDocuments = actions.viewDocuments ? tripRecord.documents : []
          const signedDocuments = visibleDocuments.filter((entry) => entry.kind === 'SIGNED_OR')
          const stampedDocuments = visibleDocuments.filter((entry) => entry.kind === 'STAMPED_COPY')
          return (
            <article key={tripRecord.trip_id} className="card card-border bg-base-100">
              <div className="card-body gap-4 p-5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <p className="text-lg font-bold">{formatDate(tripRecord.scheduled_date)}</p>
                    <p className="text-sm text-base-content/70">
                      {formatTons(tripRecord.load_tons)} · you are{' '}
                      {isDriver ? 'the driver' : 'a helper'}
                    </p>
                  </div>
                  <StatusBadge kind="trip" status={tripRecord.status} />
                </div>
                <div className="space-y-2">
                  <p className="flex items-start gap-3">
                    <span className="mt-2 h-2.5 w-2.5 shrink-0 rounded-full bg-base-content/40" />
                    <span>
                      <span className="block text-xs uppercase tracking-wide text-base-content/50">
                        Pickup
                      </span>
                      {tripRecord.pickup_location}
                    </span>
                  </p>
                  <p className="flex items-start gap-3">
                    <span className="mt-2 h-2.5 w-2.5 shrink-0 rounded-full bg-primary" />
                    <span>
                      <span className="block text-xs uppercase tracking-wide text-base-content/50">
                        Delivery
                      </span>
                      {tripRecord.delivery_location}
                    </span>
                  </p>
                </div>
                <TripSteps status={tripRecord.status} />
                {nextAction ? (
                  <button
                    type="button"
                    disabled={isBusy}
                    className="btn btn-primary btn-lg w-full"
                    onClick={async () => {
                      if (await onProgress(tripRecord.trip_id, nextAction.name))
                        showToast(PROGRESS_MESSAGES[nextAction.name])
                    }}
                  >
                    {nextAction.label}
                  </button>
                ) : null}
                {uploadSigned || signedDocuments.length > 0 ? (
                  <Section title="Signed OR" open={tripRecord.status === 'DELIVERED_OR_PENDING'}>
                    <DocumentLinks
                      documents={signedDocuments}
                      disabled={isBusy}
                      onOpen={(identifier) => onOpenDocument(tripRecord.trip_id, identifier)}
                    />
                    {uploadSigned ? (
                      <OrUploadForm
                        label={
                          tripRecord.status === 'OR_UPLOADED'
                            ? 'Replace the signed OR'
                            : 'Photo of the signed OR'
                        }
                        disabled={isBusy}
                        onUpload={async (imageFile) => {
                          const succeeded = await onUpload(
                            tripRecord.trip_id,
                            imageFile,
                            'SIGNED_OR',
                          )
                          if (succeeded) showToast('Signed OR uploaded')
                          return succeeded
                        }}
                      />
                    ) : null}
                  </Section>
                ) : null}
                {confirmReceipt ? (
                  <Section title="Confirm receipt" open>
                    <ConfirmReceiptForm
                      disabled={isBusy}
                      onConfirm={async (receivedAtIso) => {
                        const succeeded = await onConfirm(tripRecord.trip_id, receivedAtIso)
                        if (succeeded) showToast('Receipt confirmed. Trip completed!')
                        return succeeded
                      }}
                    />
                  </Section>
                ) : null}
                {uploadStamped || stampedDocuments.length > 0 ? (
                  <Section title="Stamped copy (optional)">
                    <DocumentLinks
                      documents={stampedDocuments}
                      disabled={isBusy}
                      onOpen={(identifier) => onOpenDocument(tripRecord.trip_id, identifier)}
                    />
                    {uploadStamped ? (
                      <OrUploadForm
                        label="Photo of the stamped copy"
                        disabled={isBusy}
                        onUpload={async (imageFile) => {
                          const succeeded = await onUpload(
                            tripRecord.trip_id,
                            imageFile,
                            'STAMPED_COPY',
                          )
                          if (succeeded) showToast('Stamped copy uploaded')
                          return succeeded
                        }}
                      />
                    ) : null}
                  </Section>
                ) : null}
              </div>
            </article>
          )
        })}
      </div>
      <Toast toast={toast} />
    </section>
  )
}
