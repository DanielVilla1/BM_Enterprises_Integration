# ===== AI GENERATED: TodoService =====
# Purpose: Business orchestration for Todo use-cases
# Inputs: repository implementing IToDoRepository
# Returns: DTOs consumed by controllers
# Flow:
# 1. Delegate to repository, handle simple validations

from typing import List, Optional
from ..Contract.i_todo_repository import IToDoRepository
from ..DTO.todo_dto import TodoCreate, TodoUpdate, TodoOut


class TodoService:
    def __init__(self, repository: IToDoRepository):
        self.repository = repository

    def list_todos(self) -> List[TodoOut]:
        return self.repository.list_all()

    def get_todo(self, todo_id: int) -> Optional[TodoOut]:
        return self.repository.get(todo_id)

    def create_todo(self, payload: TodoCreate) -> TodoOut:
        if not payload.title or not payload.title.strip():
            raise ValueError("title is required")
        return self.repository.create(payload)

    def update_todo(self, todo_id: int, payload: TodoUpdate) -> Optional[TodoOut]:
        return self.repository.update(todo_id, payload)

    def delete_todo(self, todo_id: int) -> bool:
        return self.repository.delete(todo_id)
