# ===== AI GENERATED: TripRepository =====
# Purpose: SQLAlchemy implementation of ITripRepository
# Inputs: Session
# Returns: Trip entities (never ORM rows)
# Flow:
# 1. Trips are read together with their active crew rows
# 2. Crew changes end old rows and add new ones (history is kept)
# 3. Resource queries return open-trip facts for the dispatch rules


from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from ..Entity.dispatch import (
    OPEN_STATUSES,
    ResourceKind,
    ResourceTrip,
    Trip,
    TripStatus,
    TruckReplacement,
)
from .orm_models import (
    EmployeeRow,
    TripCrewRow,
    TripRow,
    TruckReplacementRow,
    TruckRow,
    utc_now,
)

_OPEN_VALUES = [status.value for status in OPEN_STATUSES]

# AI MODIFIED: Preserve historical departure restrictions when correcting receipts.


class TripRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _crew_for(self, trip_ids: list[UUID]) -> dict[UUID, tuple[UUID | None, tuple[UUID, ...]]]:
        if not trip_ids:
            return {}
        statement = (
            select(TripCrewRow)
            .where(TripCrewRow.trip_id.in_(trip_ids), TripCrewRow.removed_at.is_(None))
            .order_by(TripCrewRow.assigned_at, TripCrewRow.crew_entry_id)
        )
        drivers: dict[UUID, UUID] = {}
        helpers: dict[UUID, list[UUID]] = {}
        for row in self._session.scalars(statement).all():
            if row.crew_role == "DRIVER":
                drivers[row.trip_id] = row.employee_id
            else:
                helpers.setdefault(row.trip_id, []).append(row.employee_id)
        return {trip_id: (drivers.get(trip_id), tuple(helpers.get(trip_id, ()))) for trip_id in trip_ids}

    def _to_entities(self, rows: list[TripRow]) -> list[Trip]:
        crew = self._crew_for([row.trip_id for row in rows])
        trips: list[Trip] = []
        for row in rows:
            driver_id, helper_ids = crew[row.trip_id]
            trips.append(
                Trip(
                    trip_id=row.trip_id,
                    order_id=row.order_id,
                    truck_id=row.truck_id,
                    load_tons=Decimal(row.load_tons),
                    status=TripStatus(row.status),
                    driver_id=driver_id,  # type: ignore[arg-type]
                    helper_ids=helper_ids,
                    accepted_at=row.accepted_at,
                    cleared_at=row.cleared_at,
                    departed_at=row.departed_at,
                    delivered_at=row.delivered_at,
                    closed_reason=row.closed_reason,
                    created_by=row.created_by,
                    created_at=row.created_at,
                    or_uploaded_at=row.or_uploaded_at,
                    or_uploaded_by=row.or_uploaded_by,
                    receipt_confirmed_at=row.receipt_confirmed_at,
                    receipt_confirmed_by=row.receipt_confirmed_by,
                    receipt_received_at=row.receipt_received_at,
                )
            )
        return trips

    def _one(self, row: TripRow | None) -> Trip | None:
        return self._to_entities([row])[0] if row is not None else None

    def get_by_id(self, trip_id: UUID) -> Trip | None:
        return self._one(self._session.get(TripRow, trip_id))

    def list_page(
        self,
        limit: int,
        offset: int,
        status: TripStatus | None,
        order_id: UUID | None,
        truck_id: UUID | None,
    ) -> list[Trip]:
        statement = select(TripRow).order_by(TripRow.created_at.desc(), TripRow.trip_id)
        if status is not None:
            statement = statement.where(TripRow.status == status.value)
        if order_id is not None:
            statement = statement.where(TripRow.order_id == order_id)
        if truck_id is not None:
            statement = statement.where(TripRow.truck_id == truck_id)
        return self._to_entities(list(self._session.scalars(statement.limit(limit).offset(offset))))

    def list_assigned(
        self, employee_id: UUID, limit: int, offset: int, status: TripStatus | None
    ) -> list[Trip]:
        statement = (
            select(TripRow)
            .join(TripCrewRow, TripCrewRow.trip_id == TripRow.trip_id)
            .where(TripCrewRow.employee_id == employee_id, TripCrewRow.removed_at.is_(None))
            .order_by(TripRow.created_at.desc(), TripRow.trip_id)
        )
        if status is not None:
            statement = statement.where(TripRow.status == status.value)
        return self._to_entities(list(self._session.scalars(statement.limit(limit).offset(offset))))

    def list_for_order(self, order_id: UUID) -> list[Trip]:
        statement = select(TripRow).where(TripRow.order_id == order_id).order_by(TripRow.created_at)
        return self._to_entities(list(self._session.scalars(statement)))

    def _add_crew(self, trip_id: UUID, driver_id: UUID, helper_ids: tuple[UUID, ...]) -> None:
        self._session.add(TripCrewRow(trip_id=trip_id, employee_id=driver_id, crew_role="DRIVER"))
        for helper_id in helper_ids:
            self._session.add(TripCrewRow(trip_id=trip_id, employee_id=helper_id, crew_role="HELPER"))

    def create(
        self,
        order_id: UUID,
        truck_id: UUID,
        load_tons: Decimal,
        driver_id: UUID,
        helper_ids: tuple[UUID, ...],
        created_by: UUID | None,
    ) -> Trip:
        row = TripRow(
            order_id=order_id,
            truck_id=truck_id,
            load_tons=load_tons,
            status=TripStatus.SCHEDULED.value,
            created_by=created_by,
        )
        self._session.add(row)
        self._session.flush()
        self._add_crew(row.trip_id, driver_id, helper_ids)
        self._session.flush()
        self._session.refresh(row)
        return self._one(row)  # type: ignore[return-value]

    def replace_crew(self, trip_id: UUID, driver_id: UUID, helper_ids: tuple[UUID, ...]) -> Trip | None:
        row = self._session.get(TripRow, trip_id)
        if row is None:
            return None
        self._session.execute(
            update(TripCrewRow)
            .where(TripCrewRow.trip_id == trip_id, TripCrewRow.removed_at.is_(None))
            .values(removed_at=utc_now())
        )
        self._add_crew(trip_id, driver_id, helper_ids)
        self._session.flush()
        return self._one(row)

    def set_status(self, trip_id: UUID, status: TripStatus) -> Trip | None:
        row = self._session.get(TripRow, trip_id)
        if row is None:
            return None
        row.status = status.value
        now = utc_now()
        if status is TripStatus.SCHEDULED:
            row.accepted_at = None
            row.cleared_at = None
        elif status is TripStatus.ACCEPTED:
            row.accepted_at = row.accepted_at or now
            row.cleared_at = None
        elif status is TripStatus.CLEARED_FOR_DISPATCH:
            row.cleared_at = now
        elif status is TripStatus.IN_TRANSIT:
            row.departed_at = now
        elif status is TripStatus.DELIVERED_OR_PENDING:
            row.delivered_at = now
        self._session.flush()
        return self._one(row)

    def close(self, trip_id: UUID, status: TripStatus, reason: str) -> Trip | None:
        row = self._session.get(TripRow, trip_id)
        if row is None:
            return None
        row.status = status.value
        row.closed_reason = reason
        self._session.flush()
        return self._one(row)

    def set_truck(self, trip_id: UUID, truck_id: UUID) -> Trip | None:
        row = self._session.get(TripRow, trip_id)
        if row is None:
            return None
        row.truck_id = truck_id
        self._session.flush()
        return self._one(row)

    def record_replacement(
        self,
        trip_id: UUID,
        original_truck_id: UUID,
        replacement_truck_id: UUID,
        reason: str,
        replaced_by: UUID | None,
    ) -> TruckReplacement:
        row = TruckReplacementRow(
            trip_id=trip_id,
            original_truck_id=original_truck_id,
            replacement_truck_id=replacement_truck_id,
            reason=reason,
            replaced_by=replaced_by,
        )
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return TruckReplacement(
            replacement_id=row.replacement_id,
            trip_id=row.trip_id,
            original_truck_id=row.original_truck_id,
            replacement_truck_id=row.replacement_truck_id,
            reason=row.reason,
            effective_at=row.effective_at,
            replaced_by=row.replaced_by,
        )

    def find_open_resource_trips(
        self, truck_id: UUID, employee_ids: Iterable[UUID], exclude_trip_id: UUID | None
    ) -> list[ResourceTrip]:
        found: list[ResourceTrip] = []
        truck_statement = select(TripRow).where(
            TripRow.truck_id == truck_id, TripRow.status.in_(_OPEN_VALUES)
        )
        for row in self._session.scalars(truck_statement):
            found.append(ResourceTrip(row.trip_id, TripStatus(row.status), ResourceKind.TRUCK, truck_id))
        member_ids = list(employee_ids)
        if member_ids:
            crew_statement = (
                select(TripRow, TripCrewRow)
                .join(TripCrewRow, TripCrewRow.trip_id == TripRow.trip_id)
                .where(
                    TripCrewRow.employee_id.in_(member_ids),
                    TripCrewRow.removed_at.is_(None),
                    TripRow.status.in_(_OPEN_VALUES),
                )
            )
            for trip_row, crew_row in self._session.execute(crew_statement).all():
                found.append(
                    ResourceTrip(
                        trip_row.trip_id,
                        TripStatus(trip_row.status),
                        ResourceKind(crew_row.crew_role),
                        crew_row.employee_id,
                    )
                )
        return [one for one in found if one.trip_id != exclude_trip_id]

    def find_departed_trip_ids(
        self, truck_id: UUID, employee_ids: Iterable[UUID], since: datetime, exclude_trip_id: UUID
    ) -> list[UUID]:
        """Find later departures involving a resource, including failed/completed trips."""
        crew_trip_ids = select(TripCrewRow.trip_id).where(
            TripCrewRow.employee_id.in_(list(employee_ids)), TripCrewRow.removed_at.is_(None)
        )
        replaced_trip_ids = select(TruckReplacementRow.trip_id).where(
            or_(
                TruckReplacementRow.original_truck_id == truck_id,
                TruckReplacementRow.replacement_truck_id == truck_id,
            )
        )
        statement = (
            select(TripRow.trip_id)
            .where(
                TripRow.trip_id != exclude_trip_id,
                TripRow.departed_at >= since,
                or_(
                    TripRow.truck_id == truck_id,
                    TripRow.trip_id.in_(crew_trip_ids),
                    TripRow.trip_id.in_(replaced_trip_ids),
                ),
            )
            .order_by(TripRow.departed_at, TripRow.trip_id)
        )
        return list(self._session.scalars(statement))

    def list_open_resource_trips(self) -> list[ResourceTrip]:
        found: list[ResourceTrip] = []
        for row in self._session.scalars(select(TripRow).where(TripRow.status.in_(_OPEN_VALUES))):
            found.append(ResourceTrip(row.trip_id, TripStatus(row.status), ResourceKind.TRUCK, row.truck_id))
        crew_statement = (
            select(TripRow, TripCrewRow)
            .join(TripCrewRow, TripCrewRow.trip_id == TripRow.trip_id)
            .where(TripCrewRow.removed_at.is_(None), TripRow.status.in_(_OPEN_VALUES))
        )
        for trip_row, crew_row in self._session.execute(crew_statement).all():
            found.append(
                ResourceTrip(
                    trip_row.trip_id,
                    TripStatus(trip_row.status),
                    ResourceKind(crew_row.crew_role),
                    crew_row.employee_id,
                )
            )
        return found

    def open_truck_statuses(self, truck_id: UUID) -> list[TripStatus]:
        statement = select(TripRow.status).where(
            TripRow.truck_id == truck_id, TripRow.status.in_(_OPEN_VALUES)
        )
        return [TripStatus(value) for value in self._session.scalars(statement).all()]

    def lock_resources(self, truck_ids: Iterable[UUID], employee_ids: Iterable[UUID]) -> None:
        """Row locks in a fixed order (trucks, then employees by id) to avoid deadlocks."""
        ordered_trucks = sorted(set(truck_ids), key=str)
        ordered_people = sorted(set(employee_ids), key=str)
        if ordered_trucks:
            self._session.execute(
                select(TruckRow.truck_id).where(TruckRow.truck_id.in_(ordered_trucks)).with_for_update()
            ).all()
        if ordered_people:
            self._session.execute(
                select(EmployeeRow.employee_id)
                .where(EmployeeRow.employee_id.in_(ordered_people))
                .with_for_update()
            ).all()

    # AI MODIFIED: Expose retained truck replacement history for authorized reports.
    def list_replacements(self, trip_id: UUID) -> list[TruckReplacement]:
        return self.list_replacements_for_trips([trip_id])

    def list_replacements_for_trips(self, trip_ids: list[UUID]) -> list[TruckReplacement]:
        if not trip_ids:
            return []
        rows = self._session.scalars(
            select(TruckReplacementRow)
            .where(TruckReplacementRow.trip_id.in_(trip_ids))
            .order_by(TruckReplacementRow.effective_at)
        ).all()
        return [
            TruckReplacement(
                row.replacement_id,
                row.trip_id,
                row.original_truck_id,
                row.replacement_truck_id,
                row.reason,
                row.effective_at,
                row.replaced_by,
            )
            for row in rows
        ]

    def lock_trip(self, trip_id: UUID) -> None:
        self._session.execute(
            select(TripRow.trip_id).where(TripRow.trip_id == trip_id).with_for_update()
        ).all()

    def mark_or_uploaded(self, trip_id: UUID, uploaded_by: UUID | None) -> Trip | None:
        row = self._session.get(TripRow, trip_id)
        if row is None:
            return None
        row.status = TripStatus.OR_UPLOADED.value
        row.or_uploaded_at = utc_now()
        row.or_uploaded_by = uploaded_by
        self._session.flush()
        return self._one(row)

    def mark_receipt_confirmed(
        self, trip_id: UUID, confirmed_by: UUID | None, received_at: datetime
    ) -> Trip | None:
        row = self._session.get(TripRow, trip_id)
        if row is None:
            return None
        row.status = TripStatus.COMPLETED.value
        row.receipt_confirmed_at = utc_now()
        row.receipt_confirmed_by = confirmed_by
        row.receipt_received_at = received_at
        self._session.flush()
        return self._one(row)

    def clear_receipt_confirmation(self, trip_id: UUID) -> Trip | None:
        row = self._session.get(TripRow, trip_id)
        if row is None:
            return None
        row.status = TripStatus.OR_UPLOADED.value
        row.receipt_confirmed_at = None
        row.receipt_confirmed_by = None
        row.receipt_received_at = None
        self._session.flush()
        return self._one(row)
