"""
Authentication service for user management and security operations
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import secrets
import logging

from app.models.user import User, UserRole, UserStatus
from app.security import get_password_hash, verify_password, create_access_token
from app.utils.exceptions import AuthenticationError, ValidationError
from app.utils.validators import validate_email, validate_password

logger = logging.getLogger(__name__)

class AuthService:
    """Service class for authentication operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, username: str, email: str, password: str, 
                   first_name: str, last_name: str, phone_number: Optional[str] = None,
                   role: UserRole = UserRole.PATIENT) -> User:
        """Create a new user account"""
        try:
            # Validate input
            if not validate_email(email):
                raise ValidationError("Invalid email format")
            
            if not validate_password(password):
                raise ValidationError("Password does not meet requirements")
            
            # Check if user already exists
            if self.get_user_by_email(email):
                raise ValidationError("Email already registered")
            
            if self.get_user_by_username(username):
                raise ValidationError("Username already taken")
            
            # Create user
            hashed_password = get_password_hash(password)
            
            user = User(
                username=username.lower().strip(),
                email=email.lower().strip(),
                hashed_password=hashed_password,
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                phone_number=phone_number.strip() if phone_number else None,
                role=role,
                status=UserStatus.PENDING
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User created successfully: {username}")
            return user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        try:
            # Find user by username or email
            user = self.get_user_by_username(username) or self.get_user_by_email(username)
            
            if not user:
                logger.warning(f"Authentication failed: User not found - {username}")
                return None
            
            # Verify password
            if not verify_password(password, user.hashed_password):
                logger.warning(f"Authentication failed: Invalid password - {username}")
                return None
            
            # Check if user is active
            if not user.is_active or user.status != UserStatus.ACTIVE:
                logger.warning(f"Authentication failed: User not active - {username}")
                raise AuthenticationError("Account is not active")
            
            logger.info(f"User authenticated successfully: {username}")
            return user
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            return self.db.query(User).filter(User.username == username.lower()).first()
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return self.db.query(User).filter(User.email == email.lower()).first()
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                user.last_login = datetime.utcnow()
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            self.db.rollback()
            return False
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password"""
        try:
            if not validate_password(new_password):
                raise ValidationError("Password does not meet requirements")
            
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValidationError("User not found")
            
            user.hashed_password = get_password_hash(new_password)
            self.db.commit()
            
            logger.info(f"Password changed for user: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            self.db.rollback()
            raise
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        """Reset user password (admin function)"""
        try:
            if not validate_password(new_password):
                raise ValidationError("Password does not meet requirements")
            
            user = self.get_user_by_id(user_id)
            if not user:
                raise ValidationError("User not found")
            
            user.hashed_password = get_password_hash(new_password)
            self.db.commit()
            
            logger.info(f"Password reset for user: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting password: {e}")
            self.db.rollback()
            raise
    
    def activate_user(self, user_id: int) -> bool:
        """Activate user account"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.status = UserStatus.ACTIVE
            user.is_active = True
            self.db.commit()
            
            logger.info(f"User activated: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error activating user: {e}")
            self.db.rollback()
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.status = UserStatus.INACTIVE
            user.is_active = False
            self.db.commit()
            
            logger.info(f"User deactivated: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            self.db.rollback()
            return False
    
    def verify_user_email(self, user_id: int) -> bool:
        """Mark user email as verified"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            user.is_verified = True
            if user.status == UserStatus.PENDING:
                user.status = UserStatus.ACTIVE
            
            self.db.commit()
            
            logger.info(f"Email verified for user: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            self.db.rollback()
            return False
    
    def generate_verification_token(self, user_id: int) -> str:
        """Generate email verification token"""
        try:
            # In production, store this token in database with expiration
            token = secrets.token_urlsafe(32)
            
            # For now, we'll use a simple token format
            # In production, use JWT or store in database
            verification_token = f"verify_{user_id}_{token}"
            
            logger.info(f"Verification token generated for user ID: {user_id}")
            return verification_token
            
        except Exception as e:
            logger.error(f"Error generating verification token: {e}")
            raise
    
    def verify_email_token(self, token: str) -> Optional[int]:
        """Verify email verification token"""
        try:
            # Simple token verification (in production, use proper JWT or database lookup)
            if token.startswith("verify_"):
                parts = token.split("_")
                if len(parts) >= 3:
                    user_id = int(parts[1])
                    # In production, verify token expiration and validity
                    return user_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error verifying email token: {e}")
            return None
    
    def generate_password_reset_token(self, user_id: int) -> str:
        """Generate password reset token"""
        try:
            # In production, store this token in database with expiration
            token = secrets.token_urlsafe(32)
            
            # For now, we'll use a simple token format
            reset_token = f"reset_{user_id}_{token}"
            
            logger.info(f"Password reset token generated for user ID: {user_id}")
            return reset_token
            
        except Exception as e:
            logger.error(f"Error generating reset token: {e}")
            raise
    
    def verify_password_reset_token(self, token: str) -> Optional[int]:
        """Verify password reset token"""
        try:
            # Simple token verification (in production, use proper JWT or database lookup)
            if token.startswith("reset_"):
                parts = token.split("_")
                if len(parts) >= 3:
                    user_id = int(parts[1])
                    # In production, verify token expiration and validity
                    return user_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error verifying reset token: {e}")
            return None
    
    def update_user_profile(self, user_id: int, **kwargs) -> bool:
        """Update user profile information"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            # Allowed fields for update
            allowed_fields = [
                'first_name', 'last_name', 'phone_number', 
                'bio', 'preferences', 'profile_picture'
            ]
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Profile updated for user: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            self.db.rollback()
            return False
    
    def get_users_by_role(self, role: UserRole, active_only: bool = True) -> list[User]:
        """Get users by role"""
        try:
            query = self.db.query(User).filter(User.role == role)
            
            if active_only:
                query = query.filter(User.is_active == True, User.status == UserStatus.ACTIVE)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting users by role: {e}")
            return []
    
    def get_user_statistics(self) -> dict:
        """Get user statistics"""
        try:
            stats = {}
            
            # Total users
            stats['total_users'] = self.db.query(User).count()
            
            # Active users
            stats['active_users'] = self.db.query(User).filter(
                User.is_active == True,
                User.status == UserStatus.ACTIVE
            ).count()
            
            # Users by role
            for role in UserRole:
                stats[f'{role.value}_count'] = self.db.query(User).filter(User.role == role).count()
            
            # Recent registrations (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            stats['recent_registrations'] = self.db.query(User).filter(
                User.created_at >= thirty_days_ago
            ).count()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {}
    
    def check_user_permissions(self, user_id: int, required_role: UserRole) -> bool:
        """Check if user has required role or higher"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False
            
            # Role hierarchy (higher roles can access lower role functions)
            role_hierarchy = {
                UserRole.ADMIN: 5,
                UserRole.DOCTOR: 4,
                UserRole.NURSE: 3,
                UserRole.CAREGIVER: 2,
                UserRole.FAMILY_MEMBER: 1,
                UserRole.PATIENT: 1
            }
            
            user_level = role_hierarchy.get(user.role, 0)
            required_level = role_hierarchy.get(required_role, 0)
            
            return user_level >= required_level
            
        except Exception as e:
            logger.error(f"Error checking user permissions: {e}")
            return False