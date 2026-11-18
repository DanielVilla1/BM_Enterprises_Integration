# ===== AI GENERATED: application_settings =====
# Purpose: Central typed settings loaded from environment variables
# Inputs: Environment variables / .env file
# Returns: cached ApplicationSettings instance
# Flow:
# 1. Declare every tunable with a safe default
# 2. Split comma separated lists into tuples
# 3. Cache the instance for the whole process

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class ApplicationSettings(BaseSettings):
    """Runtime configuration. Secrets come from the environment only."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "sqlite:///./dev.db"
    cors_allowed_origins: Annotated[tuple[str, ...], NoDecode] = ("http://localhost:5173",)
    enable_api_docs: bool = True

    clerk_issuer: str = ""
    clerk_jwks_url: str = ""
    clerk_audience: str = ""
    clerk_authorized_parties: Annotated[tuple[str, ...], NoDecode] = ()
    clerk_webhook_secret: str = ""
    clerk_secret_key: str = ""
    clerk_api_base_url: str = "https://api.clerk.com"
    clerk_clock_skew_seconds: int = 5

    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_bucket: str = "delivery-documents"
    signed_url_ttl_seconds: int = 120
    max_upload_bytes: int = 5 * 1024 * 1024

    helper_or_upload_enabled: bool = False
    # AI MODIFIED: Keep personal deductions closed until the documented D16 review.
    payroll_deductions_enabled: bool = False
    # AI MODIFIED: Positive, bounded request budgets cannot silently disable protection.
    rate_limit_failed_auth_per_minute: int = Field(default=20, ge=1, le=1000)
    rate_limit_webhook_per_minute: int = Field(default=120, ge=1, le=1000)
    rate_limit_api_ip_per_minute: int = Field(default=600, ge=1, le=1000)
    rate_limit_api_user_per_minute: int = Field(default=120, ge=1, le=1000)
    rate_limit_upload_ip_per_minute: int = Field(default=30, ge=1, le=1000)
    rate_limit_upload_user_per_minute: int = Field(default=10, ge=1, le=1000)
    max_webhook_body_bytes: int = 262144

    @field_validator("cors_allowed_origins", "clerk_authorized_parties", mode="before")
    @classmethod
    def split_comma_separated(cls, raw_value: object) -> object:
        """Allow comma separated environment values for tuple fields."""
        if isinstance(raw_value, str):
            return tuple(part.strip() for part in raw_value.split(",") if part.strip())
        return raw_value


@lru_cache
def get_settings() -> ApplicationSettings:
    """Return the process-wide settings instance."""
    return ApplicationSettings()
