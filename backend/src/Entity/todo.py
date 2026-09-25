# ===== AI GENERATED: TodoEntity =====
# Purpose: Define ORM `Todo` entity for persistence
# Inputs: SQLAlchemy `Base` from `database.py`
# Returns: `Todo` ORM model class
# Flow:
# 1. Define table columns
# 2. Provide simple repr

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from ..database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Todo id={self.id} title={self.title!r} completed={self.completed}>"
