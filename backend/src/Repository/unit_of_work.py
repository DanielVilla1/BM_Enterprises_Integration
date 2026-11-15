# ===== AI GENERATED: SqlAlchemyUnitOfWork =====
# Purpose: Session-backed transaction control
# Inputs: SQLAlchemy Session
# Returns: commit / rollback
# Flow:
# 1. Repositories only flush; this class commits

from sqlalchemy.orm import Session


class SqlAlchemyUnitOfWork:
    def __init__(self, session: Session) -> None:
        self._session = session

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
