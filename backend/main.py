# AI MODIFIED: main.py
# ===== AI GENERATED: main_app =====
# Purpose: Wire FastAPI app, include routers and initialize DB tables
# Inputs: registers `todo` router
# Returns: running FastAPI app
# Flow:
# 1. Create app and CORS
# 2. Include router
# 3. Create DB tables at startup

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .src.database import engine, Base
from .src.Controller.todo_controller import router as todo_router
from .src.database import SessionLocal
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from .src.Entity.todo import Todo as TodoModel


app = FastAPI(title="TechReserve API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # create tables if they do not exist
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "TechReserve API is running"}


app.include_router(todo_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    try:
        db = SessionLocal()
        # try a lightweight query to ensure DB connectivity
        _ = db.query(TodoModel).limit(1).all()
        return JSONResponse({"db": True})
    except SQLAlchemyError as e:
        return JSONResponse({"db": False, "error": str(e)}, status_code=500)
    finally:
        try:
            db.close()
        except Exception:
            pass
