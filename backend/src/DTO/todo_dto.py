# ===== AI GENERATED: todo_dto =====
# Purpose: Pydantic DTOs for Todo create/update/response
# Inputs: request payloads
# Returns: Pydantic models for validation and response
# Flow:
# 1. Define `TodoCreate`, `TodoUpdate`, `TodoOut`

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TodoCreate(BaseModel):
    title: str


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None


class TodoOut(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: datetime

    # Pydantic v2: enable attribute-based ORM parsing
    model_config = {"from_attributes": True}
