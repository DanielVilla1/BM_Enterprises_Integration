# ===== AI GENERATED: SupabaseObjectStorage =====
# Purpose: Private bucket access through the Supabase Storage REST API
# Inputs: project URL, service key (server-side only), bucket name
# Returns: signed URLs or StorageError; objects are never public
# Flow:
# 1. put: upload with the service key, bounded retries on 5xx/transport errors
# 2. create_signed_url: short-lived URL generated after the caller was authorized
# 3. delete: best-effort cleanup when the database commit fails

import time
from collections.abc import Callable
from urllib.parse import quote

import httpx

from ...Contract.i_storage import StorageError

REQUEST_TIMEOUT_SECONDS = 15.0
MAXIMUM_ATTEMPTS = 3


class SupabaseObjectStorage:
    """Implements IObjectStorage."""

    def __init__(
        self,
        base_url: str,
        service_key: str,
        bucket: str,
        transport: httpx.BaseTransport | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._service_key = service_key
        self._bucket = bucket
        self._transport = transport
        self._sleeper = sleeper

    def _client(self) -> httpx.Client:
        if not self._base_url or not self._service_key:
            raise StorageError("object storage is not configured")
        return httpx.Client(
            base_url=f"{self._base_url}/storage/v1",
            headers={"Authorization": f"Bearer {self._service_key}", "apikey": self._service_key},
            timeout=REQUEST_TIMEOUT_SECONDS,
            transport=self._transport,
        )

    def _object_path(self, path: str) -> str:
        return f"/object/{self._bucket}/{quote(path, safe='/')}"

    def put(self, path: str, content: bytes, content_type: str) -> None:
        with self._client() as client:
            last_failure = "unknown"
            for attempt in range(1, MAXIMUM_ATTEMPTS + 1):
                try:
                    response = client.post(
                        self._object_path(path),
                        content=content,
                        headers={"Content-Type": content_type, "x-upsert": "false"},
                    )
                except httpx.TransportError as transport_error:
                    last_failure = type(transport_error).__name__
                else:
                    if response.status_code in (200, 201):
                        return
                    if response.status_code < 500 and response.status_code != 429:
                        raise StorageError(f"storage rejected the upload ({response.status_code})")
                    last_failure = f"status {response.status_code}"
                if attempt < MAXIMUM_ATTEMPTS:
                    self._sleeper(0.5 * attempt)
        raise StorageError(f"storage unavailable after retries ({last_failure})")

    def create_signed_url(self, path: str, expires_in_seconds: int) -> str:
        with self._client() as client:
            try:
                response = client.post(
                    f"/object/sign/{self._bucket}/{quote(path, safe='/')}",
                    json={"expiresIn": expires_in_seconds},
                )
            except httpx.TransportError as transport_error:
                raise StorageError("storage unavailable") from transport_error
        if response.status_code != 200:
            raise StorageError(f"storage could not sign the URL ({response.status_code})")
        try:
            signed_path = response.json()["signedURL"]
        except (ValueError, KeyError, TypeError) as parse_error:
            raise StorageError("storage returned an unexpected response") from parse_error
        if not isinstance(signed_path, str) or not signed_path.startswith("/object/sign/"):
            raise StorageError("storage returned an unexpected URL")
        return f"{self._base_url}/storage/v1{signed_path}"

    def delete(self, path: str) -> None:
        try:
            with self._client() as client:
                client.delete(self._object_path(path))
        except (httpx.HTTPError, StorageError):
            return
