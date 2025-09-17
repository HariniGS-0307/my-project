"""
Medication-related Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

from app.models.medication import MedicationType, MedicationStatus, FrequencyType

class MedicationBase(BaseModel):
    """Base medication schema with common fields"""
    name: str = Field(..., min_length=2, max_length=200)
    generic_name: Optional[str] = Field(None, max_length=200)
    brand_name: Optional[str] = Field(None, max_length=200)
    medication_type: MedicationType
    strength: Optional[str] = Field(None, max_length=50)
    dosage_form: Optional[str] = Field(None, max_length=50)
    
    @validator('name')
    def validate_medication_name(cls, v):
        import re
        if not re.match(r'^[A-Za-z0-9\s\-\(\)\.]+$', v.strip()):
            raise ValueError('Medication name contains invalid characters')
        return v.strip()
    
    @validator('strength')
    def validate_strength(cls, v):
        if v is not None:
            import re
            # Common strength patterns: 10mg, 5ml, 2.5mg, etc.
            if not re.match(r'^\d+(\.\d+)?\s*(mg|g|ml|l|mcg|units?|iu)$', v.lower().strip()):
                raise ValueError('Invalid strength format (e.g., 10mg, 5ml)')
        return v

class MedicationCreate(MedicationBase):
    """Schema for medication creation"""
    patient_id: int
    dosage_amount: Optional[float] = Field(None, gt=0)
    dosage_unit: Optional[str] = Field(None, max_length=20)
    frequency: FrequencyType
    frequency_details: Optional[str] = Field(None, max_length=100)
    route_of_administration: Optional[str] = Field(None, max_length=50)
    instructions: Optional[str] = Field(None, max_length=1000)
    start_date: datetime
    end_date: Optional[datetime] = None
    duration_days: Optional[int] = Field(None, gt=0, le=365)
    quantity_prescribed: Optional[int] = Field(None, gt=0)
    refills_remaining: Optional[int] = Field(0, ge=0, le=12)
    is_critical: Optional[bool] = False
    requires_monitoring: Optional[bool] = False
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v is not None and 'start_date' in values:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v
    
    @validator('dosage_amount')
    def validate_dosage_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Dosage amount must be positive')
        return v
    
    @validator('route_of_administration')
    def validate_route(cls, v):
        if v is not None:
            valid_routes = [
                'oral', 'topical', 'injection', 'intravenous', 'intramuscular',
                'subcutaneous', 'inhalation', 'rectal', 'sublingual', 'transdermal'
            ]
            if v.lower() not in valid_routes:
                raise ValueError(f'Invalid route of administration. Valid options: {", ".join(valid_routes)}')
        return v.lower() if v else v

class MedicationUpdate(BaseModel):
    """Schema for medication updates"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    generic_name: Optional[str] = Field(None, max_length=200)
    brand_name: Optional[str] = Field(None, max_length=200)
    medication_type: Optional[MedicationType] = None
    strength: Optional[str] = Field(None, max_length=50)
    dosage_form: Optional[str] = Field(None, max_length=50)
    dosage_amount: Optional[float] = Field(None, gt=0)
    dosage_unit: Optional[str] = Field(None, max_length=20)
    frequency: Optional[FrequencyType] = None
    frequency_details: Optional[str] = Field(None, max_length=100)
    route_of_administration: Optional[str] = Field(None, max_length=50)
    instructions: Optional[str] = Field(None, max_length=1000)
    end_date: Optional[datetime] = None
    duration_days: Optional[int] = Field(None, gt=0, le=365)
    quantity_prescribed: Optional[int] = Field(None, gt=0)
    quantity_remaining: Optional[int] = Field(None, ge=0)
    refills_remaining: Optional[int] = Field(None, ge=0, le=12)
    status: Optional[MedicationStatus] = None
    is_critical: Optional[bool] = None
    requires_monitoring: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('name')
    def validate_medication_name(cls, v):
        if v is not None:
            import re
            if not re.match(r'^[A-Za-z0-9\s\-\(\)\.]+$', v.strip()):
                raise ValueError('Medication name contains invalid characters')
        return v.strip() if v else v

class MedicationResponse(BaseModel):
    """Schema for medication response"""
    id: int
    patient_id: int
    prescribed_by_id: int
    prescription_id: Optional[int]
    name: str
    generic_name: Optional[str]
    brand_name: Optional[str]
    ndc_number: Optional[str]
    medication_type: MedicationType
    strength: Optional[str]
    dosage_form: Optional[str]
    dosage_amount: Optional[float]
    dosage_unit: Optional[str]
    frequency: FrequencyType
    frequency_details: Optional[str]
    route_of_administration: Optional[str]
    instructions: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    duration_days: Optional[int]
    status: MedicationStatus
    quantity_prescribed: Optional[int]
    quantity_remaining: Optional[int]
    refills_remaining: Optional[int]
    last_refill_date: Optional[datetime]
    next_refill_due: Optional[datetime]
    is_critical: bool
    requires_monitoring: bool
    adherence_score: Optional[float]
    missed_doses: int
    last_taken: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed fields
    is_active: bool
    is_due_for_refill: bool
    days_supply_remaining: int
    is_expired: bool
    full_name: str
    
    # Related information
    prescribed_by_name: Optional[str] = None
    patient_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class MedicationListResponse(BaseModel):
    """Schema for paginated medication list response"""
    medications: List[MedicationResponse]
    total: int
    page: int
    per_page: int
    pages: int

class DoseTaken(BaseModel):
    """Schema for recording a dose taken"""
    taken_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    side_effects: Optional[List[str]] = []
    effectiveness: Optional[int] = Field(None, ge=1, le=10)  # 1-10 scale
    
    @validator('taken_at')
    def validate_taken_at(cls, v):
        if v is not None and v > datetime.now():
            raise ValueError('Dose taken time cannot be in the future')
        return v

class MissedDose(BaseModel):
    """Schema for recording a missed dose"""
    missed_at: datetime
    reason: Optional[str] = Field(None, max_length=500)
    will_take_later: Optional[bool] = False
    
    @validator('missed_at')
    def validate_missed_at(cls, v):
        if v > datetime.now():
            raise ValueError('Missed dose time cannot be in the future')
        return v

class RefillRequest(BaseModel):
    """Schema for medication refill request"""
    quantity: int = Field(..., gt=0)
    refills: Optional[int] = Field(0, ge=0, le=12)
    pharmacy_name: Optional[str] = Field(None, max_length=200)
    pharmacy_phone: Optional[str] = Field(None, max_length=20)
    pharmacy_notes: Optional[str] = Field(None, max_length=500)
    requested_date: Optional[date] = None
    
    @validator('requested_date')
    def validate_requested_date(cls, v):
        if v is not None and v < date.today():
            raise ValueError('Requested date cannot be in the past')
        return v

class MedicationInteraction(BaseModel):
    """Schema for medication interaction"""
    medication1_id: int
    medication2_id: int
    interaction_type: str = Field(..., regex="^(major|moderate|minor)$")
    description: str = Field(..., max_length=1000)
    severity_score: Optional[float] = Field(None, ge=0, le=10)
    recommendations: Optional[str] = Field(None, max_length=1000)

class MedicationAdherence(BaseModel):
    """Schema for medication adherence tracking"""
    medication_id: int
    patient_id: int
    period_start: date
    period_end: date
    prescribed_doses: int = Field(..., gt=0)
    taken_doses: int = Field(..., ge=0)
    missed_doses: int = Field(..., ge=0)
    adherence_percentage: float = Field(..., ge=0, le=100)
    
    @validator('period_end')
    def validate_period(cls, v, values):
        if 'period_start' in values and v <= values['period_start']:
            raise ValueError('Period end must be after period start')
        return v
    
    @validator('adherence_percentage')
    def validate_adherence(cls, v, values):
        if 'prescribed_doses' in values and 'taken_doses' in values:
            calculated = (values['taken_doses'] / values['prescribed_doses']) * 100
            if abs(v - calculated) > 1:  # Allow small rounding differences
                raise ValueError('Adherence percentage does not match taken/prescribed doses')
        return v

class MedicationSchedule(BaseModel):
    """Schema for medication schedule"""
    medication_id: int
    schedule_times: List[str] = Field(..., min_items=1)  # Times in HH:MM format
    days_of_week: Optional[List[int]] = Field(None, min_items=1, max_items=7)  # 0=Monday, 6=Sunday
    special_instructions: Optional[str] = Field(None, max_length=500)
    
    @validator('schedule_times')
    def validate_times(cls, v):
        import re
        for time_str in v:
            if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', time_str):
                raise ValueError(f'Invalid time format: {time_str}. Use HH:MM format')
        return v
    
    @validator('days_of_week')
    def validate_days(cls, v):
        if v is not None:
            for day in v:
                if day < 0 or day > 6:
                    raise ValueError('Days of week must be 0-6 (0=Monday, 6=Sunday)')
        return v

class MedicationAlert(BaseModel):
    """Schema for medication alerts"""
    medication_id: int
    alert_type: str = Field(..., regex="^(refill|interaction|side_effect|missed_dose|expiration)$")
    severity: str = Field(..., regex="^(low|medium|high|critical)$")
    message: str = Field(..., max_length=500)
    action_required: Optional[str] = Field(None, max_length=500)
    expires_at: Optional[datetime] = None

class MedicationSearchFilters(BaseModel):
    """Schema for medication search filters"""
    search: Optional[str] = None
    patient_id: Optional[int] = None
    status: Optional[MedicationStatus] = None
    medication_type: Optional[MedicationType] = None
    is_critical: Optional[bool] = None
    requires_monitoring: Optional[bool] = None
    prescribed_by_id: Optional[int] = None
    due_for_refill: Optional[bool] = None
    adherence_below: Optional[float] = Field(None, ge=0, le=100)

class MedicationStats(BaseModel):
    """Schema for medication statistics"""
    total_medications: int
    active_medications: int
    critical_medications: int
    medications_due_for_refill: int
    average_adherence: float
    medications_by_type: Dict[str, int]
    medications_by_status: Dict[str, int]

class MedicationHistory(BaseModel):
    """Schema for medication history"""
    medication_id: int
    action: str = Field(..., regex="^(prescribed|taken|missed|refilled|discontinued|modified)$")
    action_date: datetime
    details: Optional[str] = Field(None, max_length=500)
    performed_by_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class MedicationReminder(BaseModel):
    """Schema for medication reminder settings"""
    medication_id: int
    reminder_times: List[str] = Field(..., min_items=1)  # Times in HH:MM format
    reminder_methods: List[str] = Field(..., min_items=1)  # email, sms, push, call
    advance_minutes: Optional[int] = Field(15, ge=0, le=120)  # Minutes before dose time
    is_active: Optional[bool] = True
    
    @validator('reminder_times')
    def validate_times(cls, v):
        import re
        for time_str in v:
            if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', time_str):
                raise ValueError(f'Invalid time format: {time_str}. Use HH:MM format')
        return v
    
    @validator('reminder_methods')
    def validate_methods(cls, v):
        valid_methods = ['email', 'sms', 'push', 'call']
        for method in v:
            if method not in valid_methods:
                raise ValueError(f'Invalid reminder method: {method}. Valid options: {", ".join(valid_methods)}')
        return v

class MedicationDiscontinue(BaseModel):
    """Schema for discontinuing medication"""
    reason: str = Field(..., max_length=500)
    discontinue_date: Optional[date] = None
    alternative_medication: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('discontinue_date')
    def validate_discontinue_date(cls, v):
        if v is not None and v > date.today():
            raise ValueError('Discontinue date cannot be in the future')
        return v