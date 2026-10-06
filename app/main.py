"""FastAPI application entry point."""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router as employees_router

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(
    title="Employee Management API",
    description=(
        "CRUD API for employees. Read endpoints are public; "
        "`POST /employees`, `PUT /employees/{id}` and `DELETE /employees/{id}` "
        "require the `X-API-Key` header."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees_router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "api_key_configured": bool(os.environ.get("API_KEY"))}
