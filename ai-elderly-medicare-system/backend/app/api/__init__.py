"""
API Package for AI Elderly Medicare System
"""

from fastapi import APIRouter
from .v1 import auth, patients, medications, appointments, notifications, deliveries, dashboard, reports, caregivers, reminders, health_monitoring

# Create main API router
api_router = APIRouter()

# Include all v1 routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(patients.router, prefix="/patients", tags=["Patients"])
api_router.include_router(medications.router, prefix="/medications", tags=["Medications"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["Appointments"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(deliveries.router, prefix="/deliveries", tags=["Deliveries"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(caregivers.router, prefix="/caregivers", tags=["Caregivers"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["Reminders"])
api_router.include_router(health_monitoring.router, prefix="/health", tags=["Health Monitoring"])

__all__ = ["api_router"]