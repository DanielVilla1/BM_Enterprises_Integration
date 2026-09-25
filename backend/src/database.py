# ===== AI GENERATED: database_setup =====
# Purpose: Create SQLAlchemy engine, session and Base for ORM models
# Inputs: Reads DATABASE_URL from environment
# Returns: `engine`, `SessionLocal`, `Base` for repository use
# Flow:
# 1. Read env DATABASE_URL
# 2. Create engine and sessionmaker
# 3. Export Base for model declarations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# Use SQLite for local dev by default; if a different DATABASE_URL is provided
# (e.g. PostgreSQL in Docker), the engine will be created accordingly.
if DATABASE_URL.startswith("sqlite"):
	engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
	engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

