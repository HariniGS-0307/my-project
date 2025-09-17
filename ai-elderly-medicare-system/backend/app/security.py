"""
Security utilities for authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

class PermissionChecker:
    """Class for checking user permissions"""
    
    @staticmethod
    def can_access_patient_data(user_role: str, user_id: int, patient_user_id: int) -> bool:
        """Check if user can access patient data"""
        if user_role == "admin":
            return True
        elif user_role in ["doctor", "nurse"]:
            return True  # Healthcare providers can access all patients
        elif user_role == "patient":
            return user_id == patient_user_id  # Patients can only access their own data
        elif user_role == "caregiver":
            # In a real system, you'd check if caregiver is assigned to this patient
            return True
        return False
    
    @staticmethod
    def can_modify_patient_data(user_role: str) -> bool:
        """Check if user can modify patient data"""
        return user_role in ["admin", "doctor", "nurse"]
    
    @staticmethod
    def can_schedule_appointments(user_role: str) -> bool:
        """Check if user can schedule appointments"""
        return user_role in ["admin", "doctor", "nurse", "caregiver"]
    
    @staticmethod
    def can_access_all_patients(user_role: str) -> bool:
        """Check if user can access all patient records"""
        return user_role in ["admin", "doctor", "nurse"]
    
    @staticmethod
    def can_manage_users(user_role: str) -> bool:
        """Check if user can manage other users"""
        return user_role == "admin"
    
    @staticmethod
    def can_view_reports(user_role: str) -> bool:
        """Check if user can view system reports"""
        return user_role in ["admin", "doctor"]

def require_roles(allowed_roles: list):
    """Decorator to require specific roles for endpoint access"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be implemented with the actual user context
            # For now, it's a placeholder
            return func(*args, **kwargs)
        return wrapper
    return decorator

def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data like SSN, medical record numbers"""
    return pwd_context.hash(data)

def verify_sensitive_data(plain_data: str, hashed_data: str) -> bool:
    """Verify sensitive data against its hash"""
    return pwd_context.verify(plain_data, hashed_data)

def generate_patient_id() -> str:
    """Generate unique patient ID"""
    import uuid
    return f"PAT-{uuid.uuid4().hex[:8].upper()}"

def generate_appointment_id() -> str:
    """Generate unique appointment ID"""
    import uuid
    return f"APT-{uuid.uuid4().hex[:8].upper()}"

def sanitize_input(input_string: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", "&", "\"", "'", "/", "\\"]
    sanitized = input_string
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    
    return sanitized.strip()

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    import re
    # Simple US phone number validation
    pattern = r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'
    return re.match(pattern, phone) is not None