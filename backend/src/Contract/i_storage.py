# ===== AI GENERATED: storage_contracts =====
# Purpose: Ports for private object storage and image sanitizing
# Inputs: bytes, paths, time-to-live
# Returns: signed URLs, sanitized images, or typed failures
# Flow:
# 1. IObjectStorage hides the provider (Supabase Storage today)
# 2. IImageSanitizer validates content and strips metadata

from dataclasses import dataclass
from typing import Protocol


class StorageError(Exception):
    """The object store could not complete the request."""


class InvalidImageError(Exception):
    """The upload is not an acceptable JPEG or PNG image."""


@dataclass(frozen=True)
class SanitizedImage:
    content: bytes
    content_type: str
    extension: str


class IObjectStorage(Protocol):
    def put(self, path: str, content: bytes, content_type: str) -> None: ...

    def create_signed_url(self, path: str, expires_in_seconds: int) -> str: ...

    def delete(self, path: str) -> None: ...


class IImageSanitizer(Protocol):
    def sanitize(self, raw_content: bytes) -> SanitizedImage: ...
