# ===== AI GENERATED: OrService =====
# Purpose: Signed OR upload, signed URLs, receipt confirmation and its correction (spec 6)
# Inputs: trip/document/idempotency repositories, object storage, image sanitizer, audit
# Returns: OrDocument / TripView entities or BusinessRuleError
# 1. Upload: validate and sanitize, store the object BEFORE the database transaction
# 2. Confirm: only the assigned driver; Idempotency-Key makes retries safe (IDEM-01)
# 3. Completion commits trip, restriction removal, order progress and audit in one transaction
# 4. Correction: Owner only, audited, refused once the next trip has departed


from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from ..Contract.i_audit_repository import IAuditRepository
from ..Contract.i_document_repositories import IIdempotencyRepository, IOrDocumentRepository
from ..Contract.i_financial_repository import ITripFinancialControls
from ..Contract.i_storage import (
    IImageSanitizer,
    InvalidImageError,
    IObjectStorage,
    StorageError,
)
from ..Contract.i_trip_repository import ITripRepository
from ..Contract.i_unit_of_work import IUnitOfWork
from ..Entity.access import AccessLevel
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.dispatch import Trip, TripStatus, TripView
from ..Entity.documents import OrDocument, OrDocumentKind
from ..Entity.employee import Principal
from .trip_service import TripService
from .trip_state_synchronizer import TripStateSynchronizer

CLOCK_SKEW = timedelta(minutes=5)
STORAGE_FOLDERS = {OrDocumentKind.SIGNED_OR: "signed-or", OrDocumentKind.STAMPED_COPY: "stamped-copy"}


def as_utc(moment: datetime) -> datetime:
    """Treat naive datetimes (SQLite) as UTC and normalize aware ones."""
    return moment.replace(tzinfo=UTC) if moment.tzinfo is None else moment.astimezone(UTC)


def _error(status: int, code: str, title: str, detail: str, **extensions: object) -> BusinessRuleError:
    return BusinessRuleError(status, code, title, detail, None, dict(extensions) or None)


def _conflict(code: str, detail: str, **extensions: object) -> BusinessRuleError:
    return _error(409, code, "Conflict", detail, **extensions)


def _trip_not_found() -> BusinessRuleError:
    return _error(404, "TRIP_NOT_FOUND", "Not found", "The trip was not found.")


class OrService:
    def __init__(
        self,
        trips: ITripRepository,
        documents: IOrDocumentRepository,
        idempotency: IIdempotencyRepository,
        storage: IObjectStorage,
        sanitizer: IImageSanitizer,
        audit: IAuditRepository,
        unit_of_work: IUnitOfWork,
        synchronizer: TripStateSynchronizer,
        trip_service: TripService,
        signed_url_ttl_seconds: int,
        maximum_upload_bytes: int,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        financial_controls: ITripFinancialControls | None = None,
        presentation_enabled: bool = False,
    ) -> None:
        self._trips = trips
        self._documents = documents
        self._idempotency = idempotency
        self._storage = storage
        self._sanitizer = sanitizer
        self._audit = audit
        self._unit_of_work = unit_of_work
        self._synchronizer = synchronizer
        self._trip_service = trip_service
        self._signed_url_ttl = signed_url_ttl_seconds
        self._maximum_upload_bytes = maximum_upload_bytes
        self._clock = clock
        self._financial_controls = financial_controls
        self._presentation_enabled = presentation_enabled

    # ----- documents ---------------------------------------------------------------

    def upload_document(
        self,
        principal: Principal,
        level: AccessLevel,
        trip_id: UUID,
        kind: OrDocumentKind,
        raw_content: bytes,
        trace_id: str | None,
    ) -> OrDocument:
        trip = self._crew_trip(principal, level, trip_id)
        if len(raw_content) > self._maximum_upload_bytes:
            raise _error(413, "PAYLOAD_TOO_LARGE", "Payload too large", "The file is larger than 5 MB.")
        self._require_uploadable(trip, kind)
        try:
            image = self._sanitizer.sanitize(raw_content)
        except InvalidImageError as invalid_image:
            raise _error(
                422, "INVALID_IMAGE", "Validation failed", "Upload a JPEG or PNG image."
            ) from invalid_image
        storage_path = f"{STORAGE_FOLDERS[kind]}/{trip_id}/{uuid4()}.{image.extension}"
        try:
            self._storage.put(storage_path, image.content, image.content_type)
        except StorageError as storage_error:
            raise _error(
                503,
                "STORAGE_UNAVAILABLE",
                "Service unavailable",
                "The document could not be stored. Try again shortly.",
            ) from storage_error
        try:
            self._trips.lock_trip(trip_id)
            locked = self._crew_trip(principal, level, trip_id)
            self._require_uploadable(locked, kind)
            self._documents.supersede_active(trip_id, kind)
            document = self._documents.add(
                trip_id, kind, storage_path, image.content_type, len(image.content), principal.employee_id
            )
            if kind is OrDocumentKind.SIGNED_OR and locked.status is TripStatus.DELIVERED_OR_PENDING:
                self._trips.mark_or_uploaded(trip_id, principal.employee_id)
            self._record(principal, "or_document.uploaded", trip_id, {"kind": kind.value}, trace_id)
            self._unit_of_work.commit()
        except Exception:
            self._storage.delete(storage_path)
            raise
        return document

    def list_documents(self, principal: Principal, level: AccessLevel, trip_id: UUID) -> list[OrDocument]:
        self._crew_trip(principal, level, trip_id)
        include_history = level is not AccessLevel.OWN
        return self._documents.list_for_trip(trip_id, include_history)

    def issue_document_url(
        self,
        principal: Principal,
        level: AccessLevel,
        trip_id: UUID,
        document_id: UUID,
        trace_id: str | None,
    ) -> tuple[str, int]:
        self._crew_trip(principal, level, trip_id)
        document = self._documents.get(document_id)
        hidden_history = level is AccessLevel.OWN and document is not None and document.superseded_at
        if document is None or document.trip_id != trip_id or hidden_history:
            raise _error(404, "DOCUMENT_NOT_FOUND", "Not found", "The document was not found.")
        try:
            # AI MODIFIED: Fictional local presentation evidence is fetched with bearer authorization.
            url = (
                f"/api/v1/finance/presentation-documents/{document.document_id}"
                if self._presentation_enabled and document.storage_path.startswith("presentation/")
                else self._storage.create_signed_url(document.storage_path, self._signed_url_ttl)
            )
        except StorageError as storage_error:
            raise _error(
                503,
                "STORAGE_UNAVAILABLE",
                "Service unavailable",
                "The document link could not be created. Try again shortly.",
            ) from storage_error
        self._record(principal, "or_document.url_issued", trip_id, {"kind": document.kind.value}, trace_id)
        self._unit_of_work.commit()
        return url, self._signed_url_ttl

    # ----- completion --------------------------------------------------------------

    def confirm_receipt(
        self,
        principal: Principal,
        level: AccessLevel,
        trip_id: UUID,
        received_at: datetime,
        idempotency_key: str,
        trace_id: str | None,
    ) -> TripView:
        trip = self._driver_trip(principal, level, trip_id)
        self._trips.lock_trip(trip_id)
        scope = f"trip.confirm_receipt:{trip_id}"
        previous = self._idempotency.get(idempotency_key, principal.employee_id)
        if previous is not None:
            if previous.scope != scope:
                raise _conflict("IDEMPOTENCY_KEY_REUSED", "This Idempotency-Key was used for another action.")
            return self._trip_service.view_for(self._load(trip_id))
        trip = self._load(trip_id)
        if trip.status is TripStatus.COMPLETED:
            raise _conflict("TRIP_ALREADY_COMPLETED", "Receipt was already confirmed for this trip.")
        signed = [
            one
            for one in self._documents.list_for_trip(trip_id, False)
            if one.kind is OrDocumentKind.SIGNED_OR
        ]
        if trip.status is not TripStatus.OR_UPLOADED or not signed:
            raise _conflict("SIGNED_OR_REQUIRED", "Upload the signed OR before confirming receipt.")
        self._validate_receipt_time(trip, received_at)
        self._trips.mark_receipt_confirmed(trip_id, principal.employee_id, as_utc(received_at))
        self._idempotency.save(idempotency_key, principal.employee_id, scope)
        self._synchronizer.refresh_truck(trip.truck_id)
        self._synchronizer.refresh_order(trip.order_id)
        stamped = any(
            one.kind is OrDocumentKind.STAMPED_COPY for one in self._documents.list_for_trip(trip_id, False)
        )
        self._record(principal, "trip.receipt_confirmed", trip_id, {"stamped_copy": stamped}, trace_id)
        self._unit_of_work.commit()
        # AI MODIFIED: Financial calculation starts after the operational transaction has committed.
        if self._financial_controls:
            self._financial_controls.after_completion(trip_id, trace_id)
        return self._trip_service.view_for(self._load(trip_id))

    def correct_confirmation(
        self, principal: Principal, trip_id: UUID, reason: str, trace_id: str | None
    ) -> TripView:
        # AI MODIFIED: Hold dependent ledgers in the same correction transaction.
        if self._financial_controls:
            self._financial_controls.lock_finances()
        trip = self._load(trip_id)
        self._trips.lock_trip(trip_id)
        trip = self._load(trip_id)
        if trip.status is not TripStatus.COMPLETED:
            raise _conflict("NOT_COMPLETED", "Only a completed trip's confirmation can be corrected.")
        others = self._trips.find_open_resource_trips(
            trip.truck_id, [trip.driver_id, *trip.helper_ids], trip.trip_id
        )
        # AI MODIFIED: Closed trips still prevent reopening an earlier receipt.
        departed_ids = self._trips.find_departed_trip_ids(
            trip.truck_id,
            [trip.driver_id, *trip.helper_ids],
            as_utc(trip.receipt_confirmed_at or trip.created_at),
            trip.trip_id,
        )
        if departed_ids:
            raise _conflict(
                "CORRECTION_NOT_POSSIBLE",
                "A later trip with the same truck or crew has already departed.",
                blocking_trip_ids=[str(identifier) for identifier in departed_ids],
            )
        reopened = list(
            dict.fromkeys(one.trip_id for one in others if one.status is TripStatus.CLEARED_FOR_DISPATCH)
        )
        for later_trip_id in reopened:
            self._trips.set_status(later_trip_id, TripStatus.ACCEPTED)
        if self._financial_controls:
            self._financial_controls.hold_receipt(trip_id, reason)
        self._trips.clear_receipt_confirmation(trip_id)
        self._synchronizer.refresh_truck(trip.truck_id)
        self._synchronizer.refresh_order(trip.order_id)
        self._record(
            principal,
            "trip.receipt_correction",
            trip_id,
            {"reason": reason, "reopened_clearances": [str(one) for one in reopened]},
            trace_id,
        )
        self._unit_of_work.commit()
        return self._trip_service.view_for(self._load(trip_id))

    # ----- helpers -----------------------------------------------------------------

    def _load(self, trip_id: UUID) -> Trip:
        trip = self._trips.get_by_id(trip_id)
        if trip is None:
            raise _trip_not_found()
        return trip

    def _crew_trip(self, principal: Principal, level: AccessLevel, trip_id: UUID) -> Trip:
        trip = self._load(trip_id)
        if level is AccessLevel.OWN and principal.employee_id not in (trip.driver_id, *trip.helper_ids):
            raise _trip_not_found()
        return trip

    def _driver_trip(self, principal: Principal, level: AccessLevel, trip_id: UUID) -> Trip:
        if level is not AccessLevel.OWN:
            raise _error(403, "PERMISSION_DENIED", "Forbidden", "Only the assigned driver can do this.")
        trip = self._load(trip_id)
        if trip.driver_id != principal.employee_id:
            raise _trip_not_found()
        return trip

    @staticmethod
    def _require_uploadable(trip: Trip, kind: OrDocumentKind) -> None:
        if kind is OrDocumentKind.SIGNED_OR:
            if trip.status is TripStatus.COMPLETED:
                raise _conflict(
                    "TRIP_ALREADY_COMPLETED", "The trip is completed; the signed OR can no longer change."
                )
            if trip.status not in (TripStatus.DELIVERED_OR_PENDING, TripStatus.OR_UPLOADED):
                raise _conflict("TRIP_NOT_DELIVERED", "Record the delivery before uploading the signed OR.")
        elif trip.status not in (TripStatus.OR_UPLOADED, TripStatus.COMPLETED):
            raise _conflict("SIGNED_OR_REQUIRED", "Upload the signed OR before adding a stamped copy.")

    def _validate_receipt_time(self, trip: Trip, received_at: datetime) -> None:
        received = as_utc(received_at)
        if received > self._clock() + CLOCK_SKEW:
            raise _error(
                422, "INVALID_RECEIPT_TIME", "Validation failed", "The receipt time cannot be in the future."
            )
        if trip.delivered_at is not None and received < as_utc(trip.delivered_at):
            raise _error(
                422,
                "INVALID_RECEIPT_TIME",
                "Validation failed",
                "The receipt time cannot be before the delivery was recorded.",
            )

    def _record(
        self,
        principal: Principal,
        action: str,
        trip_id: UUID,
        details: dict[str, object],
        trace_id: str | None,
    ) -> None:
        self._audit.append(principal.employee_id, action, "trip", str(trip_id), details, trace_id)
