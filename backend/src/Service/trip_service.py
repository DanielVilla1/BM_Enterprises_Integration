# ===== AI GENERATED: TripService =====
# Purpose: Assign trips and move them through the dispatch workflow (spec 4, 5)
# Inputs: trip, order, truck, employee, license repositories, audit, unit of work
# Returns: TripView entities or BusinessRuleError (409 with a stable code)
# Flow:
# 1. Assign: capacity, order load, truck condition, crew, license, availability
# 2. Transitions: accept, clear dispatch, depart, deliver; cancel / fail
# 3. Crew change and truck replacement never bypass the OR dispatch restriction
# 4. Order and truck statuses are re-derived from trips after every change

from collections.abc import Callable
from datetime import date
from decimal import Decimal
from uuid import UUID

from ..Contract.i_audit_repository import IAuditRepository
from ..Contract.i_employee_repository import IEmployeeRepository
from ..Contract.i_fleet_repositories import IDriverLicenseRepository, ITruckRepository
from ..Contract.i_operations_repositories import IDeliveryOrderRepository
from ..Contract.i_trip_repository import ITripRepository
from ..Contract.i_unit_of_work import IUnitOfWork
from ..Entity.access import AccessLevel, RoleCode
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.clock import manila_today
from ..Entity.dispatch import (
    MAXIMUM_HELPERS,
    MINIMUM_HELPERS,
    PRE_DEPARTURE_STATUSES,
    PRE_UPLOAD_STATUSES,
    REPLACEABLE_TRUCK_STATUSES,
    DispatchResources,
    ResourceAvailability,
    Trip,
    TripStatus,
    TripView,
    assigned_load,
    blocking_trips,
    derive_order_status,
    derive_truck_status,
)
from ..Entity.employee import Employee, Principal
from ..Entity.fleet import LicenseValidity, Truck, TruckStatus, license_validity
from ..Entity.operations import DeliveryOrder, OrderStatus

DISPATCH_BLOCKED_MESSAGE = (
    "Dispatch blocked: The previous trip's OR has not yet been marked as received by the steel company."
)
FINAL_ORDER_STATUSES = (OrderStatus.CANCELLED, OrderStatus.COMPLETED)


def _error(status: int, code: str, title: str, detail: str, **extensions: object) -> BusinessRuleError:
    return BusinessRuleError(status, code, title, detail, None, dict(extensions) or None)


def _conflict(code: str, detail: str, **extensions: object) -> BusinessRuleError:
    return _error(409, code, "Conflict", detail, **extensions)


def _not_found(code: str, detail: str) -> BusinessRuleError:
    return _error(404, code, "Not found", detail)


class TripService:
    def __init__(
        self,
        trips: ITripRepository,
        orders: IDeliveryOrderRepository,
        trucks: ITruckRepository,
        employees: IEmployeeRepository,
        licenses: IDriverLicenseRepository,
        audit: IAuditRepository,
        unit_of_work: IUnitOfWork,
        today_provider: Callable[[], date] = manila_today,
    ) -> None:
        self._trips = trips
        self._orders = orders
        self._trucks = trucks
        self._employees = employees
        self._licenses = licenses
        self._audit = audit
        self._unit_of_work = unit_of_work
        self._today_provider = today_provider

    # ----- queries -----------------------------------------------------------------

    def list_trips(
        self,
        limit: int,
        offset: int,
        status: TripStatus | None,
        order_id: UUID | None,
        truck_id: UUID | None,
    ) -> list[TripView]:
        return self._views(self._trips.list_page(limit, offset, status, order_id, truck_id))

    def list_assigned(
        self, principal: Principal, level: AccessLevel, limit: int, offset: int, status: TripStatus | None
    ) -> list[TripView]:
        if level is AccessLevel.OWN:
            return self._views(self._trips.list_assigned(principal.employee_id, limit, offset, status))
        return self._views(self._trips.list_page(limit, offset, status, None, None))

    def get_trip(self, principal: Principal, level: AccessLevel, trip_id: UUID) -> TripView:
        trip = self._load(trip_id)
        if level is AccessLevel.OWN and principal.employee_id not in (trip.driver_id, *trip.helper_ids):
            raise self._trip_not_found()
        return self._view(trip)

    def list_resources(self) -> DispatchResources:
        open_trips = self._trips.list_open_resource_trips()
        pre_upload_by_resource: dict[UUID, UUID] = {}
        for resource_trip in open_trips:
            if resource_trip.status in PRE_UPLOAD_STATUSES:
                pre_upload_by_resource.setdefault(resource_trip.resource_id, resource_trip.trip_id)
        today = self._today_provider()

        def availability(
            resource_id: UUID, name: str, reason: str | None, capacity: Decimal | None = None
        ) -> ResourceAvailability:
            blocker = pre_upload_by_resource.get(resource_id)
            final_reason = reason or ("IN_PROGRESS_TRIP" if blocker else None)
            return ResourceAvailability(
                resource_id, name, final_reason is None, final_reason, blocker, capacity
            )

        trucks = [
            availability(
                truck.truck_id,
                truck.plate_number,
                "MAINTENANCE" if truck.status is TruckStatus.MAINTENANCE else None,
                truck.capacity_tons,
            )
            for truck in self._trucks.list_page(100, 0, None, True)
        ]
        drivers = [
            availability(person.employee_id, person.full_name, self._license_reason(person, today))
            for person in self._employees.list_by_role(RoleCode.DRIVER, True)
        ]
        helpers = [
            availability(person.employee_id, person.full_name, None)
            for person in self._employees.list_by_role(RoleCode.HELPER, True)
        ]
        return DispatchResources(trucks, drivers, helpers)

    # ----- assignment --------------------------------------------------------------

    def create_trip(
        self,
        principal: Principal,
        order_id: UUID,
        truck_id: UUID,
        driver_id: UUID,
        helper_ids: tuple[UUID, ...],
        load_tons: Decimal,
        trace_id: str | None,
    ) -> TripView:
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise _not_found("ORDER_NOT_FOUND", "The delivery order was not found.")
        if order.status in FINAL_ORDER_STATUSES:
            raise _conflict("ORDER_NOT_ASSIGNABLE", "This order can no longer receive trips.")
        self._trips.lock_resources([truck_id], [driver_id, *helper_ids])
        self._validate_truck(truck_id, load_tons)
        remaining = order.total_weight_tons - assigned_load(self._trips.list_for_order(order_id))
        if load_tons > remaining:
            raise _conflict(
                "LOAD_EXCEEDS_ORDER", f"The load exceeds the order's unassigned weight ({remaining} t)."
            )
        self._validate_crew(driver_id, helper_ids, max(self._today_provider(), order.scheduled_date))
        self._ensure_available(truck_id, [driver_id, *helper_ids], None)
        trip = self._trips.create(order_id, truck_id, load_tons, driver_id, helper_ids, principal.employee_id)
        self._refresh_truck(truck_id)
        self._refresh_order(order_id)
        self._record(principal, "trip.created", trip.trip_id, {}, trace_id)
        self._unit_of_work.commit()
        return self._view(trip)

    def change_crew(
        self,
        principal: Principal,
        trip_id: UUID,
        driver_id: UUID,
        helper_ids: tuple[UUID, ...],
        trace_id: str | None,
    ) -> TripView:
        trip = self._load(trip_id)
        if trip.status not in PRE_DEPARTURE_STATUSES:
            raise _conflict("CREW_LOCKED", "The crew can only change before the truck departs.")
        order = self._require_order(trip.order_id)
        self._trips.lock_resources([trip.truck_id], [driver_id, *helper_ids])
        self._validate_crew(driver_id, helper_ids, max(self._today_provider(), order.scheduled_date))
        self._ensure_available(trip.truck_id, [driver_id, *helper_ids], trip.trip_id)
        if driver_id == trip.driver_id and set(helper_ids) == set(trip.helper_ids):
            return self._view(trip)
        self._trips.replace_crew(trip_id, driver_id, helper_ids)
        driver_changed = driver_id != trip.driver_id
        if driver_changed:
            self._trips.set_status(trip_id, TripStatus.SCHEDULED)
        elif trip.status is TripStatus.CLEARED_FOR_DISPATCH:
            self._trips.set_status(trip_id, TripStatus.ACCEPTED)
        self._record(principal, "trip.crew_changed", trip_id, {"driver_changed": driver_changed}, trace_id)
        self._unit_of_work.commit()
        return self._view(self._load(trip_id))

    def replace_truck(
        self,
        principal: Principal,
        trip_id: UUID,
        replacement_truck_id: UUID,
        reason: str,
        original_needs_maintenance: bool,
        trace_id: str | None,
    ) -> TripView:
        trip = self._load(trip_id)
        if trip.status not in REPLACEABLE_TRUCK_STATUSES:
            raise _conflict(
                "TRIP_NOT_REPLACEABLE", "The truck can only be replaced before or during transit."
            )
        if replacement_truck_id == trip.truck_id:
            raise _conflict("SAME_TRUCK", "The replacement must be a different truck.")
        self._trips.lock_resources([trip.truck_id, replacement_truck_id], [])
        self._validate_truck(replacement_truck_id, trip.load_tons)
        departing = trip.status in (TripStatus.CLEARED_FOR_DISPATCH, TripStatus.IN_TRANSIT)
        self._ensure_truck_free(replacement_truck_id, trip.trip_id, departing)
        original_truck_id = trip.truck_id
        self._trips.set_truck(trip_id, replacement_truck_id)
        self._trips.record_replacement(
            trip_id, original_truck_id, replacement_truck_id, reason, principal.employee_id
        )
        if original_needs_maintenance:
            self._trucks.open_maintenance(original_truck_id, reason, principal.employee_id)
            self._trucks.set_status(original_truck_id, TruckStatus.MAINTENANCE)
        else:
            self._refresh_truck(original_truck_id)
        self._refresh_truck(replacement_truck_id)
        self._record(
            principal,
            "trip.truck_replaced",
            trip_id,
            {"original_needs_maintenance": original_needs_maintenance},
            trace_id,
        )
        self._unit_of_work.commit()
        return self._view(self._load(trip_id))

    # ----- progress ----------------------------------------------------------------

    def accept_trip(
        self, principal: Principal, level: AccessLevel, trip_id: UUID, trace_id: str | None
    ) -> TripView:
        trip = self._driver_trip(principal, level, trip_id)
        self._require_status(trip, {TripStatus.SCHEDULED}, "TRIP_NOT_SCHEDULED")
        self._trips.set_status(trip_id, TripStatus.ACCEPTED)
        self._record(principal, "trip.accepted", trip_id, {}, trace_id)
        self._unit_of_work.commit()
        return self._view(self._load(trip_id))

    def clear_dispatch(self, principal: Principal, trip_id: UUID, trace_id: str | None) -> TripView:
        trip = self._load(trip_id)
        self._require_status(trip, {TripStatus.ACCEPTED}, "TRIP_NOT_ACCEPTED")
        self._trips.lock_resources([trip.truck_id], [trip.driver_id, *trip.helper_ids])
        self._ensure_dispatchable(trip)
        self._trips.set_status(trip_id, TripStatus.CLEARED_FOR_DISPATCH)
        self._record(principal, "trip.dispatch_cleared", trip_id, {}, trace_id)
        self._unit_of_work.commit()
        return self._view(self._load(trip_id))

    def depart_trip(
        self, principal: Principal, level: AccessLevel, trip_id: UUID, trace_id: str | None
    ) -> TripView:
        trip = self._driver_trip(principal, level, trip_id)
        self._require_status(trip, {TripStatus.CLEARED_FOR_DISPATCH}, "TRIP_NOT_CLEARED")
        self._trips.lock_resources([trip.truck_id], [trip.driver_id, *trip.helper_ids])
        self._ensure_dispatchable(trip)
        self._trips.set_status(trip_id, TripStatus.IN_TRANSIT)
        self._refresh_truck(trip.truck_id)
        self._refresh_order(trip.order_id)
        self._record(principal, "trip.departed", trip_id, {}, trace_id)
        self._unit_of_work.commit()
        return self._view(self._load(trip_id))

    def record_delivery(
        self, principal: Principal, level: AccessLevel, trip_id: UUID, trace_id: str | None
    ) -> TripView:
        trip = self._driver_trip(principal, level, trip_id)
        self._require_status(trip, {TripStatus.IN_TRANSIT}, "TRIP_NOT_IN_TRANSIT")
        self._trips.set_status(trip_id, TripStatus.DELIVERED_OR_PENDING)
        self._refresh_truck(trip.truck_id)
        self._record(principal, "trip.delivered", trip_id, {}, trace_id)
        self._unit_of_work.commit()
        return self._view(self._load(trip_id))

    def cancel_trip(self, principal: Principal, trip_id: UUID, reason: str, trace_id: str | None) -> TripView:
        trip = self._load(trip_id)
        self._require_status(trip, PRE_DEPARTURE_STATUSES, "TRIP_NOT_CANCELLABLE")
        return self._close(principal, trip, TripStatus.CANCELLED, reason, "trip.cancelled", trace_id)

    def fail_trip(self, principal: Principal, trip_id: UUID, reason: str, trace_id: str | None) -> TripView:
        trip = self._load(trip_id)
        self._require_status(
            trip, {TripStatus.IN_TRANSIT, TripStatus.DELIVERED_OR_PENDING}, "TRIP_NOT_FAILABLE"
        )
        return self._close(principal, trip, TripStatus.FAILED, reason, "trip.failed", trace_id)

    # ----- rules -------------------------------------------------------------------

    def _close(
        self,
        principal: Principal,
        trip: Trip,
        status: TripStatus,
        reason: str,
        action: str,
        trace_id: str | None,
    ) -> TripView:
        self._trips.close(trip.trip_id, status, reason)
        self._refresh_truck(trip.truck_id)
        self._refresh_order(trip.order_id)
        self._record(principal, action, trip.trip_id, {}, trace_id)
        self._unit_of_work.commit()
        return self._view(self._load(trip.trip_id))

    def _validate_truck(self, truck_id: UUID, load_tons: Decimal) -> Truck:
        truck = self._trucks.get_by_id(truck_id)
        if truck is None:
            raise _not_found("TRUCK_NOT_FOUND", "The truck was not found.")
        if not truck.is_active or truck.status is TruckStatus.MAINTENANCE:
            raise _conflict("TRUCK_UNAVAILABLE", "The truck is retired or in maintenance.")
        if load_tons > truck.capacity_tons:
            raise _conflict(
                "CAPACITY_EXCEEDED", f"The load exceeds the truck's capacity ({truck.capacity_tons} t)."
            )
        return truck

    def _validate_crew(self, driver_id: UUID, helper_ids: tuple[UUID, ...], reference_date: date) -> None:
        if not MINIMUM_HELPERS <= len(helper_ids) <= MAXIMUM_HELPERS:
            raise _error(
                422,
                "CREW_SIZE_INVALID",
                "Validation failed",
                "A trip needs one driver and one or two helpers.",
            )
        if len(set(helper_ids)) != len(helper_ids) or driver_id in helper_ids:
            raise _error(422, "CREW_DUPLICATE", "Validation failed", "Each crew member may appear only once.")
        driver = self._require_active(driver_id)
        if RoleCode.DRIVER not in driver.role_codes:
            raise _conflict("NOT_A_DRIVER", "The selected driver does not have the Driver role.")
        stored = self._licenses.get_by_employee(driver_id)
        if stored is None:
            raise _conflict("DRIVER_LICENSE_MISSING", "The driver has no license on record.")
        if license_validity(stored.expiry_date, reference_date) is LicenseValidity.EXPIRED:
            raise _conflict("DRIVER_LICENSE_EXPIRED", "The driver's license is expired for this trip date.")
        for helper_id in helper_ids:
            helper = self._require_active(helper_id)
            if RoleCode.HELPER not in helper.role_codes:
                raise _conflict("NOT_A_HELPER", "A selected helper does not have the Helper role.")

    def _require_active(self, employee_id: UUID) -> Employee:
        employee = self._employees.get_by_id(employee_id)
        if employee is None:
            raise _not_found("EMPLOYEE_NOT_FOUND", "A crew member was not found.")
        if not employee.is_active:
            raise _conflict("EMPLOYEE_INACTIVE", "A crew member is not active.")
        return employee

    def _ensure_available(self, truck_id: UUID, crew_ids: list[UUID], exclude_trip_id: UUID | None) -> None:
        resource_trips = self._trips.find_open_resource_trips(truck_id, crew_ids, exclude_trip_id)
        blockers = blocking_trips(resource_trips, PRE_UPLOAD_STATUSES)
        if blockers:
            raise _conflict(
                "RESOURCE_UNAVAILABLE",
                "The truck or a crew member already has an assigned trip that has not reached OR upload.",
                blocking_trip_ids=[str(one.trip_id) for one in blockers],
            )

    def _ensure_truck_free(self, truck_id: UUID, trip_id: UUID, departing: bool) -> None:
        resource_trips = self._trips.find_open_resource_trips(truck_id, [], trip_id)
        if departing and resource_trips:
            raise _conflict(
                "DISPATCH_BLOCKED",
                DISPATCH_BLOCKED_MESSAGE,
                blocking_trip_ids=[str(one.trip_id) for one in resource_trips],
            )
        blockers = blocking_trips(resource_trips, PRE_UPLOAD_STATUSES)
        if blockers:
            raise _conflict(
                "RESOURCE_UNAVAILABLE",
                "The replacement truck already has an assigned trip.",
                blocking_trip_ids=[str(one.trip_id) for one in blockers],
            )

    def _ensure_dispatchable(self, trip: Trip) -> None:
        resource_trips = self._trips.find_open_resource_trips(
            trip.truck_id, [trip.driver_id, *trip.helper_ids], trip.trip_id
        )
        if resource_trips:
            only_receipt_pending = all(one.status is TripStatus.OR_UPLOADED for one in resource_trips)
            message = (
                DISPATCH_BLOCKED_MESSAGE
                if only_receipt_pending
                else "Dispatch blocked: The truck or a crew member is still on another trip."
            )
            blocker_ids = list(dict.fromkeys(str(one.trip_id) for one in resource_trips))
            raise _conflict("DISPATCH_BLOCKED", message, blocking_trip_ids=blocker_ids)

    def _license_reason(self, person: Employee, today: date) -> str | None:
        stored = self._licenses.get_by_employee(person.employee_id)
        if stored is None:
            return "LICENSE_MISSING"
        if license_validity(stored.expiry_date, today) is LicenseValidity.EXPIRED:
            return "LICENSE_EXPIRED"
        return None

    def _refresh_truck(self, truck_id: UUID) -> None:
        truck = self._trucks.get_by_id(truck_id)
        if truck is None or truck.status is TruckStatus.MAINTENANCE:
            return
        derived = derive_truck_status(self._trips.open_truck_statuses(truck_id))
        if derived is not truck.status:
            self._trucks.set_status(truck_id, derived)

    def _refresh_order(self, order_id: UUID) -> None:
        order = self._orders.get_by_id(order_id)
        if order is None or order.status is OrderStatus.CANCELLED:
            return
        derived = derive_order_status(order.total_weight_tons, self._trips.list_for_order(order_id))
        if derived is not order.status:
            self._orders.set_status(order_id, derived)

    def _driver_trip(self, principal: Principal, level: AccessLevel, trip_id: UUID) -> Trip:
        if level is not AccessLevel.OWN:
            raise _error(403, "PERMISSION_DENIED", "Forbidden", "Only the assigned driver can do this.")
        trip = self._load(trip_id)
        if trip.driver_id != principal.employee_id:
            raise self._trip_not_found()
        return trip

    @staticmethod
    def _require_status(trip: Trip, allowed: set[TripStatus] | frozenset[TripStatus], code: str) -> None:
        if trip.status not in allowed:
            raise _conflict(code, f"The trip is {trip.status.value} and cannot take this action.")

    # ----- helpers -----------------------------------------------------------------

    @staticmethod
    def _trip_not_found() -> BusinessRuleError:
        return _not_found("TRIP_NOT_FOUND", "The trip was not found.")

    def _load(self, trip_id: UUID) -> Trip:
        trip = self._trips.get_by_id(trip_id)
        if trip is None:
            raise self._trip_not_found()
        return trip

    def _require_order(self, order_id: UUID) -> DeliveryOrder:
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise _not_found("ORDER_NOT_FOUND", "The delivery order was not found.")
        return order

    def _view(self, trip: Trip) -> TripView:
        order = self._require_order(trip.order_id)
        return TripView(trip, order.scheduled_date, order.pickup_location, order.delivery_location)

    def _views(self, trips: list[Trip]) -> list[TripView]:
        return [self._view(trip) for trip in trips]

    def _record(
        self,
        principal: Principal,
        action: str,
        trip_id: UUID,
        details: dict[str, object],
        trace_id: str | None,
    ) -> None:
        self._audit.append(principal.employee_id, action, "trip", str(trip_id), details, trace_id)
