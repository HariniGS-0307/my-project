"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.security import create_access_token, verify_password, get_password_hash, verify_token
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.utils.validators import validate_email, validate_password
from app.utils.exceptions import AuthenticationError, ValidationError

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Pydantic models for request/response
from pydantic import BaseModel, EmailStr, validator

class UserRegister(BaseModel):
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
        return v
    
    @validator('password')
    def validate_password_strength(cls, v):
        if not validate_password(v):
            raise ValueError('Password must be at least 8 characters with uppercase, lowercase, and number')
        return v

class UserLogin(BaseModel):
    username: str
    password: str
    remember_me: Optional[bool] = False

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not validate_password(v):
            raise ValueError('Password must be at least 8 characters with uppercase, lowercase, and number')
        return v

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not validate_password(v):
            raise ValueError('Password must be at least 8 characters with uppercase, lowercase, and number')
        return v

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        auth_service = AuthService(db)
        
        # Check if user already exists
        if auth_service.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        if auth_service.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user
        user = auth_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone_number=user_data.phone_number,
            role=user_data.role
        )
        
        # Send verification email
        email_service = EmailService()
        background_tasks.add_task(
            email_service.send_verification_email,
            user.email,
            user.first_name,
            auth_service.generate_verification_token(user.id)
        )
        
        logger.info(f"User registered successfully: {user.username}")
        return UserResponse.from_orm(user)
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

@router.post("/login", response_model=TokenResponse)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    try:
        auth_service = AuthService(db)
        
        # Authenticate user
        user = auth_service.authenticate_user(user_credentials.username, user_credentials.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active or user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active",
            )
        
        # Update last login
        auth_service.update_last_login(user.id)
        
        # Create access token
        expires_delta = timedelta(days=7) if user_credentials.remember_me else timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=expires_delta
        )
        
        logger.info(f"User logged in successfully: {user.username}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(expires_delta.total_seconds()),
            user=UserResponse.from_orm(user)
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user information"""
    try:
        # Verify token and get user
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(int(user_id))
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        return UserResponse.from_orm(user)
        
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    try:
        # Verify current token
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(int(user_id))
        
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        
        # Create new access token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=1800,  # 30 minutes
            user=UserResponse.from_orm(user)
        )
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not refresh token")

@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        # Get current user
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(int(user_id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password",
            )
        
        # Update password
        auth_service.change_password(user.id, password_data.new_password)
        
        logger.info(f"Password changed for user: {user.username}")
        return {"message": "Password changed successfully"}
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password change failed")

@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    try:
        auth_service = AuthService(db)
        user = auth_service.get_user_by_email(request.email)
        
        if user:
            # Generate reset token
            reset_token = auth_service.generate_password_reset_token(user.id)
            
            # Send reset email
            email_service = EmailService()
            background_tasks.add_task(
                email_service.send_password_reset_email,
                user.email,
                user.first_name,
                reset_token
            )
            
            logger.info(f"Password reset requested for: {request.email}")
        
        # Always return success to prevent email enumeration
        return {"message": "If the email exists, a reset link has been sent"}
        
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        return {"message": "If the email exists, a reset link has been sent"}

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Confirm password reset"""
    try:
        auth_service = AuthService(db)
        
        # Verify reset token and get user
        user_id = auth_service.verify_password_reset_token(reset_data.token)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Reset password
        auth_service.reset_password(user_id, reset_data.new_password)
        
        logger.info(f"Password reset completed for user ID: {user_id}")
        return {"message": "Password reset successfully"}
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password reset failed")

@router.post("/verify-email")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify user email address"""
    try:
        auth_service = AuthService(db)
        
        # Verify email token
        user_id = auth_service.verify_email_token(token)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Mark email as verified
        auth_service.verify_user_email(user_id)
        
        logger.info(f"Email verified for user ID: {user_id}")
        return {"message": "Email verified successfully"}
        
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email verification failed")

@router.post("/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Logout user (client should discard token)"""
    try:
        # In a production system, you might want to blacklist the token
        # For now, we'll just return a success message
        logger.info("User logged out")
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"message": "Logout completed"}

@router.get("/verify-token")
async def verify_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify if token is valid"""
    try:
        payload = verify_token(credentials.credentials)
        return {
            "valid": True, 
            "user_id": payload.get("sub"),
            "expires": payload.get("exp")
        }
    except Exception:
        return {"valid": False}