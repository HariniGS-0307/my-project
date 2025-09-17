"""
Notification-related Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.notification import (
    NotificationType, NotificationStatus, NotificationPriority, NotificationChannel
)

class NotificationBase(BaseModel):
    """Base notification schema with common fields"""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=2000)
    notification_type: NotificationType
    priority: Optional[NotificationPriority] = NotificationPriority.MEDIUM
    channel: Optional[NotificationChannel] = NotificationChannel.IN_APP
    
    @validator('title')
    def validate_title(cls, v):
        return v.strip()
    
    @validator('message')
    def validate_message(cls, v):
        return v.strip()

class NotificationCreate(NotificationBase):
    """Schema for notification creation"""
    user_id: int
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    patient_id: Optional[int] = None
    appointment_id: Optional[int] = None
    medication_id: Optional[int] = None
    health_record_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = Field(None, max_length=500)
    action_text: Optional[str] = Field(None, max_length=100)
    group_id: Optional[str] = Field(None, max_length=100)
    thread_id: Optional[str] = Field(None, max_length=100)
    parent_notification_id: Optional[int] = None
    
    @validator('scheduled_for')
    def validate_scheduled_for(cls, v):
        if v is not None and v <= datetime.now():
            raise ValueError('Scheduled time must be in the future')
        return v
    
    @validator('expires_at')
    def validate_expires_at(cls, v, values):
        if v is not None:
            now = datetime.now()
            if v <= now:
                raise ValueError('Expiration time must be in the future')
            
            scheduled_for = values.get('scheduled_for')
            if scheduled_for and v <= scheduled_for:
                raise ValueError('Expiration time must be after scheduled time')
        return v
    
    @validator('action_url')
    def validate_action_url(cls, v):
        if v is not None:
            import re
            # Basic URL validation
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$|^/[^\s]*$'
            if not re.match(url_pattern, v):
                raise ValueError('Invalid URL format')
        return v

class NotificationUpdate(BaseModel):
    """Schema for notification updates"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    message: Optional[str] = Field(None, min_length=1, max_length=2000)
    notification_type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    channel: Optional[NotificationChannel] = None
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    action_url: Optional[str] = Field(None, max_length=500)
    action_text: Optional[str] = Field(None, max_length=100)
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_starred: Optional[bool] = None
    
    @validator('title', 'message')
    def validate_strings(cls, v):
        return v.strip() if v else v
    
    @validator('scheduled_for')
    def validate_scheduled_for(cls, v):
        if v is not None and v <= datetime.now():
            raise ValueError('Scheduled time must be in the future')
        return v

class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: int
    user_id: int
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority
    channel: NotificationChannel
    status: NotificationStatus
    scheduled_for: Optional[datetime]
    expires_at: Optional[datetime]
    patient_id: Optional[int]
    appointment_id: Optional[int]
    medication_id: Optional[int]
    health_record_id: Optional[int]
    metadata: Optional[Dict[str, Any]]
    action_url: Optional[str]
    action_text: Optional[str]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    failed_at: Optional[datetime]
    failure_reason: Optional[str]
    retry_count: int
    max_retries: int
    next_retry_at: Optional[datetime]
    group_id: Optional[str]
    thread_id: Optional[str]
    parent_notification_id: Optional[int]
    is_read: bool
    is_archived: bool
    is_starred: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed fields
    is_pending: bool = False
    is_sent: bool = False
    is_overdue: bool = False
    is_expired: bool = False
    can_retry: bool = False
    display_time: Optional[str] = None
    
    # Related information
    user_name: Optional[str] = None
    patient_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    """Schema for paginated notification list response"""
    notifications: List[NotificationResponse]
    total: int
    page: int
    per_page: int
    pages: int
    unread_count: int

class NotificationMarkRead(BaseModel):
    """Schema for marking notifications as read"""
    notification_ids: List[int] = Field(..., min_items=1, max_items=100)
    mark_as_read: bool = True

class NotificationBulkAction(BaseModel):
    """Schema for bulk notification actions"""
    notification_ids: List[int] = Field(..., min_items=1, max_items=100)
    action: str = Field(..., regex="^(mark_read|mark_unread|archive|unarchive|star|unstar|delete)$")

class NotificationSearchFilters(BaseModel):
    """Schema for notification search filters"""
    search: Optional[str] = None
    notification_type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    channel: Optional[NotificationChannel] = None
    status: Optional[NotificationStatus] = None
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None
    is_starred: Optional[bool] = None
    patient_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    group_id: Optional[str] = None
    thread_id: Optional[str] = None
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        if v is not None and 'date_from' in values and values['date_from'] is not None:
            if v <= values['date_from']:
                raise ValueError('End date must be after start date')
        return v

class NotificationStats(BaseModel):
    """Schema for notification statistics"""
    total_notifications: int
    unread_notifications: int
    pending_notifications: int
    failed_notifications: int
    notifications_by_type: Dict[str, int]
    notifications_by_priority: Dict[str, int]
    notifications_by_channel: Dict[str, int]
    notifications_by_status: Dict[str, int]
    delivery_rate: float
    average_delivery_time: Optional[float]  # in seconds

class NotificationTemplate(BaseModel):
    """Schema for notification templates"""
    name: str = Field(..., min_length=1, max_length=100)
    notification_type: NotificationType
    title_template: str = Field(..., min_length=1, max_length=200)
    message_template: str = Field(..., min_length=1, max_length=2000)
    priority: Optional[NotificationPriority] = NotificationPriority.MEDIUM
    channel: Optional[NotificationChannel] = NotificationChannel.IN_APP
    variables: Optional[List[str]] = []  # Template variables like {patient_name}
    is_active: Optional[bool] = True
    
    @validator('variables')
    def validate_variables(cls, v):
        if v:
            import re
            for var in v:
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var):
                    raise ValueError(f'Invalid variable name: {var}')
        return v

class NotificationPreferences(BaseModel):
    """Schema for user notification preferences"""
    user_id: int
    email_notifications: Optional[bool] = True
    sms_notifications: Optional[bool] = False
    push_notifications: Optional[bool] = True
    in_app_notifications: Optional[bool] = True
    medication_reminders: Optional[bool] = True
    appointment_reminders: Optional[bool] = True
    health_alerts: Optional[bool] = True
    system_alerts: Optional[bool] = True
    delivery_updates: Optional[bool] = True
    quiet_hours_start: Optional[str] = Field(None, regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    quiet_hours_end: Optional[str] = Field(None, regex=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    timezone: Optional[str] = Field(None, max_length=50)
    
    @validator('quiet_hours_end')
    def validate_quiet_hours(cls, v, values):
        if v is not None and 'quiet_hours_start' in values and values['quiet_hours_start'] is not None:
            # Convert to minutes for comparison
            start_parts = values['quiet_hours_start'].split(':')
            end_parts = v.split(':')
            start_minutes = int(start_parts[0]) * 60 + int(start_parts[1])
            end_minutes = int(end_parts[0]) * 60 + int(end_parts[1])
            
            # Allow overnight quiet hours (e.g., 22:00 to 06:00)
            if start_minutes == end_minutes:
                raise ValueError('Quiet hours start and end cannot be the same')
        return v

class NotificationSchedule(BaseModel):
    """Schema for scheduling notifications"""
    notification_template_id: Optional[int] = None
    user_id: int
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=2000)
    notification_type: NotificationType
    priority: Optional[NotificationPriority] = NotificationPriority.MEDIUM
    channel: Optional[NotificationChannel] = NotificationChannel.IN_APP
    schedule_type: str = Field(..., regex="^(immediate|delayed|recurring)$")
    scheduled_for: Optional[datetime] = None
    recurrence_pattern: Optional[str] = Field(None, regex="^(daily|weekly|monthly|custom)$")
    recurrence_data: Optional[Dict[str, Any]] = None  # Cron expression, days of week, etc.
    expires_at: Optional[datetime] = None
    max_occurrences: Optional[int] = Field(None, ge=1, le=1000)
    
    @validator('scheduled_for')
    def validate_scheduled_for(cls, v, values):
        schedule_type = values.get('schedule_type')
        if schedule_type in ['delayed', 'recurring'] and not v:
            raise ValueError('Scheduled time is required for delayed and recurring notifications')
        if v is not None and v <= datetime.now():
            raise ValueError('Scheduled time must be in the future')
        return v
    
    @validator('recurrence_pattern')
    def validate_recurrence(cls, v, values):
        schedule_type = values.get('schedule_type')
        if schedule_type == 'recurring' and not v:
            raise ValueError('Recurrence pattern is required for recurring notifications')
        return v

class NotificationDeliveryStatus(BaseModel):
    """Schema for notification delivery status"""
    notification_id: int
    channel: NotificationChannel
    status: NotificationStatus
    delivered_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    retry_count: int = 0
    next_retry_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class NotificationThread(BaseModel):
    """Schema for notification thread"""
    thread_id: str
    subject: str
    participant_ids: List[int]
    notifications: List[NotificationResponse]
    created_at: datetime
    last_activity: datetime
    is_active: bool

class NotificationGroup(BaseModel):
    """Schema for notification group"""
    group_id: str
    group_type: str = Field(..., regex="^(patient_alerts|appointment_series|medication_course|system_maintenance)$")
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    notifications: List[NotificationResponse]
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

class NotificationAnalytics(BaseModel):
    """Schema for notification analytics"""
    period_start: datetime
    period_end: datetime
    total_sent: int
    total_delivered: int
    total_read: int
    total_failed: int
    delivery_rate: float
    read_rate: float
    failure_rate: float
    average_delivery_time: Optional[float]  # in seconds
    average_read_time: Optional[float]  # in seconds
    channel_performance: Dict[str, Dict[str, Any]]
    type_performance: Dict[str, Dict[str, Any]]
    peak_hours: List[int]  # Hours of day with most activity

class NotificationWebhook(BaseModel):
    """Schema for notification webhooks"""
    url: str = Field(..., max_length=500)
    events: List[str] = Field(..., min_items=1)  # sent, delivered, read, failed
    secret: Optional[str] = Field(None, min_length=10, max_length=100)
    is_active: Optional[bool] = True
    retry_on_failure: Optional[bool] = True
    max_retries: Optional[int] = Field(3, ge=0, le=10)
    
    @validator('url')
    def validate_webhook_url(cls, v):
        import re
        if not re.match(r'^https://[^\s/$.?#].[^\s]*$', v):
            raise ValueError('Webhook URL must be HTTPS')
        return v
    
    @validator('events')
    def validate_events(cls, v):
        valid_events = ['sent', 'delivered', 'read', 'failed', 'cancelled']
        for event in v:
            if event not in valid_events:
                raise ValueError(f'Invalid event: {event}. Valid events: {", ".join(valid_events)}')
        return v