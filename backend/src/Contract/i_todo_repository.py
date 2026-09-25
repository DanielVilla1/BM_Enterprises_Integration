# ===== AI GENERATED: IToDoRepository =====
# Purpose: Define repository interface for Todo persistence
# Inputs: Domain/service calls
# Returns: method signatures for implementations
# Flow:
# 1. Provide signatures: list_all, get, create, update, delete

from typing import List, Optional
from ..DTO.todo_dto import TodoCreate, TodoUpdate, TodoOut


class IToDoRepository:
    def list_all(self) -> List[TodoOut]:
        raise NotImplementedError()

    def get(self, todo_id: int) -> Optional[TodoOut]:
        raise NotImplementedError()

    def create(self, payload: TodoCreate) -> TodoOut:
        raise NotImplementedError()

    def update(self, todo_id: int, payload: TodoUpdate) -> Optional[TodoOut]:
        raise NotImplementedError()

    def delete(self, todo_id: int) -> bool:
        raise NotImplementedError()
