"""
Medication model for tracking patient medications and prescriptions
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.database import Base

class MedicationType(enum.Enum):
    """Types of medications"""
    TABLET = "tablet"
    CAPSULE = "capsule"
    LIQUID = "liquid"
    INJECTION = "injection"
    TOPICAL = "topical"
    INHALER = "inhaler"
    PATCH = "patch"
    DROPS = "drops"
    SUPPOSITORY = "suppository"
    OTHER = "other"

class MedicationStatus(enum.Enum):
    """Medication status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"

class FrequencyType(enum.Enum):
    """Medication frequency types"""
    ONCE_DAILY = "once_daily"
    TWICE_DAILY = "twice_daily"
    THREE_TIMES_DAILY = "three_times_daily"
    FOUR_TIMES_DAILY = "four_times_daily"
    AS_NEEDED = "as_needed"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class Medication(Base):
    """Medication model for patient medication management"""
    
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    prescribed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"))
    
    # Medication Information
    name = Column(String(200), nullable=False, index=True)
    generic_name = Column(String(200))
    brand_name = Column(String(200))
    ndc_number = Column(String(20))  # National Drug Code
    medication_type = Column(Enum(MedicationType), nullable=False)
    
    # Dosage Information
    strength = Column(String(50))  # e.g., "10mg", "5ml"
    dosage_form = Column(String(50))  # e.g., "tablet", "capsule"
    dosage_amount = Column(Float)  # Amount per dose
    dosage_unit = Column(String(20))  # e.g., "mg", "ml", "units"
    
    # Administration Instructions
    frequency = Column(Enum(FrequencyType), nullable=False)
    frequency_details = Column(String(100))  # Custom frequency description
    route_of_administration = Column(String(50))  # oral, topical, injection, etc.
    instructions = Column(Text)  # Special instructions
    
    # Timing
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    duration_days = Column(Integer)
    
    # Status and Monitoring
    status = Column(Enum(MedicationStatus), default=MedicationStatus.ACTIVE)
    is_critical = Column(Boolean, default=False)  # Critical medication
    requires_monitoring = Column(Boolean, default=False)
    
    # Supply Information
    quantity_prescribed = Column(Integer)
    quantity_remaining = Column(Integer)
    refills_remaining = Column(Integer, default=0)
    last_refill_date = Column(DateTime(timezone=True))
    next_refill_due = Column(DateTime(timezone=True))
    
    # Cost and Insurance
    cost_per_unit = Column(Float)
    insurance_covered = Column(Boolean, default=True)
    copay_amount = Column(Float)
    
    # Side Effects and Interactions
    known_side_effects = Column(JSON)  # List of known side effects
    drug_interactions = Column(JSON)  # List of drug interactions
    allergies_warnings = Column(Text)
    
    # AI Analysis
    ai_risk_score = Column(Float)  # AI-calculated risk score
    ai_recommendations = Column(JSON)  # AI recommendations
    interaction_alerts = Column(JSON)  # Drug interaction alerts
    
    # Compliance Tracking
    adherence_score = Column(Float)  # Medication adherence percentage
    missed_doses = Column(Integer, default=0)
    last_taken = Column(DateTime(timezone=True))
    
    # Notes and Comments
    notes = Column(Text)
    pharmacy_notes = Column(Text)
    patient_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    discontinued_at = Column(DateTime(timezone=True))
    
    # Relationships
    patient = relationship("Patient", back_populates="medications")
    prescribed_by = relationship("User", foreign_keys=[prescribed_by_id])
    prescription = relationship("Prescription", back_populates="medications")
    deliveries = relationship("Delivery", back_populates="medication", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Medication(id={self.id}, name='{self.name}', patient_id={self.patient_id}, status='{self.status.value}')>"
    
    @property
    def is_active(self):
        """Check if medication is currently active"""
        return self.status == MedicationStatus.ACTIVE
    
    @property
    def is_due_for_refill(self):
        """Check if medication is due for refill"""
        if self.next_refill_due:
            return datetime.now() >= self.next_refill_due
        return False
    
    @property
    def days_supply_remaining(self):
        """Calculate days of supply remaining"""
        if self.quantity_remaining and self.dosage_amount:
            daily_consumption = self.get_daily_consumption()
            if daily_consumption > 0:
                return int(self.quantity_remaining / daily_consumption)
        return 0
    
    @property
    def is_expired(self):
        """Check if medication has expired"""
        if self.end_date:
            return datetime.now() > self.end_date
        return False
    
    @property
    def full_name(self):
        """Get full medication name with strength"""
        name = self.brand_name or self.name
        if self.strength:
            return f"{name} {self.strength}"
        return name
    
    def get_daily_consumption(self):
        """Calculate daily medication consumption"""
        frequency_map = {
            FrequencyType.ONCE_DAILY: 1,
            FrequencyType.TWICE_DAILY: 2,
            FrequencyType.THREE_TIMES_DAILY: 3,
            FrequencyType.FOUR_TIMES_DAILY: 4,
            FrequencyType.WEEKLY: 1/7,
            FrequencyType.MONTHLY: 1/30,
            FrequencyType.AS_NEEDED: 0.5,  # Estimate
            FrequencyType.CUSTOM: 1  # Default
        }
        
        daily_frequency = frequency_map.get(self.frequency, 1)
        return (self.dosage_amount or 1) * daily_frequency
    
    def calculate_next_refill_date(self):
        """Calculate when next refill is due"""
        if self.quantity_remaining and self.dosage_amount:
            days_remaining = self.days_supply_remaining
            if days_remaining > 7:  # Refill when 7 days left
                refill_date = datetime.now() + timedelta(days=days_remaining - 7)
                self.next_refill_due = refill_date
                return refill_date
        return None
    
    def record_dose_taken(self):
        """Record that a dose was taken"""
        self.last_taken = datetime.now()
        if self.quantity_remaining:
            self.quantity_remaining -= (self.dosage_amount or 1)
        
        # Recalculate next refill date
        self.calculate_next_refill_date()
    
    def record_missed_dose(self):
        """Record a missed dose"""
        self.missed_doses += 1
        self.update_adherence_score()
    
    def update_adherence_score(self):
        """Update medication adherence score"""
        if self.start_date:
            days_on_medication = (datetime.now() - self.start_date).days
            if days_on_medication > 0:
                expected_doses = days_on_medication * self.get_daily_consumption()
                if expected_doses > 0:
                    adherence = max(0, (expected_doses - self.missed_doses) / expected_doses * 100)
                    self.adherence_score = round(adherence, 2)
    
    def add_refill(self, quantity: int, refills: int = 0):
        """Add refill to medication"""
        self.quantity_remaining = (self.quantity_remaining or 0) + quantity
        self.refills_remaining = refills
        self.last_refill_date = datetime.now()
        self.calculate_next_refill_date()
    
    def discontinue(self, reason: str = None):
        """Discontinue medication"""
        self.status = MedicationStatus.DISCONTINUED
        self.discontinued_at = datetime.now()
        if reason:
            self.notes = f"{self.notes or ''}\nDiscontinued: {reason}".strip()
    
    def check_drug_interactions(self, other_medications: list):
        """Check for drug interactions with other medications"""
        # This would integrate with a drug interaction database
        # For now, return placeholder data
        interactions = []
        
        for med in other_medications:
            if med.id != self.id:
                # Placeholder interaction check
                if "warfarin" in self.name.lower() and "aspirin" in med.name.lower():
                    interactions.append({
                        "medication": med.name,
                        "severity": "high",
                        "description": "Increased bleeding risk"
                    })
        
        return interactions
    
    def get_side_effects_summary(self):
        """Get summary of side effects"""
        if self.known_side_effects:
            return self.known_side_effects
        
        # Return common side effects based on medication type
        common_side_effects = {
            "tablet": ["nausea", "dizziness", "headache"],
            "injection": ["injection site reaction", "pain", "swelling"],
            "topical": ["skin irritation", "redness", "itching"]
        }
        
        return common_side_effects.get(self.medication_type.value, [])
    
    def is_time_for_dose(self):
        """Check if it's time for next dose"""
        if not self.last_taken:
            return True
        
        frequency_hours = {
            FrequencyType.ONCE_DAILY: 24,
            FrequencyType.TWICE_DAILY: 12,
            FrequencyType.THREE_TIMES_DAILY: 8,
            FrequencyType.FOUR_TIMES_DAILY: 6,
            FrequencyType.WEEKLY: 168,
            FrequencyType.MONTHLY: 720,
            FrequencyType.AS_NEEDED: 4,  # Minimum 4 hours between doses
            FrequencyType.CUSTOM: 24
        }
        
        hours_since_last = (datetime.now() - self.last_taken).total_seconds() / 3600
        required_interval = frequency_hours.get(self.frequency, 24)
        
        return hours_since_last >= required_interval