"""
Patient-related Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

from app.models.patient import Gender, BloodType

class PatientBase(BaseModel):
    """Base patient schema with common fields"""
    date_of_birth: date
    gender: Gender
    blood_type: Optional[BloodType] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field("USA", max_length=50)
    
    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        if v > date.today():
            raise ValueError('Birth date cannot be in the future')
        
        # Calculate age
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        
        if age < 0 or age > 150:
            raise ValueError('Age must be between 0 and 150 years')
        
        return v
    
    @validator('zip_code')
    def validate_zip_code(cls, v):
        if v is not None:
            # US ZIP code validation
            import re
            if not re.match(r'^\d{5}(-\d{4})?$', v):
                raise ValueError('Invalid ZIP code format')
        return v

class PatientCreate(PatientBase):
    """Schema for patient creation"""
    user_id: int
    height: Optional[float] = Field(None, gt=0, le=300)  # cm
    weight: Optional[float] = Field(None, gt=0, le=500)  # kg
    medical_record_number: Optional[str] = Field(None, max_length=50)
    insurance_number: Optional[str] = Field(None, max_length=100)
    medicare_number: Optional[str] = Field(None, max_length=50)
    primary_physician_id: Optional[int] = None
    assigned_caregiver_id: Optional[int] = None
    care_plan: Optional[str] = Field(None, max_length=2000)
    special_needs: Optional[str] = Field(None, max_length=1000)
    
    @validator('height')
    def validate_height(cls, v):
        if v is not None and (v < 50 or v > 250):
            raise ValueError('Height must be between 50-250 cm')
        return v
    
    @validator('weight')
    def validate_weight(cls, v):
        if v is not None and (v < 20 or v > 300):
            raise ValueError('Weight must be between 20-300 kg')
        return v
    
    @validator('medical_record_number')
    def validate_mrn(cls, v):
        if v is not None:
            import re
            # Remove spaces and hyphens
            cleaned = re.sub(r'[\s-]', '', v)
            if not re.match(r'^[A-Za-z0-9]{6,20}$', cleaned):
                raise ValueError('Medical record number must be 6-20 alphanumeric characters')
        return v
    
    @validator('medicare_number')
    def validate_medicare(cls, v):
        if v is not None:
            import re
            # New Medicare format or old SSN-based format
            new_format = r'^\d[A-Za-z]{2}\d-[A-Za-z]{2}\d-[A-Za-z]{2}\d{2}$'
            old_format = r'^\d{3}-\d{2}-\d{4}[A-Za-z]?$'
            
            if not (re.match(new_format, v) or re.match(old_format, v)):
                raise ValueError('Invalid Medicare number format')
        return v

class PatientUpdate(BaseModel):
    """Schema for patient updates"""
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    blood_type: Optional[BloodType] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=50)
    height: Optional[float] = Field(None, gt=0, le=300)
    weight: Optional[float] = Field(None, gt=0, le=500)
    medical_record_number: Optional[str] = Field(None, max_length=50)
    insurance_number: Optional[str] = Field(None, max_length=100)
    medicare_number: Optional[str] = Field(None, max_length=50)
    primary_physician_id: Optional[int] = None
    assigned_caregiver_id: Optional[int] = None
    care_plan: Optional[str] = Field(None, max_length=2000)
    special_needs: Optional[str] = Field(None, max_length=1000)
    risk_level: Optional[str] = Field(None, regex="^(low|medium|high|critical)$")
    mobility_status: Optional[str] = Field(None, max_length=50)
    cognitive_status: Optional[str] = Field(None, max_length=50)
    
    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        if v is not None:
            if v > date.today():
                raise ValueError('Birth date cannot be in the future')
            
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            
            if age < 0 or age > 150:
                raise ValueError('Age must be between 0 and 150 years')
        return v
    
    @validator('height')
    def validate_height(cls, v):
        if v is not None and (v < 50 or v > 250):
            raise ValueError('Height must be between 50-250 cm')
        return v
    
    @validator('weight')
    def validate_weight(cls, v):
        if v is not None and (v < 20 or v > 300):
            raise ValueError('Weight must be between 20-300 kg')
        return v

class PatientResponse(BaseModel):
    """Schema for patient response"""
    id: int
    patient_id: str
    user_id: int
    date_of_birth: date
    gender: Gender
    blood_type: Optional[BloodType]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    country: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    medical_record_number: Optional[str]
    insurance_number: Optional[str]
    medicare_number: Optional[str]
    risk_level: str
    mobility_status: Optional[str]
    cognitive_status: Optional[str]
    care_plan: Optional[str]
    special_needs: Optional[str]
    is_active_patient: bool
    primary_physician_id: Optional[int]
    assigned_caregiver_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    last_visit: Optional[datetime]
    
    # Computed fields
    age: Optional[int] = None
    bmi: Optional[float] = None
    is_elderly: Optional[bool] = None
    full_address: Optional[str] = None
    
    # User information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    
    # Healthcare provider information
    primary_physician_name: Optional[str] = None
    assigned_caregiver_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class PatientListResponse(BaseModel):
    """Schema for paginated patient list response"""
    patients: List[PatientResponse]
    total: int
    page: int
    per_page: int
    pages: int

class PatientSummary(BaseModel):
    """Schema for patient summary information"""
    patient_info: Dict[str, Any]
    health_metrics: Dict[str, Any]
    care_summary: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
    alerts: List[str]
    upcoming_events: List[Dict[str, Any]]

class PatientSearchFilters(BaseModel):
    """Schema for patient search filters"""
    search: Optional[str] = None
    risk_level: Optional[str] = Field(None, regex="^(low|medium|high|critical)$")
    is_active: Optional[bool] = None
    age_min: Optional[int] = Field(None, ge=0, le=150)
    age_max: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[Gender] = None
    primary_physician_id: Optional[int] = None
    assigned_caregiver_id: Optional[int] = None
    has_chronic_conditions: Optional[bool] = None
    
    @validator('age_max')
    def validate_age_range(cls, v, values):
        if v is not None and 'age_min' in values and values['age_min'] is not None:
            if v < values['age_min']:
                raise ValueError('Maximum age must be greater than minimum age')
        return v

class PatientVitalSigns(BaseModel):
    """Schema for patient vital signs"""
    systolic_bp: Optional[int] = Field(None, ge=50, le=300)
    diastolic_bp: Optional[int] = Field(None, ge=30, le=200)
    heart_rate: Optional[int] = Field(None, ge=30, le=250)
    temperature: Optional[float] = Field(None, ge=90.0, le=110.0)
    respiratory_rate: Optional[int] = Field(None, ge=5, le=60)
    oxygen_saturation: Optional[float] = Field(None, ge=70.0, le=100.0)
    blood_sugar: Optional[float] = Field(None, ge=50.0, le=600.0)
    pain_level: Optional[int] = Field(None, ge=0, le=10)
    
    @validator('diastolic_bp')
    def validate_bp_ratio(cls, v, values):
        if v is not None and 'systolic_bp' in values and values['systolic_bp'] is not None:
            if v >= values['systolic_bp']:
                raise ValueError('Diastolic BP must be lower than systolic BP')
        return v

class PatientHealthRecord(BaseModel):
    """Schema for patient health record entry"""
    vital_signs: Optional[PatientVitalSigns] = None
    symptoms: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=2000)
    diagnosis: Optional[str] = Field(None, max_length=500)
    treatment_plan: Optional[str] = Field(None, max_length=1000)
    recorded_at: Optional[datetime] = None

class PatientMedicalHistory(BaseModel):
    """Schema for patient medical history"""
    conditions: List[str] = []
    allergies: List[str] = []
    surgeries: List[Dict[str, Any]] = []
    family_history: List[str] = []
    social_history: Optional[str] = Field(None, max_length=1000)
    
    @validator('conditions', 'allergies', 'family_history')
    def validate_lists(cls, v):
        if len(v) > 50:  # Reasonable limit
            raise ValueError('Too many items in list')
        return v

class PatientEmergencyContact(BaseModel):
    """Schema for patient emergency contact"""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    relationship: str = Field(..., max_length=50)
    primary_phone: str = Field(..., max_length=20)
    secondary_phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    address: Optional[str] = Field(None, max_length=500)
    is_primary: Optional[bool] = False
    can_make_decisions: Optional[bool] = False

class PatientCareTeam(BaseModel):
    """Schema for patient care team"""
    primary_physician: Optional[Dict[str, Any]] = None
    specialists: List[Dict[str, Any]] = []
    nurses: List[Dict[str, Any]] = []
    caregivers: List[Dict[str, Any]] = []
    therapists: List[Dict[str, Any]] = []

class PatientInsurance(BaseModel):
    """Schema for patient insurance information"""
    primary_insurance: Optional[str] = Field(None, max_length=100)
    secondary_insurance: Optional[str] = Field(None, max_length=100)
    medicare_number: Optional[str] = Field(None, max_length=50)
    medicaid_number: Optional[str] = Field(None, max_length=50)
    insurance_group: Optional[str] = Field(None, max_length=50)
    policy_number: Optional[str] = Field(None, max_length=50)
    copay_amount: Optional[float] = Field(None, ge=0)
    deductible: Optional[float] = Field(None, ge=0)

class PatientPreferences(BaseModel):
    """Schema for patient preferences"""
    preferred_language: Optional[str] = Field(None, max_length=50)
    communication_preference: Optional[str] = Field(None, regex="^(phone|email|text|mail)$")
    appointment_reminders: Optional[bool] = True
    medication_reminders: Optional[bool] = True
    health_tips: Optional[bool] = True
    emergency_notifications: Optional[bool] = True
    dietary_restrictions: List[str] = []
    accessibility_needs: List[str] = []

class PatientStats(BaseModel):
    """Schema for patient statistics"""
    total_patients: int
    active_patients: int
    elderly_patients: int
    high_risk_patients: int
    patients_by_risk_level: Dict[str, int]
    average_age: float
    gender_distribution: Dict[str, int]

class PatientAssignCaregiver(BaseModel):
    """Schema for assigning caregiver to patient"""
    caregiver_id: int
    assignment_type: Optional[str] = Field("primary", regex="^(primary|secondary|respite|temporary)$")
    start_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)

class PatientTransfer(BaseModel):
    """Schema for patient transfer between facilities"""
    from_facility: str = Field(..., max_length=200)
    to_facility: str = Field(..., max_length=200)
    transfer_date: date
    transfer_reason: str = Field(..., max_length=500)
    medical_summary: Optional[str] = Field(None, max_length=2000)
    medications_list: List[str] = []
    special_instructions: Optional[str] = Field(None, max_length=1000)