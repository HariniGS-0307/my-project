"""
Appointment model for scheduling patient visits and consultations
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timedelta

from .database import Base

class AppointmentType(enum.Enum):
    """Types of appointments"""
    ROUTINE_CHECKUP = "routine_checkup"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    CONSULTATION = "consultation"
    MEDICATION_REVIEW = "medication_review"
    THERAPY = "therapy"
    VACCINATION = "vaccination"
    DIAGNOSTIC = "diagnostic"
    TELEHEALTH = "telehealth"

class AppointmentStatus(enum.Enum):
    """Appointment status options"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"

class Priority(enum.Enum):
    """Appointment priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"

class Appointment(Base):
    """Appointment model for patient scheduling"""
    
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Appointment Details
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30)
    appointment_type = Column(Enum(AppointmentType), nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    
    # Location and Method
    location = Column(String(200))
    room_number = Column(String(20))
    is_virtual = Column(Boolean, default=False)
    virtual_meeting_link = Column(String(500))
    
    # Appointment Information
    chief_complaint = Column(Text)
    reason_for_visit = Column(Text)
    notes = Column(Text)
    preparation_instructions = Column(Text)
    
    # Follow-up Information
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime(timezone=True))
    follow_up_notes = Column(Text)
    
    # Billing and Insurance
    insurance_authorization = Column(String(100))
    copay_amount = Column(Integer)  # in cents
    billing_code = Column(String(20))
    
    # Reminders and Notifications
    reminder_sent = Column(Boolean, default=False)
    confirmation_required = Column(Boolean, default=True)
    confirmed_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    cancelled_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    provider = relationship("User", foreign_keys=[provider_id], back_populates="appointments_as_provider")
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, date='{self.appointment_date}', status='{self.status.value}')>"
    
    @property
    def end_time(self):
        """Calculate appointment end time"""
        if self.appointment_date and self.duration_minutes:
            return self.appointment_date + timedelta(minutes=self.duration_minutes)
        return None
    
    @property
    def is_upcoming(self):
        """Check if appointment is in the future"""
        return self.appointment_date > datetime.now() if self.appointment_date else False
    
    @property
    def is_today(self):
        """Check if appointment is today"""
        if self.appointment_date:
            today = datetime.now().date()
            return self.appointment_date.date() == today
        return False
    
    @property
    def is_overdue(self):
        """Check if appointment is overdue"""
        if self.appointment_date and self.status == AppointmentStatus.SCHEDULED:
            return datetime.now() > self.appointment_date
        return False
    
    @property
    def time_until_appointment(self):
        """Get time remaining until appointment"""
        if self.appointment_date and self.is_upcoming:
            return self.appointment_date - datetime.now()
        return None
    
    @property
    def formatted_date_time(self):
        """Get formatted date and time string"""
        if self.appointment_date:
            return self.appointment_date.strftime("%Y-%m-%d %H:%M")
        return None
    
    def can_be_cancelled(self):
        """Check if appointment can be cancelled"""
        cancellable_statuses = [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]
        return self.status in cancellable_statuses and self.is_upcoming
    
    def can_be_rescheduled(self):
        """Check if appointment can be rescheduled"""
        return self.can_be_cancelled()
    
    def get_reminder_time(self, hours_before=24):
        """Get the time when reminder should be sent"""
        if self.appointment_date:
            return self.appointment_date - timedelta(hours=hours_before)
        return None
    
    def mark_completed(self, notes=None):
        """Mark appointment as completed"""
        self.status = AppointmentStatus.COMPLETED
        self.completed_at = datetime.now()
        if notes:
            self.notes = notes
    
    def cancel_appointment(self, reason=None):
        """Cancel the appointment"""
        self.status = AppointmentStatus.CANCELLED
        self.cancelled_at = datetime.now()
        if reason:
            self.notes = f"Cancelled: {reason}"