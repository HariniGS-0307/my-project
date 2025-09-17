"""
Emergency contact model for patient emergency contacts and family members
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from typing import Optional, Dict, Any

from app.database import Base

class RelationshipType(enum.Enum):
    """Types of relationships to patient"""
    SPOUSE = "spouse"
    CHILD = "child"
    PARENT = "parent"
    SIBLING = "sibling"
    GRANDCHILD = "grandchild"
    GRANDPARENT = "grandparent"
    AUNT_UNCLE = "aunt_uncle"
    COUSIN = "cousin"
    FRIEND = "friend"
    NEIGHBOR = "neighbor"
    CAREGIVER = "caregiver"
    LEGAL_GUARDIAN = "legal_guardian"
    POWER_OF_ATTORNEY = "power_of_attorney"
    HEALTHCARE_PROXY = "healthcare_proxy"
    OTHER = "other"

class ContactPriority(enum.Enum):
    """Priority levels for emergency contacts"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    BACKUP = "backup"

class ContactStatus(enum.Enum):
    """Status of emergency contact"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNAVAILABLE = "unavailable"
    DECEASED = "deceased"

class EmergencyContact(Base):
    """Emergency contact model for patient emergency contacts"""
    
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # Contact Information
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    
    # Relationship
    relationship = Column(Enum(RelationshipType), nullable=False)
    relationship_description = Column(String(100))  # For "other" relationships
    
    # Contact Details
    primary_phone = Column(String(20), nullable=False)
    secondary_phone = Column(String(20))
    email = Column(String(100))
    
    # Address
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(10))
    country = Column(String(50), default="USA")
    
    # Priority and Availability
    priority = Column(Enum(ContactPriority), default=ContactPriority.SECONDARY)
    status = Column(Enum(ContactStatus), default=ContactStatus.ACTIVE)
    
    # Availability Information
    preferred_contact_method = Column(String(20), default="phone")  # phone, email, text
    best_time_to_call = Column(String(100))
    time_zone = Column(String(50))
    
    # Authorization and Legal
    is_authorized_for_medical_info = Column(Boolean, default=False)
    is_healthcare_proxy = Column(Boolean, default=False)
    is_power_of_attorney = Column(Boolean, default=False)
    is_legal_guardian = Column(Boolean, default=False)
    can_make_medical_decisions = Column(Boolean, default=False)
    
    # Emergency Specific
    should_contact_in_emergency = Column(Boolean, default=True)
    can_pick_up_patient = Column(Boolean, default=False)
    has_key_to_home = Column(Boolean, default=False)
    lives_with_patient = Column(Boolean, default=False)
    
    # Work Information
    employer = Column(String(100))
    work_phone = Column(String(20))
    work_address = Column(Text)
    
    # Additional Information
    languages_spoken = Column(String(200))
    special_instructions = Column(Text)
    medical_conditions = Column(Text)  # If relevant for emergency situations
    
    # Contact History
    last_contacted = Column(DateTime(timezone=True))
    last_contact_successful = Column(Boolean)
    contact_attempts = Column(Integer, default=0)
    
    # Verification
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))
    verification_method = Column(String(50))
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="emergency_contacts")
    
    def __repr__(self):
        return f"<EmergencyContact(id={self.id}, name='{self.full_name}', relationship='{self.relationship.value}', patient_id={self.patient_id})>"
    
    @property
    def full_name(self):
        """Get contact's full name"""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)
    
    @property
    def is_active(self):
        """Check if contact is active"""
        return self.status == ContactStatus.ACTIVE
    
    @property
    def is_primary_contact(self):
        """Check if this is the primary emergency contact"""
        return self.priority == ContactPriority.PRIMARY
    
    @property
    def can_authorize_treatment(self):
        """Check if contact can authorize medical treatment"""
        return (self.is_healthcare_proxy or 
                self.is_power_of_attorney or 
                self.is_legal_guardian or 
                self.can_make_medical_decisions)
    
    @property
    def full_address(self):
        """Get formatted full address"""
        parts = []
        if self.address_line1:
            parts.append(self.address_line1)
        if self.address_line2:
            parts.append(self.address_line2)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.zip_code:
            parts.append(self.zip_code)
        if self.country and self.country != "USA":
            parts.append(self.country)
        
        return ", ".join(parts) if parts else None
    
    @property
    def contact_info_summary(self):
        """Get summary of contact information"""
        info = {
            "name": self.full_name,
            "relationship": self.get_relationship_display(),
            "primary_phone": self.primary_phone,
            "priority": self.priority.value,
            "can_authorize": self.can_authorize_treatment
        }
        
        if self.email:
            info["email"] = self.email
        if self.secondary_phone:
            info["secondary_phone"] = self.secondary_phone
            
        return info
    
    def get_relationship_display(self):
        """Get human-readable relationship description"""
        if self.relationship == RelationshipType.OTHER and self.relationship_description:
            return self.relationship_description
        
        relationship_labels = {
            RelationshipType.SPOUSE: "Spouse",
            RelationshipType.CHILD: "Child",
            RelationshipType.PARENT: "Parent",
            RelationshipType.SIBLING: "Sibling",
            RelationshipType.GRANDCHILD: "Grandchild",
            RelationshipType.GRANDPARENT: "Grandparent",
            RelationshipType.AUNT_UNCLE: "Aunt/Uncle",
            RelationshipType.COUSIN: "Cousin",
            RelationshipType.FRIEND: "Friend",
            RelationshipType.NEIGHBOR: "Neighbor",
            RelationshipType.CAREGIVER: "Caregiver",
            RelationshipType.LEGAL_GUARDIAN: "Legal Guardian",
            RelationshipType.POWER_OF_ATTORNEY: "Power of Attorney",
            RelationshipType.HEALTHCARE_PROXY: "Healthcare Proxy",
            RelationshipType.OTHER: "Other"
        }
        
        return relationship_labels.get(self.relationship, "Unknown")
    
    def record_contact_attempt(self, successful: bool = False, notes: str = None):
        """Record a contact attempt"""
        self.last_contacted = datetime.now()
        self.last_contact_successful = successful
        self.contact_attempts += 1
        
        if notes:
            current_notes = self.notes or ""
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            contact_note = f"[{timestamp}] Contact attempt {'successful' if successful else 'failed'}: {notes}"
            self.notes = f"{current_notes}\n{contact_note}".strip()
    
    def verify_contact(self, method: str = "phone"):
        """Mark contact as verified"""
        self.is_verified = True
        self.verification_date = datetime.now()
        self.verification_method = method
    
    def update_contact_info(self, **kwargs):
        """Update contact information"""
        updatable_fields = [
            'primary_phone', 'secondary_phone', 'email', 'address_line1', 
            'address_line2', 'city', 'state', 'zip_code', 'employer', 
            'work_phone', 'preferred_contact_method', 'best_time_to_call'
        ]
        
        for field, value in kwargs.items():
            if field in updatable_fields and hasattr(self, field):
                setattr(self, field, value)
        
        # Reset verification if contact info changed
        if any(field in ['primary_phone', 'secondary_phone', 'email'] for field in kwargs.keys()):
            self.is_verified = False
            self.verification_date = None
    
    def set_as_primary(self):
        """Set this contact as primary emergency contact"""
        self.priority = ContactPriority.PRIMARY
        self.should_contact_in_emergency = True
    
    def deactivate(self, reason: str = None):
        """Deactivate emergency contact"""
        self.status = ContactStatus.INACTIVE
        if reason:
            current_notes = self.notes or ""
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            deactivation_note = f"[{timestamp}] Deactivated: {reason}"
            self.notes = f"{current_notes}\n{deactivation_note}".strip()
    
    def get_contact_methods(self):
        """Get available contact methods"""
        methods = []
        
        if self.primary_phone:
            methods.append({
                "type": "phone",
                "value": self.primary_phone,
                "label": "Primary Phone",
                "preferred": self.preferred_contact_method == "phone"
            })
        
        if self.secondary_phone:
            methods.append({
                "type": "phone",
                "value": self.secondary_phone,
                "label": "Secondary Phone",
                "preferred": False
            })
        
        if self.email:
            methods.append({
                "type": "email",
                "value": self.email,
                "label": "Email",
                "preferred": self.preferred_contact_method == "email"
            })
        
        if self.work_phone:
            methods.append({
                "type": "phone",
                "value": self.work_phone,
                "label": "Work Phone",
                "preferred": False
            })
        
        return methods
    
    def get_authorization_summary(self):
        """Get summary of legal authorizations"""
        authorizations = []
        
        if self.is_healthcare_proxy:
            authorizations.append("Healthcare Proxy")
        if self.is_power_of_attorney:
            authorizations.append("Power of Attorney")
        if self.is_legal_guardian:
            authorizations.append("Legal Guardian")
        if self.can_make_medical_decisions:
            authorizations.append("Medical Decision Maker")
        if self.is_authorized_for_medical_info:
            authorizations.append("Medical Information Access")
        
        return authorizations
    
    @classmethod
    def get_primary_contact(cls, db_session, patient_id: int):
        """Get primary emergency contact for patient"""
        return db_session.query(cls).filter(
            cls.patient_id == patient_id,
            cls.priority == ContactPriority.PRIMARY,
            cls.status == ContactStatus.ACTIVE
        ).first()
    
    @classmethod
    def get_emergency_contacts(cls, db_session, patient_id: int, active_only: bool = True):
        """Get all emergency contacts for patient, ordered by priority"""
        query = db_session.query(cls).filter(cls.patient_id == patient_id)
        
        if active_only:
            query = query.filter(cls.status == ContactStatus.ACTIVE)
        
        # Order by priority (primary first)
        priority_order = {
            ContactPriority.PRIMARY: 1,
            ContactPriority.SECONDARY: 2,
            ContactPriority.TERTIARY: 3,
            ContactPriority.BACKUP: 4
        }
        
        contacts = query.all()
        return sorted(contacts, key=lambda x: priority_order.get(x.priority, 5))
    
    @classmethod
    def get_authorized_contacts(cls, db_session, patient_id: int):
        """Get contacts authorized to receive medical information"""
        return db_session.query(cls).filter(
            cls.patient_id == patient_id,
            cls.status == ContactStatus.ACTIVE,
            cls.is_authorized_for_medical_info == True
        ).all()
    
    def to_dict(self):
        """Convert emergency contact to dictionary"""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "relationship": self.get_relationship_display(),
            "primary_phone": self.primary_phone,
            "secondary_phone": self.secondary_phone,
            "email": self.email,
            "address": self.full_address,
            "priority": self.priority.value,
            "status": self.status.value,
            "is_authorized": self.is_authorized_for_medical_info,
            "can_authorize_treatment": self.can_authorize_treatment,
            "preferred_contact_method": self.preferred_contact_method,
            "best_time_to_call": self.best_time_to_call,
            "last_contacted": self.last_contacted.isoformat() if self.last_contacted else None,
            "is_verified": self.is_verified,
            "authorizations": self.get_authorization_summary()
        }