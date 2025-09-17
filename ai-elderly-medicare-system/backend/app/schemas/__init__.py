"""
Pydantic Schemas Package for AI Elderly Medicare System
Request/Response models for API validation
"""

from .user_schema import (
    UserCreate, UserUpdate, UserResponse, UserLogin, 
    PasswordChange, PasswordReset, UserListResponse
)
from .patient_schema import (
    PatientCreate, PatientUpdate, PatientResponse, 
    PatientListResponse, PatientSummary
)
from .medication_schema import (
    MedicationCreate, MedicationUpdate, MedicationResponse,
    MedicationListResponse, DoseTaken, RefillRequest
)
from .appointment_schema import (
    AppointmentCreate, AppointmentUpdate, AppointmentResponse,
    AppointmentListResponse, AppointmentReschedule
)
from .notification_schema import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationListResponse, NotificationMarkRead
)

__all__ = [
    # User schemas
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin",
    "PasswordChange", "PasswordReset", "UserListResponse",
    
    # Patient schemas
    "PatientCreate", "PatientUpdate", "PatientResponse",
    "PatientListResponse", "PatientSummary",
    
    # Medication schemas
    "MedicationCreate", "MedicationUpdate", "MedicationResponse",
    "MedicationListResponse", "DoseTaken", "RefillRequest",
    
    # Appointment schemas
    "AppointmentCreate", "AppointmentUpdate", "AppointmentResponse",
    "AppointmentListResponse", "AppointmentReschedule",
    
    # Notification schemas
    "NotificationCreate", "NotificationUpdate", "NotificationResponse",
    "NotificationListResponse", "NotificationMarkRead",
]