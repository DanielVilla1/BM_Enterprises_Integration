# ===== AI GENERATED: ClerkTokenVerifier =====
# Purpose: Verify Clerk session JWTs locally against cached JWKS keys
# Inputs: issuer, JWKS url, audience, authorized parties, clock skew
# Returns: VerifiedClaims or typed failure
# Flow:
# 1. Resolve the signing key (cached by PyJWKClient)
# 2. Decode: RS256 only; require exp, iat, sub; check issuer / aud
# 3. Check azp against the allowlist when configured

from collections.abc import Callable

import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientConnectionError, PyJWKClientError, PyJWTError

from ...Contract.i_token_verifier import (
    ProviderUnavailableError,
    TokenVerificationError,
    VerifiedClaims,
)

KeyResolver = Callable[[str], object]


class ClerkTokenVerifier:
    """Implements ITokenVerifier. Never calls Clerk per request: keys are cached."""

    def __init__(
        self,
        issuer: str,
        jwks_url: str,
        audience: str,
        authorized_parties: tuple[str, ...],
        clock_skew_seconds: int,
        key_resolver: KeyResolver | None = None,
    ) -> None:
        self._issuer = issuer
        self._audience = audience
        self._authorized_parties = authorized_parties
        self._clock_skew_seconds = clock_skew_seconds
        self._key_resolver = key_resolver
        self._jwks_url = jwks_url
        self._jwk_client = (
            PyJWKClient(jwks_url, cache_keys=True, timeout=5) if jwks_url and key_resolver is None else None
        )

    def _resolve_signing_key(self, raw_token: str) -> object:
        if self._key_resolver is not None:
            return self._key_resolver(raw_token)
        if not self._issuer or self._jwk_client is None:
            raise ProviderUnavailableError("identity provider is not configured")
        try:
            return self._jwk_client.get_signing_key_from_jwt(raw_token).key
        except PyJWKClientConnectionError as connection_error:
            raise ProviderUnavailableError("signing keys unavailable") from connection_error
        except (PyJWKClientError, PyJWTError) as key_error:
            raise TokenVerificationError("no usable signing key") from key_error

    def verify(self, raw_token: str) -> VerifiedClaims:
        signing_key = self._resolve_signing_key(raw_token)
        try:
            claims = jwt.decode(
                raw_token,
                signing_key,
                algorithms=["RS256"],
                issuer=self._issuer,
                audience=self._audience or None,
                leeway=self._clock_skew_seconds,
                options={
                    "require": ["exp", "iat", "sub", "iss"],
                    "verify_aud": bool(self._audience),
                },
            )
        except PyJWTError as decode_error:
            raise TokenVerificationError("token rejected") from decode_error
        authorized_party = claims.get("azp")
        if self._authorized_parties and authorized_party not in self._authorized_parties:
            raise TokenVerificationError("unauthorized party")
        subject = claims["sub"]
        if not isinstance(subject, str) or not subject:
            raise TokenVerificationError("invalid subject")
        return VerifiedClaims(subject=subject)
