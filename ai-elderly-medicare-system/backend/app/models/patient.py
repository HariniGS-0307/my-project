├── backend/                              # Python Backend (Flask/FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # Main application entry
│   │   ├── config.py                    # Configuration settings
│   │   ├── database.py                  # Database connection
│   │   ├── security.py                  # Security & Authentication
│   │   │
│   │   ├── models/                      # Database Models (SQLAlchemy)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── patient.py
│   │   │   ├── medication.py
│   │   │   ├── appointment.py
│   │   │   ├── notification.py
│   │   │   ├── delivery.py
│   │   │   ├── caregiver.py
│   │   │   ├── health_record.py
│   │   │   ├── prescription.py
│   │   │   └── emergency_contact.py
│   │   │
│   │ """
Patient model for elderly healthcare management
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Float, Boolean, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, date

from .database import Base

class Gender(enum.Enum):
    """Gender options"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class BloodType(enum.Enum):
    """Blood type options"""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class Patient(Base):
    """Patient model for elderly individuals"""
    
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Personal Information
    patient_id = Column(String(20), unique=True, index=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    blood_type = Column(Enum(BloodType))
    
    # Contact Information
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(10))
    country = Column(String(50), default="USA")
    
    # Medical Information
    height = Column(Float)  # in cm
    weight = Column(Float)  # in kg
    medical_record_number = Column(String(50), unique=True)
    insurance_number = Column(String(100))
    medicare_number = Column(String(50))
    
    # Health Status
    is_active_patient = Column(Boolean, default=True)
    risk_level = Column(String(20), default="low")  # low, medium, high, critical
    mobility_status = Column(String(50))
    cognitive_status = Column(String(50))
    
    # Care Information
    primary_physician_id = Column(Integer, ForeignKey("users.id"))
    assigned_caregiver_id = Column(Integer, ForeignKey("users.id"))
    care_plan = Column(Text)
    special_needs = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_visit = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="patients")
    primary_physician = relationship("User", foreign_keys=[primary_physician_id])
    assigned_caregiver = relationship("User", foreign_keys=[assigned_caregiver_id])
    
    health_records = relationship("HealthRecord", back_populates="patient", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    medications = relationship("Medication", back_populates="patient", cascade="all, delete-orphan")
    emergency_contacts = relationship("EmergencyContact", back_populates="patient", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, patient_id='{self.patient_id}', name='{self.user.full_name if self.user else 'Unknown'}')>"
    
    @property
    def age(self):
        """Calculate patient's age"""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    @property
    def bmi(self):
        """Calculate BMI if height and weight are available"""
        if self.height and self.weight:
            height_m = self.height / 100  # convert cm to meters
            return round(self.weight / (height_m ** 2), 2)
        return None
    
    @property
    def is_elderly(self):
        """Check if patient is elderly (65+)"""
        return self.age and self.age >= 65
    
    @property
    def full_address(self):
        """Get formatted full address"""
        parts = [self.address, self.city, self.state, self.zip_code, self.country]
        return ", ".join(filter(None, parts))
    
    def get_latest_health_record(self):
        """Get the most recent health record"""
        if self.health_records:
            return max(self.health_records, key=lambda x: x.recorded_at)
        return None
    
    def get_current_medications(self):
        """Get currently active medications"""
        return [med for med in self.medications if med.is_active]
    
    def get_upcoming_appointments(self):
        """Get upcoming appointments"""
        now = datetime.now()
        return [apt for apt in self.appointments if apt.appointment_date > now and apt.status != "cancelled"]