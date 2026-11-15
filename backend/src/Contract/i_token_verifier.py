# ===== AI GENERATED: ITokenVerifier =====
# Purpose: Port for verifying identity-provider session tokens
# Inputs: raw bearer token
# Returns: VerifiedClaims or a typed failure
# Flow:
# 1. verify returns claims when signature, issuer, expiry, azp pass
# 2. TokenVerificationError means 401; ProviderUnavailableError means 503

from dataclasses import dataclass
from typing import Protocol


class TokenVerificationError(Exception):
    """The token is not acceptable (bad signature, expired, wrong issuer...)."""


class ProviderUnavailableError(Exception):
    """Signing keys could not be obtained and none are cached."""


@dataclass(frozen=True)
class VerifiedClaims:
    subject: str


class ITokenVerifier(Protocol):
    def verify(self, raw_token: str) -> VerifiedClaims: ...
