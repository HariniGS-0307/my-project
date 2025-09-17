"""
Authentication schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

from app.models.user import UserRole, UserStatus

class UserCreate(BaseModel):
    """Schema for user registration"""
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    role: Optional[UserRole] = UserRole.PATIENT
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if len(v) < 1:
            raise ValueError('Name cannot be empty')
        if len(v) > 50:
            raise ValueError('Name must be less than 50 characters')
        return v

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str  # Can be username or email
    password: str

class UserResponse(BaseModel):
    """Schema for user response data"""
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
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    """Schema for token payload data"""
    username: Optional[str] = None
    user_id: Optional[int] = None

class PasswordChange(BaseModel):
    """Schema for password change request"""
    old_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v