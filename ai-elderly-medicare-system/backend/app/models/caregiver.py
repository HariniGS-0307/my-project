"""
Caregiver model for managing patient caregivers and care coordination
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Enum, JSON, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timedelta, time
from typing import Optional, Dict, Any, List

from app.database import Base

class CaregiverType(enum.Enum):
    """Types of caregivers"""
    FAMILY_MEMBER = "family_member"
    PROFESSIONAL = "professional"
    VOLUNTEER = "volunteer"
    HOME_HEALTH_AIDE = "home_health_aide"
    NURSE = "nurse"
    COMPANION = "companion"
    RESPITE = "respite"
    LIVE_IN = "live_in"

class CaregiverStatus(enum.Enum):
    """Caregiver status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    PENDING = "pending"
    SUSPENDED = "suspended"

class CertificationStatus(enum.Enum):
    """Certification status"""
    VALID = "valid"
    EXPIRED = "expired"
    PENDING_RENEWAL = "pending_renewal"
    SUSPENDED = "suspended"
    NOT_REQUIRED = "not_required"

class Caregiver(Base):
    """Caregiver model for patient care coordination"""
    
    __tablename__ = "caregivers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Caregiver Information
    caregiver_id = Column(String(20), unique=True, index=True, nullable=False)
    caregiver_type = Column(Enum(CaregiverType), nullable=False)
    status = Column(Enum(CaregiverStatus), default=CaregiverStatus.PENDING)
    
    # Professional Information
    license_number = Column(String(50))
    certification_number = Column(String(50))
    certification_status = Column(Enum(CertificationStatus), default=CertificationStatus.NOT_REQUIRED)
    certification_expiry = Column(DateTime(timezone=True))
    
    # Experience and Qualifications
    years_of_experience = Column(Integer)
    specializations = Column(JSON)  # List of specializations
    languages_spoken = Column(JSON)  # List of languages
    education_level = Column(String(100))
    
    # Availability
    is_available = Column(Boolean, default=True)
    availability_schedule = Column(JSON)  # Weekly schedule
    max_patients = Column(Integer, default=5)
    current_patient_count = Column(Integer, default=0)
    
    # Work Schedule
    shift_start_time = Column(Time)
    shift_end_time = Column(Time)
    works_weekends = Column(Boolean, default=False)
    works_nights = Column(Boolean, default=False)
    
    # Contact and Emergency Information
    emergency_contact_name = Column(String(100))
    emergency_contact_phone = Column(String(20))
    emergency_contact_relationship = Column(String(50))
    
    # Background and Verification
    background_check_completed = Column(Boolean, default=False)
    background_check_date = Column(DateTime(timezone=True))
    background_check_status = Column(String(50))
    
    # Insurance and Bonding
    is_insured = Column(Boolean, default=False)
    insurance_provider = Column(String(100))
    insurance_policy_number = Column(String(50))
    insurance_expiry = Column(DateTime(timezone=True))
    is_bonded = Column(Boolean, default=False)
    
    # Ratings and Reviews
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    total_hours_worked = Column(Float, default=0.0)
    
    # Employment Information
    employment_type = Column(String(50))  # full_time, part_time, contract, volunteer
    hourly_rate = Column(Float)
    salary = Column(Float)
    hire_date = Column(DateTime(timezone=True))
    termination_date = Column(DateTime(timezone=True))
    
    # Skills and Capabilities
    medical_skills = Column(JSON)  # List of medical skills
    personal_care_skills = Column(JSON)  # List of personal care skills
    household_skills = Column(JSON)  # List of household skills
    transportation_available = Column(Boolean, default=False)
    
    # Training and Certifications
    training_records = Column(JSON)  # Training history
    certifications = Column(JSON)  # List of certifications
    last_training_date = Column(DateTime(timezone=True))
    next_training_due = Column(DateTime(timezone=True))
    
    # Performance Metrics
    punctuality_score = Column(Float, default=100.0)
    reliability_score = Column(Float, default=100.0)
    patient_satisfaction_score = Column(Float, default=0.0)
    
    # Notes and Comments
    notes = Column(Text)
    supervisor_notes = Column(Text)
    patient_feedback = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="caregiver_profile")
    patient_assignments = relationship("PatientCaregiverAssignment", back_populates="caregiver")
    care_logs = relationship("CareLog", back_populates="caregiver")
    
    def __repr__(self):
        return f"<Caregiver(id={self.id}, caregiver_id='{self.caregiver_id}', type='{self.caregiver_type.value}', status='{self.status.value}')>"
    
    @property
    def is_active(self):
        """Check if caregiver is active"""
        return self.status == CaregiverStatus.ACTIVE
    
    @property
    def is_professional(self):
        """Check if caregiver is a professional"""
        professional_types = [
            CaregiverType.PROFESSIONAL,
            CaregiverType.HOME_HEALTH_AIDE,
            CaregiverType.NURSE
        ]
        return self.caregiver_type in professional_types
    
    @property
    def is_certified(self):
        """Check if caregiver has valid certification"""
        return self.certification_status == CertificationStatus.VALID
    
    @property
    def certification_expires_soon(self):
        """Check if certification expires within 30 days"""
        if self.certification_expiry:
            days_until_expiry = (self.certification_expiry - datetime.now()).days
            return days_until_expiry <= 30
        return False
    
    @property
    def can_accept_new_patients(self):
        """Check if caregiver can accept new patients"""
        return (self.is_active and 
                self.is_available and 
                self.current_patient_count < self.max_patients)
    
    @property
    def full_name(self):
        """Get caregiver's full name"""
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        return "Unknown"
    
    def update_availability(self, is_available: bool):
        """Update caregiver availability"""
        self.is_available = is_available
        self.last_active = datetime.now()
    
    def add_patient_assignment(self, patient_id: int):
        """Add patient to caregiver's assignments"""
        if self.can_accept_new_patients:
            self.current_patient_count += 1
            return True
        return False
    
    def remove_patient_assignment(self, patient_id: int):
        """Remove patient from caregiver's assignments"""
        if self.current_patient_count > 0:
            self.current_patient_count -= 1
    
    def update_rating(self, new_rating: float):
        """Update caregiver's average rating"""
        if self.total_reviews == 0:
            self.average_rating = new_rating
        else:
            total_points = self.average_rating * self.total_reviews
            total_points += new_rating
            self.total_reviews += 1
            self.average_rating = round(total_points / self.total_reviews, 2)
    
    def add_training_record(self, training_name: str, completion_date: datetime, 
                          certificate_number: str = None):
        """Add training record"""
        if not self.training_records:
            self.training_records = []
        
        training_record = {
            "name": training_name,
            "completion_date": completion_date.isoformat(),
            "certificate_number": certificate_number
        }
        
        self.training_records.append(training_record)
        self.last_training_date = completion_date
    
    def add_certification(self, cert_name: str, cert_number: str, 
                         issue_date: datetime, expiry_date: datetime = None):
        """Add certification"""
        if not self.certifications:
            self.certifications = []
        
        certification = {
            "name": cert_name,
            "number": cert_number,
            "issue_date": issue_date.isoformat(),
            "expiry_date": expiry_date.isoformat() if expiry_date else None
        }
        
        self.certifications.append(certification)
    
    def get_weekly_schedule(self):
        """Get formatted weekly schedule"""
        if not self.availability_schedule:
            return {}
        
        return self.availability_schedule
    
    def set_weekly_schedule(self, schedule: Dict[str, Dict]):
        """Set weekly availability schedule
        
        Example schedule format:
        {
            "monday": {"start": "09:00", "end": "17:00", "available": true},
            "tuesday": {"start": "09:00", "end": "17:00", "available": true},
            ...
        }
        """
        self.availability_schedule = schedule
    
    def is_available_at_time(self, check_datetime: datetime):
        """Check if caregiver is available at specific time"""
        if not self.is_available or not self.availability_schedule:
            return False
        
        day_name = check_datetime.strftime("%A").lower()
        day_schedule = self.availability_schedule.get(day_name)
        
        if not day_schedule or not day_schedule.get("available", False):
            return False
        
        check_time = check_datetime.time()
        start_time = datetime.strptime(day_schedule["start"], "%H:%M").time()
        end_time = datetime.strptime(day_schedule["end"], "%H:%M").time()
        
        return start_time <= check_time <= end_time
    
    def get_performance_summary(self):
        """Get performance summary"""
        return {
            "average_rating": self.average_rating,
            "total_reviews": self.total_reviews,
            "punctuality_score": self.punctuality_score,
            "reliability_score": self.reliability_score,
            "patient_satisfaction_score": self.patient_satisfaction_score,
            "total_hours_worked": self.total_hours_worked,
            "current_patients": self.current_patient_count,
            "years_experience": self.years_of_experience
        }
    
    def calculate_monthly_hours(self, month: int, year: int):
        """Calculate total hours worked in a specific month"""
        # This would integrate with time tracking system
        # For now, return estimated hours based on schedule
        if not self.availability_schedule:
            return 0
        
        total_hours = 0
        for day, schedule in self.availability_schedule.items():
            if schedule.get("available", False):
                start = datetime.strptime(schedule["start"], "%H:%M").time()
                end = datetime.strptime(schedule["end"], "%H:%M").time()
                daily_hours = (datetime.combine(datetime.today(), end) - 
                             datetime.combine(datetime.today(), start)).total_seconds() / 3600
                total_hours += daily_hours
        
        # Multiply by approximate weeks in month
        return total_hours * 4.3
    
    def get_specialization_match_score(self, required_skills: List[str]):
        """Calculate match score based on required skills"""
        if not self.specializations or not required_skills:
            return 0.0
        
        caregiver_skills = set(self.specializations)
        required_skills_set = set(required_skills)
        
        matching_skills = caregiver_skills.intersection(required_skills_set)
        match_score = len(matching_skills) / len(required_skills_set) * 100
        
        return round(match_score, 2)
    
    @classmethod
    def find_available_caregivers(cls, db_session, required_skills: List[str] = None, 
                                caregiver_type: CaregiverType = None):
        """Find available caregivers matching criteria"""
        query = db_session.query(cls).filter(
            cls.status == CaregiverStatus.ACTIVE,
            cls.is_available == True,
            cls.current_patient_count < cls.max_patients
        )
        
        if caregiver_type:
            query = query.filter(cls.caregiver_type == caregiver_type)
        
        available_caregivers = query.all()
        
        if required_skills:
            # Sort by skill match score
            scored_caregivers = []
            for caregiver in available_caregivers:
                score = caregiver.get_specialization_match_score(required_skills)
                scored_caregivers.append((caregiver, score))
            
            # Sort by score descending
            scored_caregivers.sort(key=lambda x: x[1], reverse=True)
            return [caregiver for caregiver, score in scored_caregivers]
        
        return available_caregivers


class PatientCaregiverAssignment(Base):
    """Association table for patient-caregiver assignments"""
    
    __tablename__ = "patient_caregiver_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    caregiver_id = Column(Integer, ForeignKey("caregivers.id"), nullable=False)
    
    # Assignment Details
    assignment_type = Column(String(50))  # primary, secondary, respite, etc.
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Care Plan
    care_plan = Column(Text)
    special_instructions = Column(Text)
    emergency_procedures = Column(Text)
    
    # Schedule
    scheduled_hours_per_week = Column(Float)
    actual_hours_per_week = Column(Float, default=0.0)
    
    # Performance
    patient_satisfaction = Column(Float)
    family_satisfaction = Column(Float)
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient")
    caregiver = relationship("Caregiver", back_populates="patient_assignments")
    
    def __repr__(self):
        return f"<PatientCaregiverAssignment(patient_id={self.patient_id}, caregiver_id={self.caregiver_id}, active={self.is_active})>"


class CareLog(Base):
    """Care log entries for tracking caregiver activities"""
    
    __tablename__ = "care_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    caregiver_id = Column(Integer, ForeignKey("caregivers.id"), nullable=False)
    
    # Log Details
    log_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer)
    
    # Activities
    activities_performed = Column(JSON)  # List of activities
    medications_administered = Column(JSON)  # Medications given
    vital_signs_recorded = Column(JSON)  # Vital signs taken
    
    # Observations
    patient_condition = Column(Text)
    mood_assessment = Column(String(50))
    pain_level = Column(Integer)  # 1-10 scale
    
    # Issues and Concerns
    issues_noted = Column(Text)
    concerns_raised = Column(Text)
    actions_taken = Column(Text)
    
    # Communication
    family_contacted = Column(Boolean, default=False)
    doctor_contacted = Column(Boolean, default=False)
    emergency_services_called = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("Patient")
    caregiver = relationship("Caregiver", back_populates="care_logs")
    
    def __repr__(self):
        return f"<CareLog(id={self.id}, patient_id={self.patient_id}, caregiver_id={self.caregiver_id}, date='{self.log_date}')>"