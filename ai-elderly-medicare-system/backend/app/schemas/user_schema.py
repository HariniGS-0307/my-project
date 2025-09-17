"""
User-related Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.models.user import UserRole, UserStatus

class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v.lower()
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if v is not None:
            # Remove all non-digit characters
            digits_only = ''.join(filter(str.isdigit, v))
            if len(digits_only) < 10 or len(digits_only) > 15:
                raise ValueError('Phone number must be between 10-15 digits')
        return v

class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(..., min_length=8)
    role: Optional[UserRole] = UserRole.PATIENT
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserUpdate(BaseModel):
    """Schema for user updates"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = Field(None, max_length=500)
    preferences: Optional[str] = None
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if v is not None:
            digits_only = ''.join(filter(str.isdigit, v))
            if len(digits_only) < 10 or len(digits_only) > 15:
                raise ValueError('Phone number must be between 10-15 digits')
        return v

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=1)
    remember_me: Optional[bool] = False

class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    phone_number: Optional[str]
    role: UserRole
    status: UserStatus
    is_active: bool
    is_verified: bool
    license_number: Optional[str]
    specialization: Optional[str]
    department: Optional[str]
    profile_picture: Optional[str]
    bio: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    """Schema for paginated user list response"""
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
    pages: int

class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

class TokenResponse(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class UserProfileUpdate(BaseModel):
    """Schema for user profile updates"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = Field(None, max_length=500)
    specialization: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if v is not None:
            digits_only = ''.join(filter(str.isdigit, v))
            if len(digits_only) < 10 or len(digits_only) > 15:
                raise ValueError('Phone number must be between 10-15 digits')
        return v

class UserStatusUpdate(BaseModel):
    """Schema for updating user status (admin only)"""
    status: UserStatus
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class UserRoleUpdate(BaseModel):
    """Schema for updating user role (admin only)"""
    role: UserRole
    license_number: Optional[str] = None
    specialization: Optional[str] = None
    department: Optional[str] = None

class UserStats(BaseModel):
    """Schema for user statistics"""
    total_users: int
    active_users: int
    pending_users: int
    users_by_role: dict
    recent_registrations: int

class UserSearchFilters(BaseModel):
    """Schema for user search filters"""
    search: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    department: Optional[str] = None
    specialization: Optional[str] = None

class EmailVerification(BaseModel):
    """Schema for email verification"""
    token: str = Field(..., min_length=10)

class ResendVerification(BaseModel):
    """Schema for resending verification email"""
    email: EmailStr

class UserPreferences(BaseModel):
    """Schema for user preferences"""
    theme: Optional[str] = Field(None, regex="^(light|dark|auto)$")
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    email_notifications: Optional[bool] = True
    sms_notifications: Optional[bool] = False
    push_notifications: Optional[bool] = True
    appointment_reminders: Optional[bool] = True
    medication_reminders: Optional[bool] = True
    health_alerts: Optional[bool] = True

class UserActivity(BaseModel):
    """Schema for user activity tracking"""
    user_id: int
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

class UserSession(BaseModel):
    """Schema for user session information"""
    session_id: str
    user_id: int
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    is_active: bool
    
    class Config:
        from_attributes = True