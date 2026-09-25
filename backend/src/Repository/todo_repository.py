# ===== AI GENERATED: TodoRepository =====
# Purpose: SQLAlchemy implementation of IToDoRepository
# Inputs: DB session
# Returns: CRUD operations for Todo
# Flow:
# 1. Accept session on init
# 2. Implement list_all/get/create/update/delete

from typing import List, Optional
from sqlalchemy.orm import Session
from ..Contract.i_todo_repository import IToDoRepository
from ..DTO.todo_dto import TodoCreate, TodoUpdate, TodoOut
from ..Entity.todo import Todo as TodoModel


class TodoRepository(IToDoRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> List[TodoOut]:
        rows = self.db.query(TodoModel).order_by(TodoModel.created_at.desc()).all()
        return [TodoOut.from_orm(r) for r in rows]

    def get(self, todo_id: int) -> Optional[TodoOut]:
        row = self.db.query(TodoModel).filter(TodoModel.id == todo_id).first()
        return TodoOut.from_orm(row) if row else None

    def create(self, payload: TodoCreate) -> TodoOut:
        model = TodoModel(title=payload.title)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return TodoOut.from_orm(model)

    def update(self, todo_id: int, payload: TodoUpdate) -> Optional[TodoOut]:
        row = self.db.query(TodoModel).filter(TodoModel.id == todo_id).first()
        if not row:
            return None
        if payload.title is not None:
            row.title = payload.title
        if payload.completed is not None:
            row.completed = payload.completed
        self.db.commit()
        self.db.refresh(row)
        return TodoOut.from_orm(row)

    def delete(self, todo_id: int) -> bool:
        row = self.db.query(TodoModel).filter(TodoModel.id == todo_id).first()
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        return True
