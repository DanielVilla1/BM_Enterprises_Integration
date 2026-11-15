# ===== AI GENERATED: partial_update =====
# Purpose: Shared base for PATCH bodies (only sent fields change)
# Inputs: JSON body with any subset of fields
# Returns: validated model exposing changes() as a dict
# Flow:
# 1. Reject empty bodies and explicit null on required fields
# 2. changes() returns exactly the fields the client sent

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, model_validator


class PartialUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    required_fields: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="after")
    def validate_sent_fields(self) -> "PartialUpdateRequest":
        sent = self.model_fields_set
        if not sent:
            raise ValueError("at least one field must be provided")
        for field_name in sent & self.required_fields:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self

    def changes(self) -> dict[str, object]:
        return self.model_dump(exclude_unset=True)
