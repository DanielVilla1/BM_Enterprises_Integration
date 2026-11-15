# ===== AI GENERATED: ClientService =====
# Purpose: Client (steel company and others) records
# Inputs: client repository, audit, unit of work
# Returns: Client entities or BusinessRuleError
# Flow:
# 1. Enforce unique names (case-insensitive)
# 2. Write an audit record with the changed field names only
# 3. Commit once

from collections.abc import Mapping
from uuid import UUID

from ..Contract.i_audit_repository import IAuditRepository
from ..Contract.i_operations_repositories import IClientRepository
from ..Contract.i_unit_of_work import IUnitOfWork
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.employee import Principal
from ..Entity.operations import Client


def _not_found() -> BusinessRuleError:
    return BusinessRuleError(404, "CLIENT_NOT_FOUND", "Not found", "The client was not found.")


class ClientService:
    def __init__(
        self, clients: IClientRepository, audit: IAuditRepository, unit_of_work: IUnitOfWork
    ) -> None:
        self._clients = clients
        self._audit = audit
        self._unit_of_work = unit_of_work

    def list_clients(self, limit: int, offset: int, only_active: bool | None) -> list[Client]:
        return self._clients.list_page(limit, offset, only_active)

    def get_client(self, client_id: UUID) -> Client:
        client = self._clients.get_by_id(client_id)
        if client is None:
            raise _not_found()
        return client

    def create_client(
        self,
        principal: Principal,
        name: str,
        address: str | None,
        contact_person: str | None,
        contact_phone: str | None,
        trace_id: str | None,
    ) -> Client:
        self._ensure_name_free(name, owner_id=None)
        client = self._clients.create(name, address, contact_person, contact_phone)
        self._record(principal, "client.created", client.client_id, {}, trace_id)
        self._unit_of_work.commit()
        return client

    def update_client(
        self, principal: Principal, client_id: UUID, changes: Mapping[str, object], trace_id: str | None
    ) -> Client:
        if self._clients.get_by_id(client_id) is None:
            raise _not_found()
        new_name = changes.get("name")
        if isinstance(new_name, str):
            self._ensure_name_free(new_name, owner_id=client_id)
        updated = self._clients.update(client_id, changes)
        if updated is None:
            raise _not_found()
        self._record(principal, "client.updated", client_id, {"fields": sorted(changes)}, trace_id)
        self._unit_of_work.commit()
        return updated

    def _ensure_name_free(self, name: str, owner_id: UUID | None) -> None:
        holder = self._clients.get_by_name(name)
        if holder is not None and holder.client_id != owner_id:
            raise BusinessRuleError(
                409, "CLIENT_NAME_EXISTS", "Conflict", "A client with that name already exists."
            )

    def _record(
        self,
        principal: Principal,
        action: str,
        client_id: UUID,
        details: dict[str, object],
        trace_id: str | None,
    ) -> None:
        self._audit.append(principal.employee_id, action, "client", str(client_id), details, trace_id)
