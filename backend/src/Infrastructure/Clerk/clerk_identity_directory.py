# ===== AI GENERATED: ClerkIdentityDirectory =====
# Purpose: List Clerk users through the Backend API (server-side secret key)
# Inputs: secret key, API base URL
# Returns: DirectoryUser list or IdentityDirectoryError
# Flow:
# 1. Page through GET /v1/users with a timeout and bounded retries
# 2. Validate every field before use (OWASP API10)
# 3. Never return partial results: any failure raises

import time
from collections.abc import Callable

import httpx

from ...Contract.i_identity_directory import DirectoryUser, IdentityDirectoryError
from ...Entity.clerk_user import verified_primary_email

PAGE_SIZE = 100
MAXIMUM_PAGES = 100
MAXIMUM_ATTEMPTS = 3
REQUEST_TIMEOUT_SECONDS = 10.0


class ClerkIdentityDirectory:
    """Implements IIdentityDirectory."""

    def __init__(
        self,
        secret_key: str,
        api_base_url: str,
        transport: httpx.BaseTransport | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self._secret_key = secret_key
        self._api_base_url = api_base_url.rstrip("/")
        self._transport = transport
        self._sleeper = sleeper

    def list_users(self) -> list[DirectoryUser]:
        if not self._secret_key:
            raise IdentityDirectoryError("Clerk secret key is not configured")
        users: list[DirectoryUser] = []
        with httpx.Client(
            base_url=self._api_base_url,
            headers={"Authorization": f"Bearer {self._secret_key}"},
            timeout=REQUEST_TIMEOUT_SECONDS,
            transport=self._transport,
        ) as client:
            for page_number in range(MAXIMUM_PAGES):
                rows = self._fetch_page(client, page_number * PAGE_SIZE)
                users.extend(self._parse_row(row) for row in rows)
                if len(rows) < PAGE_SIZE:
                    return users
        raise IdentityDirectoryError("user list exceeds the supported size")

    def _fetch_page(self, client: httpx.Client, offset: int) -> list[object]:
        last_failure = "unknown"
        for attempt in range(1, MAXIMUM_ATTEMPTS + 1):
            try:
                response = client.get("/v1/users", params={"limit": PAGE_SIZE, "offset": offset})
            except httpx.TransportError as transport_error:
                last_failure = type(transport_error).__name__
            else:
                if response.status_code == 200:
                    return self._parse_page(response)
                if response.status_code < 500 and response.status_code != 429:
                    raise IdentityDirectoryError(f"Clerk API rejected the request ({response.status_code})")
                last_failure = f"status {response.status_code}"
            if attempt < MAXIMUM_ATTEMPTS:
                self._sleeper(0.5 * attempt)
        raise IdentityDirectoryError(f"Clerk API unavailable after retries ({last_failure})")

    @staticmethod
    def _parse_page(response: httpx.Response) -> list[object]:
        try:
            body = response.json()
        except ValueError as parse_error:
            raise IdentityDirectoryError("Clerk API returned invalid JSON") from parse_error
        if not isinstance(body, list):
            raise IdentityDirectoryError("Clerk API returned an unexpected shape")
        return body

    @staticmethod
    def _parse_row(row: object) -> DirectoryUser:
        if not isinstance(row, dict):
            raise IdentityDirectoryError("Clerk API returned a malformed user")
        user_id = row.get("id")
        if not isinstance(user_id, str) or not user_id:
            raise IdentityDirectoryError("Clerk API returned a user without an id")
        return DirectoryUser(user_id=user_id, verified_email=verified_primary_email(row))
