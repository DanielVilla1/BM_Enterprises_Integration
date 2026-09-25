# ===== AI GENERATED: TodoController =====
# Purpose: FastAPI router exposing Todo CRUD endpoints
# Inputs: FastAPI `APIRouter`, TodoService and DB session
# Returns: JSON responses using DTOs
# Flow:
# 1. Provide endpoints: list, get, create, update, delete

from fastapi import APIRouter, Depends, HTTPException
import logging
from typing import List
from ..DTO.todo_dto import TodoCreate, TodoUpdate, TodoOut
from ..Service.todo_service import TodoService
from ..Repository.todo_repository import TodoRepository
from ..database import SessionLocal


router = APIRouter(prefix="/todos", tags=["todos"])

logger = logging.getLogger("todo_controller")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_service(db=Depends(get_db)):
    repo = TodoRepository(db)
    return TodoService(repo)


@router.get("/", response_model=List[TodoOut])
def list_todos(service: TodoService = Depends(get_service)):
    return service.list_todos()


@router.get("/{todo_id}", response_model=TodoOut)
def get_todo(todo_id: int, service: TodoService = Depends(get_service)):
    item = service.get_todo(todo_id)
    if not item:
        raise HTTPException(status_code=404, detail="Todo not found")
    return item


@router.post("/", response_model=TodoOut)
def create_todo(payload: TodoCreate, service: TodoService = Depends(get_service)):
    try:
        return service.create_todo(payload)
    except Exception as e:
        logger.exception("Failed to create todo")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{todo_id}", response_model=TodoOut)
def update_todo(todo_id: int, payload: TodoUpdate, service: TodoService = Depends(get_service)):
    try:
        item = service.update_todo(todo_id, payload)
        if not item:
            raise HTTPException(status_code=404, detail="Todo not found")
        return item
    except Exception as e:
        logger.exception("Failed to update todo %s", todo_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{todo_id}")
def delete_todo(todo_id: int, service: TodoService = Depends(get_service)):
    try:
        ok = service.delete_todo(todo_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Todo not found")
        return {"deleted": True}
    except Exception as e:
        logger.exception("Failed to delete todo %s", todo_id)
        raise HTTPException(status_code=500, detail=str(e))
