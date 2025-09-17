# backend/app/main.py
from fastapi import FastAPI
from app.database import engine, Base
from app.api import api_router  # Import your API router

# Initialize the FastAPI app
app = FastAPI(title="AI Elderly Medicare System")

# Startup event to create database tables
@app.on_event("startup")
def on_startup():
    """
    Create all tables in the database if they do not exist.
    This function is called on the "startup" event of the FastAPI application.
    """
    Base.metadata.create_all(bind=engine)

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

# Include API routers
app.include_router(api_router, prefix="/api/v1")
