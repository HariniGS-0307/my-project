"""
Prescription model for managing medical prescriptions
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from app.database import Base

class PrescriptionStatus(enum.Enum):
    """Prescription status options"""
    DRAFT = "draft"
    ACTIVE = "active"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    DISCONTINUED = "discontinued"
    ON_HOLD = "on_hold"

class PrescriptionType(enum.Enum):
    """Types of prescriptions"""
    NEW = "new"
    REFILL = "refill"
    RENEWAL = "renewal"
    MODIFICATION = "modification"
    EMERGENCY = "emergency"
    DISCHARGE = "discharge"

class PrescriptionPriority(enum.Enum):
    """Prescription priority levels"""
    ROUTINE = "routine"
    URGENT = "urgent"
    STAT = "stat"  # Immediate
    ASAP = "asap"  # As soon as possible

class Prescription(Base):
    """Prescription model for medical prescriptions"""
    
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    prescriber_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Prescription Identification
    prescription_number = Column(String(50), unique=True, index=True, nullable=False)
    rx_number = Column(String(20))  # Pharmacy RX number
    ndc_number = Column(String(20))  # National Drug Code
    
    # Prescription Details
    prescription_type = Column(Enum(PrescriptionType), default=PrescriptionType.NEW)
    status = Column(Enum(PrescriptionStatus), default=PrescriptionStatus.DRAFT)
    priority = Column(Enum(PrescriptionPriority), default=PrescriptionPriority.ROUTINE)
    
    # Medication Information
    medication_name = Column(String(200), nullable=False)
    generic_name = Column(String(200))
    brand_name = Column(String(200))
    strength = Column(String(50))  # e.g., "10mg", "5ml"
    dosage_form = Column(String(50))  # tablet, capsule, liquid, etc.
    
    # Dosing Instructions
    sig = Column(Text, nullable=False)  # Prescription directions (Signatura)
    dosage_instructions = Column(Text)  # Detailed dosing instructions
    route_of_administration = Column(String(50))  # oral, topical, injection, etc.
    frequency = Column(String(100))  # e.g., "twice daily", "as needed"
    
    # Quantity and Supply
    quantity_prescribed = Column(Integer, nullable=False)
    quantity_dispensed = Column(Integer, default=0)
    days_supply = Column(Integer)
    unit_of_measure = Column(String(20))  # tablets, ml, grams, etc.
    
    # Refill Information
    refills_authorized = Column(Integer, default=0)
    refills_remaining = Column(Integer, default=0)
    refills_used = Column(Integer, default=0)
    
    # Dates
    date_prescribed = Column(DateTime(timezone=True), nullable=False)
    date_filled = Column(DateTime(timezone=True))
    expiration_date = Column(DateTime(timezone=True))
    last_fill_date = Column(DateTime(timezone=True))
    next_fill_date = Column(DateTime(timezone=True))
    
    # Clinical Information
    diagnosis_code = Column(String(20))  # ICD-10 code
    diagnosis_description = Column(String(200))
    indication = Column(Text)  # Reason for prescription
    
    # Safety and Monitoring
    contraindications = Column(JSON)  # List of contraindications
    drug_interactions = Column(JSON)  # Known drug interactions
    allergies_checked = Column(Boolean, default=False)
    requires_monitoring = Column(Boolean, default=False)
    monitoring_parameters = Column(JSON)  # What to monitor
    
    # Pharmacy Information
    pharmacy_id = Column(String(50))
    pharmacy_name = Column(String(200))
    pharmacy_phone = Column(String(20))
    pharmacy_address = Column(Text)
    pharmacist_name = Column(String(100))
    
    # Insurance and Cost
    insurance_plan = Column(String(100))
    insurance_group = Column(String(50))
    prior_authorization_required = Column(Boolean, default=False)
    prior_authorization_number = Column(String(50))
    copay_amount = Column(Float)
    total_cost = Column(Float)
    insurance_covered_amount = Column(Float)
    
    # Electronic Prescription
    is_electronic = Column(Boolean, default=True)
    electronic_signature = Column(Text)
    transmission_date = Column(DateTime(timezone=True))
    confirmation_number = Column(String(50))
    
    # Controlled Substance Information
    is_controlled_substance = Column(Boolean, default=False)
    dea_schedule = Column(String(10))  # Schedule I-V
    dea_number = Column(String(20))
    
    # Special Instructions
    special_instructions = Column(Text)
    patient_counseling_info = Column(Text)
    pharmacy_notes = Column(Text)
    
    # Quality and Safety
    drug_utilization_review = Column(Boolean, default=False)
    dur_alerts = Column(JSON)  # Drug utilization review alerts
    clinical_decision_support = Column(JSON)  # CDS alerts and recommendations
    
    # Compliance and Adherence
    adherence_score = Column(Float)
    missed_doses_reported = Column(Integer, default=0)
    side_effects_reported = Column(JSON)
    
    # Workflow and Approval
    requires_approval = Column(Boolean, default=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(DateTime(timezone=True))
    approval_notes = Column(Text)
    
    # Audit Trail
    created_by_id = Column(Integer, ForeignKey("users.id"))
    modified_by_id = Column(Integer, ForeignKey("users.id"))
    
    # Notes and Comments
    prescriber_notes = Column(Text)
    pharmacist_notes = Column(Text)
    patient_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    cancelled_at = Column(DateTime(timezone=True))
    discontinued_at = Column(DateTime(timezone=True))
    
    # Relationships
    patient = relationship("Patient", back_populates="prescriptions")
    prescriber = relationship("User", foreign_keys=[prescriber_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    modified_by = relationship("User", foreign_keys=[modified_by_id])
    medications = relationship("Medication", back_populates="prescription")
    
    def __repr__(self):
        return f"<Prescription(id={self.id}, prescription_number='{self.prescription_number}', medication='{self.medication_name}', status='{self.status.value}')>"
    
    @property
    def is_active(self):
        """Check if prescription is active"""
        return self.status == PrescriptionStatus.ACTIVE
    
    @property
    def is_expired(self):
        """Check if prescription has expired"""
        if self.expiration_date:
            return datetime.now() > self.expiration_date
        return False
    
    @property
    def has_refills_remaining(self):
        """Check if prescription has refills remaining"""
        return self.refills_remaining > 0
    
    @property
    def is_due_for_refill(self):
        """Check if prescription is due for refill"""
        if self.next_fill_date:
            return datetime.now() >= self.next_fill_date
        return False
    
    @property
    def days_until_refill(self):
        """Get days until next refill is due"""
        if self.next_fill_date:
            delta = self.next_fill_date - datetime.now()
            return max(0, delta.days)
        return 0
    
    @property
    def is_controlled(self):
        """Check if prescription is for controlled substance"""
        return self.is_controlled_substance
    
    @property
    def full_medication_name(self):
        """Get full medication name with strength"""
        name = self.brand_name or self.medication_name
        if self.strength:
            return f"{name} {self.strength}"
        return name
    
    def calculate_expiration_date(self):
        """Calculate prescription expiration date"""
        if self.date_prescribed:
            # Most prescriptions expire after 1 year
            # Controlled substances may have shorter expiration
            if self.is_controlled_substance:
                if self.dea_schedule in ["II"]:
                    # Schedule II expires in 90 days
                    expiry = self.date_prescribed + timedelta(days=90)
                else:
                    # Schedule III-V expire in 6 months
                    expiry = self.date_prescribed + timedelta(days=180)
            else:
                # Non-controlled substances expire in 1 year
                expiry = self.date_prescribed + timedelta(days=365)
            
            self.expiration_date = expiry
            return expiry
        return None
    
    def calculate_next_fill_date(self):
        """Calculate when next refill is due"""
        if self.last_fill_date and self.days_supply:
            # Calculate based on days supply minus buffer days
            buffer_days = 3  # Allow refill 3 days early
            next_fill = self.last_fill_date + timedelta(days=self.days_supply - buffer_days)
            self.next_fill_date = next_fill
            return next_fill
        return None
    
    def process_fill(self, quantity_dispensed: int, pharmacist_name: str = None):
        """Process prescription fill"""
        self.quantity_dispensed += quantity_dispensed
        self.date_filled = datetime.now()
        self.last_fill_date = datetime.now()
        
        if pharmacist_name:
            self.pharmacist_name = pharmacist_name
        
        # Update refills
        if self.refills_remaining > 0:
            self.refills_remaining -= 1
            self.refills_used += 1
        
        # Update status
        if self.quantity_dispensed >= self.quantity_prescribed:
            self.status = PrescriptionStatus.FILLED
        else:
            self.status = PrescriptionStatus.PARTIALLY_FILLED
        
        # Calculate next fill date
        self.calculate_next_fill_date()
    
    def add_refill(self, additional_refills: int):
        """Add additional refills to prescription"""
        self.refills_authorized += additional_refills
        self.refills_remaining += additional_refills
    
    def cancel_prescription(self, reason: str = None):
        """Cancel prescription"""
        self.status = PrescriptionStatus.CANCELLED
        self.cancelled_at = datetime.now()
        if reason:
            self.prescriber_notes = f"{self.prescriber_notes or ''}\nCancelled: {reason}".strip()
    
    def discontinue_prescription(self, reason: str = None):
        """Discontinue prescription"""
        self.status = PrescriptionStatus.DISCONTINUED
        self.discontinued_at = datetime.now()
        if reason:
            self.prescriber_notes = f"{self.prescriber_notes or ''}\nDiscontinued: {reason}".strip()
    
    def check_drug_interactions(self, other_prescriptions: List['Prescription']):
        """Check for drug interactions with other prescriptions"""
        interactions = []
        
        for other_rx in other_prescriptions:
            if other_rx.id != self.id and other_rx.is_active:
                # Placeholder interaction check
                # In production, this would use a drug interaction database
                if ("warfarin" in self.medication_name.lower() and 
                    "aspirin" in other_rx.medication_name.lower()):
                    interactions.append({
                        "prescription_id": other_rx.id,
                        "medication": other_rx.medication_name,
                        "severity": "major",
                        "description": "Increased risk of bleeding"
                    })
        
        self.drug_interactions = interactions
        return interactions
    
    def validate_prescription(self):
        """Validate prescription for completeness and safety"""
        errors = []
        warnings = []
        
        # Required field validation
        if not self.medication_name:
            errors.append("Medication name is required")
        if not self.sig:
            errors.append("Prescription directions (sig) are required")
        if not self.quantity_prescribed or self.quantity_prescribed <= 0:
            errors.append("Valid quantity must be specified")
        
        # Safety checks
        if self.is_controlled_substance and not self.dea_number:
            errors.append("DEA number required for controlled substances")
        
        if self.is_expired:
            warnings.append("Prescription has expired")
        
        if not self.allergies_checked:
            warnings.append("Patient allergies not verified")
        
        return {"errors": errors, "warnings": warnings}
    
    def generate_prescription_label(self):
        """Generate prescription label information"""
        return {
            "rx_number": self.rx_number,
            "patient_name": self.patient.user.full_name if self.patient else "Unknown",
            "medication": self.full_medication_name,
            "directions": self.sig,
            "quantity": f"{self.quantity_prescribed} {self.unit_of_measure}",
            "refills": f"{self.refills_remaining} refills remaining",
            "prescriber": self.prescriber.full_name if self.prescriber else "Unknown",
            "date_filled": self.date_filled.strftime("%m/%d/%Y") if self.date_filled else None,
            "pharmacy": self.pharmacy_name,
            "discard_after": self.expiration_date.strftime("%m/%d/%Y") if self.expiration_date else None
        }
    
    def get_medication_guide_info(self):
        """Get medication guide information"""
        # This would integrate with medication database
        return {
            "medication_name": self.medication_name,
            "generic_name": self.generic_name,
            "indication": self.indication,
            "common_side_effects": self.side_effects_reported or [],
            "contraindications": self.contraindications or [],
            "storage_instructions": "Store at room temperature",
            "special_instructions": self.special_instructions
        }
    
    @classmethod
    def create_prescription(cls, patient_id: int, prescriber_id: int, 
                          medication_name: str, sig: str, quantity: int,
                          refills: int = 0):
        """Create a new prescription"""
        import uuid
        
        prescription_number = f"RX-{uuid.uuid4().hex[:8].upper()}"
        
        prescription = cls(
            patient_id=patient_id,
            prescriber_id=prescriber_id,
            prescription_number=prescription_number,
            medication_name=medication_name,
            sig=sig,
            quantity_prescribed=quantity,
            refills_authorized=refills,
            refills_remaining=refills,
            date_prescribed=datetime.now(),
            created_by_id=prescriber_id
        )
        
        # Calculate expiration date
        prescription.calculate_expiration_date()
        
        return prescription