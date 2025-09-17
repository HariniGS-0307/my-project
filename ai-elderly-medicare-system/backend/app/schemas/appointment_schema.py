"""
Appointment-related Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from enum import Enum

from app.models.appointment import AppointmentType, AppointmentStatus, Priority

class AppointmentBase(BaseModel):
    """Base appointment schema with common fields"""
    appointment_date: datetime
    duration_minutes: Optional[int] = Field(30, ge=5, le=480)  # 5 minutes to 8 hours
    appointment_type: AppointmentType
    priority: Optional[Priority] = Priority.MEDIUM
    location: Optional[str] = Field(None, max_length=200)
    room_number: Optional[str] = Field(None, max_length=20)
    is_virtual: Optional[bool] = False
    virtual_meeting_link: Optional[str] = Field(None, max_length=500)
    
    @validator('appointment_date')
    def validate_appointment_date(cls, v):
        if v <= datetime.now():
            raise ValueError('Appointment date must be in the future')
        return v
    
    @validator('virtual_meeting_link')
    def validate_meeting_link(cls, v, values):
        if values.get('is_virtual', False) and not v:
            raise ValueError('Virtual meeting link is required for virtual appointments')
        if v and not values.get('is_virtual', False):
            raise ValueError('Virtual meeting link should only be provided for virtual appointments')
        return v

class AppointmentCreate(AppointmentBase):
    """Schema for appointment creation"""
    patient_id: int
    provider_id: int
    chief_complaint: Optional[str] = Field(None, max_length=1000)
    reason_for_visit: Optional[str] = Field(None, max_length=1000)
    preparation_instructions: Optional[str] = Field(None, max_length=1000)
    insurance_authorization: Optional[str] = Field(None, max_length=100)
    copay_amount: Optional[int] = Field(None, ge=0)  # in cents
    billing_code: Optional[str] = Field(None, max_length=20)
    confirmation_required: Optional[bool] = True
    notes: Optional[str] = Field(None, max_length=2000)

class AppointmentUpdate(BaseModel):
    """Schema for appointment updates"""
    appointment_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=5, le=480)
    appointment_type: Optional[AppointmentType] = None
    status: Optional[AppointmentStatus] = None
    priority: Optional[Priority] = None
    location: Optional[str] = Field(None, max_length=200)
    room_number: Optional[str] = Field(None, max_length=20)
    is_virtual: Optional[bool] = None
    virtual_meeting_link: Optional[str] = Field(None, max_length=500)
    chief_complaint: Optional[str] = Field(None, max_length=1000)
    reason_for_visit: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=2000)
    preparation_instructions: Optional[str] = Field(None, max_length=1000)
    follow_up_required: Optional[bool] = None
    follow_up_date: Optional[datetime] = None
    follow_up_notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('appointment_date')
    def validate_appointment_date(cls, v):
        if v is not None and v <= datetime.now():
            raise ValueError('Appointment date must be in the future')
        return v
    
    @validator('follow_up_date')
    def validate_follow_up_date(cls, v, values):
        if v is not None:
            if 'appointment_date' in values and values['appointment_date']:
                if v <= values['appointment_date']:
                    raise ValueError('Follow-up date must be after appointment date')
            elif v <= datetime.now():
                raise ValueError('Follow-up date must be in the future')
        return v

class AppointmentResponse(BaseModel):
    """Schema for appointment response"""
    id: int
    patient_id: int
    provider_id: int
    appointment_date: datetime
    duration_minutes: int
    appointment_type: AppointmentType
    status: AppointmentStatus
    priority: Priority
    location: Optional[str]
    room_number: Optional[str]
    is_virtual: bool
    virtual_meeting_link: Optional[str]
    chief_complaint: Optional[str]
    reason_for_visit: Optional[str]
    notes: Optional[str]
    preparation_instructions: Optional[str]
    follow_up_required: bool
    follow_up_date: Optional[datetime]
    follow_up_notes: Optional[str]
    insurance_authorization: Optional[str]
    copay_amount: Optional[int]
    billing_code: Optional[str]
    reminder_sent: bool
    confirmation_required: bool
    confirmed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Computed fields
    end_time: Optional[datetime] = None
    is_upcoming: bool = False
    is_today: bool = False
    is_overdue: bool = False
    formatted_date_time: Optional[str] = None
    
    # Related information
    patient_name: Optional[str] = None
    provider_name: Optional[str] = None
    patient_phone: Optional[str] = None
    provider_specialization: Optional[str] = None
    
    class Config:
        from_attributes = True

class AppointmentListResponse(BaseModel):
    """Schema for paginated appointment list response"""
    appointments: List[AppointmentResponse]
    total: int
    page: int
    per_page: int
    pages: int

class AppointmentReschedule(BaseModel):
    """Schema for rescheduling appointment"""
    new_appointment_date: datetime
    reason: Optional[str] = Field(None, max_length=500)
    notify_patient: Optional[bool] = True
    
    @validator('new_appointment_date')
    def validate_new_date(cls, v):
        if v <= datetime.now():
            raise ValueError('New appointment date must be in the future')
        return v

class AppointmentCancel(BaseModel):
    """Schema for cancelling appointment"""
    reason: str = Field(..., max_length=500)
    notify_patient: Optional[bool] = True
    reschedule_offered: Optional[bool] = False

class AppointmentConfirm(BaseModel):
    """Schema for confirming appointment"""
    confirmed: bool = True
    confirmation_method: Optional[str] = Field(None, regex="^(phone|email|sms|in_person)$")
    notes: Optional[str] = Field(None, max_length=500)

class AppointmentComplete(BaseModel):
    """Schema for completing appointment"""
    completion_notes: Optional[str] = Field(None, max_length=2000)
    diagnosis: Optional[str] = Field(None, max_length=1000)
    treatment_provided: Optional[str] = Field(None, max_length=1000)
    follow_up_required: Optional[bool] = False
    follow_up_date: Optional[datetime] = None
    follow_up_instructions: Optional[str] = Field(None, max_length=1000)
    prescriptions_issued: Optional[List[str]] = []
    
    @validator('follow_up_date')
    def validate_follow_up_date(cls, v):
        if v is not None and v <= datetime.now():
            raise ValueError('Follow-up date must be in the future')
        return v

class AppointmentSearchFilters(BaseModel):
    """Schema for appointment search filters"""
    search: Optional[str] = None
    patient_id: Optional[int] = None
    provider_id: Optional[int] = None
    appointment_type: Optional[AppointmentType] = None
    status: Optional[AppointmentStatus] = None
    priority: Optional[Priority] = None
    is_virtual: Optional[bool] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    is_today: Optional[bool] = None
    is_upcoming: Optional[bool] = None
    is_overdue: Optional[bool] = None
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        if v is not None and 'date_from' in values and values['date_from'] is not None:
            if v < values['date_from']:
                raise ValueError('End date must be after start date')
        return v

class AppointmentStats(BaseModel):
    """Schema for appointment statistics"""
    total_appointments: int
    scheduled_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    no_show_appointments: int
    virtual_appointments: int
    appointments_today: int
    appointments_this_week: int
    appointments_by_type: Dict[str, int]
    appointments_by_status: Dict[str, int]
    average_duration: float

class AppointmentReminder(BaseModel):
    """Schema for appointment reminder settings"""
    appointment_id: int
    reminder_methods: List[str] = Field(..., min_items=1)  # email, sms, phone, push
    hours_before: List[int] = Field([24, 2], min_items=1)  # Hours before appointment
    custom_message: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = True
    
    @validator('reminder_methods')
    def validate_methods(cls, v):
        valid_methods = ['email', 'sms', 'phone', 'push']
        for method in v:
            if method not in valid_methods:
                raise ValueError(f'Invalid reminder method: {method}. Valid options: {", ".join(valid_methods)}')
        return v
    
    @validator('hours_before')
    def validate_hours(cls, v):
        for hours in v:
            if hours < 0 or hours > 168:  # Max 1 week before
                raise ValueError('Hours before must be between 0 and 168 (1 week)')
        return sorted(set(v), reverse=True)  # Remove duplicates and sort descending

class AppointmentAvailability(BaseModel):
    """Schema for checking provider availability"""
    provider_id: int
    date: date
    duration_minutes: Optional[int] = 30
    appointment_type: Optional[AppointmentType] = None
    
    @validator('date')
    def validate_date(cls, v):
        if v < date.today():
            raise ValueError('Date cannot be in the past')
        return v

class AvailableSlot(BaseModel):
    """Schema for available appointment slot"""
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    is_available: bool
    slot_type: Optional[str] = None  # regular, emergency, walk_in

class AppointmentAvailabilityResponse(BaseModel):
    """Schema for availability response"""
    provider_id: int
    provider_name: str
    date: date
    available_slots: List[AvailableSlot]
    total_slots: int
    available_count: int
    working_hours: Dict[str, str]  # start_time, end_time

class AppointmentWaitlist(BaseModel):
    """Schema for appointment waitlist"""
    patient_id: int
    provider_id: int
    preferred_date_from: date
    preferred_date_to: date
    preferred_times: Optional[List[str]] = []  # HH:MM format
    appointment_type: AppointmentType
    priority: Optional[Priority] = Priority.MEDIUM
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('preferred_date_to')
    def validate_date_range(cls, v, values):
        if 'preferred_date_from' in values and v < values['preferred_date_from']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('preferred_times')
    def validate_times(cls, v):
        if v:
            import re
            for time_str in v:
                if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', time_str):
                    raise ValueError(f'Invalid time format: {time_str}. Use HH:MM format')
        return v

class AppointmentHistory(BaseModel):
    """Schema for appointment history"""
    appointment_id: int
    action: str = Field(..., regex="^(scheduled|confirmed|rescheduled|cancelled|completed|no_show)$")
    action_date: datetime
    performed_by_id: Optional[int] = None
    reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    
    class Config:
        from_attributes = True

class AppointmentConflict(BaseModel):
    """Schema for appointment conflict detection"""
    conflicting_appointment_id: int
    conflict_type: str = Field(..., regex="^(time_overlap|double_booking|resource_conflict)$")
    conflict_description: str
    suggested_resolution: Optional[str] = None

class AppointmentBulkAction(BaseModel):
    """Schema for bulk appointment actions"""
    appointment_ids: List[int] = Field(..., min_items=1, max_items=100)
    action: str = Field(..., regex="^(cancel|reschedule|confirm|send_reminder)$")
    reason: Optional[str] = Field(None, max_length=500)
    new_date: Optional[datetime] = None  # For reschedule action
    notify_patients: Optional[bool] = True
    
    @validator('new_date')
    def validate_new_date(cls, v, values):
        if values.get('action') == 'reschedule' and not v:
            raise ValueError('New date is required for reschedule action')
        if v is not None and v <= datetime.now():
            raise ValueError('New date must be in the future')
        return v

class AppointmentReport(BaseModel):
    """Schema for appointment reports"""
    report_type: str = Field(..., regex="^(daily|weekly|monthly|provider|patient)$")
    date_from: date
    date_to: date
    provider_ids: Optional[List[int]] = None
    patient_ids: Optional[List[int]] = None
    include_cancelled: Optional[bool] = False
    include_no_shows: Optional[bool] = True
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        if 'date_from' in values and v < values['date_from']:
            raise ValueError('End date must be after start date')
        return v