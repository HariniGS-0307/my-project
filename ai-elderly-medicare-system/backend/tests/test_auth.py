"""
Authentication API tests
"""

import pytest
from fastapi import status
from datetime import datetime, timedelta

from app.models.user import User, UserRole, UserStatus
from app.security import verify_password, verify_token
from tests.conftest import TestDataGenerator, assert_user_response


class TestUserRegistration:
    """Test user registration endpoints"""
    
    def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert data["first_name"] == sample_user_data["first_name"]
        assert data["last_name"] == sample_user_data["last_name"]
        assert data["role"] == sample_user_data["role"]
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data
    
    def test_register_user_duplicate_email(self, client, sample_user_data, patient_user):
        """Test registration with duplicate email"""
        sample_user_data["email"] = patient_user.email
        
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]
    
    def test_register_user_duplicate_username(self, client, sample_user_data, patient_user):
        """Test registration with duplicate username"""
        sample_user_data["username"] = patient_user.username
        
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already taken" in response.json()["detail"]
    
    def test_register_user_invalid_email(self, client, sample_user_data):
        """Test registration with invalid email"""
        sample_user_data["email"] = "invalid-email"
        
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_user_weak_password(self, client, sample_user_data):
        """Test registration with weak password"""
        sample_user_data["password"] = "weak"
        
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_user_missing_fields(self, client):
        """Test registration with missing required fields"""
        incomplete_data = {
            "username": "testuser",
            "email": "test@example.com"
            # Missing password, first_name, last_name
        }
        
        response = client.post("/api/v1/auth/register", json=incomplete_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Test user login endpoints"""
    
    def test_login_success(self, client, patient_user):
        """Test successful login"""
        login_data = {
            "username": patient_user.username,
            "password": "patient123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        
        user_data = data["user"]
        assert_user_response(user_data, patient_user)
    
    def test_login_with_email(self, client, patient_user):
        """Test login with email instead of username"""
        login_data = {
            "username": patient_user.email,
            "password": "patient123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
    
    def test_login_invalid_credentials(self, client, patient_user):
        """Test login with invalid credentials"""
        login_data = {
            "username": patient_user.username,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        login_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_inactive_user(self, client, db_session):
        """Test login with inactive user"""
        # Create inactive user
        inactive_user = User(
            username="inactive_user",
            email="inactive@test.com",
            hashed_password="hashed_password",
            first_name="Inactive",
            last_name="User",
            role=UserRole.PATIENT,
            status=UserStatus.INACTIVE,
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()
        
        login_data = {
            "username": "inactive_user",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "not active" in response.json()["detail"]
    
    def test_login_remember_me(self, client, patient_user):
        """Test login with remember me option"""
        login_data = {
            "username": patient_user.username,
            "password": "patient123",
            "remember_me": True
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should have longer expiration time
        assert data["expires_in"] > 3600  # More than 1 hour


class TestTokenOperations:
    """Test token-related operations"""
    
    def test_get_current_user(self, client, patient_user, auth_headers_patient):
        """Test getting current user information"""
        response = client.get("/api/v1/auth/me", headers=auth_headers_patient)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert_user_response(data, patient_user)
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_refresh_token(self, client, patient_user, auth_headers_patient):
        """Test token refresh"""
        response = client.post("/api/v1/auth/refresh", headers=auth_headers_patient)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
    
    def test_verify_token_valid(self, client, auth_headers_patient):
        """Test token verification with valid token"""
        response = client.get("/api/v1/auth/verify-token", headers=auth_headers_patient)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["valid"] is True
        assert "user_id" in data
    
    def test_verify_token_invalid(self, client):
        """Test token verification with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = client.get("/api/v1/auth/verify-token", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["valid"] is False


class TestPasswordOperations:
    """Test password-related operations"""
    
    def test_change_password_success(self, client, patient_user, auth_headers_patient, db_session):
        """Test successful password change"""
        password_data = {
            "current_password": "patient123",
            "new_password": "NewPass123!"
        }
        
        response = client.post("/api/v1/auth/change-password", 
                             json=password_data, 
                             headers=auth_headers_patient)
        
        assert response.status_code == status.HTTP_200_OK
        assert "successfully" in response.json()["message"]
        
        # Verify password was actually changed
        db_session.refresh(patient_user)
        assert verify_password("NewPass123!", patient_user.hashed_password)
    
    def test_change_password_wrong_current(self, client, auth_headers_patient):
        """Test password change with wrong current password"""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "NewPass123!"
        }
        
        response = client.post("/api/v1/auth/change-password", 
                             json=password_data, 
                             headers=auth_headers_patient)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Incorrect current password" in response.json()["detail"]
    
    def test_change_password_weak_new(self, client, auth_headers_patient):
        """Test password change with weak new password"""
        password_data = {
            "current_password": "patient123",
            "new_password": "weak"
        }
        
        response = client.post("/api/v1/auth/change-password", 
                             json=password_data, 
                             headers=auth_headers_patient)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_forgot_password(self, client, patient_user):
        """Test forgot password request"""
        reset_data = {"email": patient_user.email}
        
        response = client.post("/api/v1/auth/forgot-password", json=reset_data)
        
        assert response.status_code == status.HTTP_200_OK
        assert "reset link has been sent" in response.json()["message"]
    
    def test_forgot_password_nonexistent_email(self, client):
        """Test forgot password with nonexistent email"""
        reset_data = {"email": "nonexistent@example.com"}
        
        response = client.post("/api/v1/auth/forgot-password", json=reset_data)
        
        # Should still return success to prevent email enumeration
        assert response.status_code == status.HTTP_200_OK
        assert "reset link has been sent" in response.json()["message"]
    
    def test_reset_password_invalid_token(self, client):
        """Test password reset with invalid token"""
        reset_data = {
            "token": "invalid_token",
            "new_password": "NewPass123!"
        }
        
        response = client.post("/api/v1/auth/reset-password", json=reset_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired" in response.json()["detail"]


class TestEmailVerification:
    """Test email verification operations"""
    
    def test_verify_email_invalid_token(self, client):
        """Test email verification with invalid token"""
        response = client.post("/api/v1/auth/verify-email?token=invalid_token")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired" in response.json()["detail"]


class TestLogout:
    """Test logout operations"""
    
    def test_logout_success(self, client, auth_headers_patient):
        """Test successful logout"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers_patient)
        
        assert response.status_code == status.HTTP_200_OK
        assert "logged out" in response.json()["message"]
    
    def test_logout_no_token(self, client):
        """Test logout without token"""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAuthenticationIntegration:
    """Integration tests for authentication flow"""
    
    def test_full_registration_login_flow(self, client, db_session):
        """Test complete registration and login flow"""
        # Register user
        user_data = TestDataGenerator.user_data()
        
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Activate user (normally done via email verification)
        user = db_session.query(User).filter(User.username == user_data["username"]).first()
        user.status = UserStatus.ACTIVE
        db_session.commit()
        
        # Login
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Access protected endpoint
        me_response = client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK
        
        user_info = me_response.json()
        assert user_info["username"] == user_data["username"]
    
    def test_token_expiration_handling(self, client, patient_user):
        """Test handling of expired tokens"""
        # Create expired token
        expired_token = create_access_token(
            data={"sub": str(patient_user.id), "username": patient_user.username},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_role_based_access(self, client, admin_user, patient_user):
        """Test role-based access control"""
        # Test admin access
        admin_token = create_access_token(
            data={"sub": str(admin_user.id), "username": admin_user.username}
        )
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        admin_response = client.get("/api/v1/auth/me", headers=admin_headers)
        assert admin_response.status_code == status.HTTP_200_OK
        assert admin_response.json()["role"] == "admin"
        
        # Test patient access
        patient_token = create_access_token(
            data={"sub": str(patient_user.id), "username": patient_user.username}
        )
        patient_headers = {"Authorization": f"Bearer {patient_token}"}
        
        patient_response = client.get("/api/v1/auth/me", headers=patient_headers)
        assert patient_response.status_code == status.HTTP_200_OK
        assert patient_response.json()["role"] == "patient"


class TestAuthenticationSecurity:
    """Test authentication security features"""
    
    def test_password_hashing(self, db_session):
        """Test that passwords are properly hashed"""
        from app.security import get_password_hash
        
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        
        # Hash should be verifiable
        assert verify_password(password, hashed)
        
        # Wrong password should not verify
        assert not verify_password("WrongPassword", hashed)
    
    def test_token_structure(self, patient_token):
        """Test JWT token structure"""
        payload = verify_token(patient_token)
        
        assert "sub" in payload
        assert "username" in payload
        assert "exp" in payload
    
    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection in login"""
        malicious_data = {
            "username": "admin'; DROP TABLE users; --",
            "password": "password"
        }
        
        response = client.post("/api/v1/auth/login", json=malicious_data)
        
        # Should return unauthorized, not cause database error
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_xss_protection(self, client, sample_user_data):
        """Test protection against XSS in registration"""
        sample_user_data["first_name"] = "<script>alert('xss')</script>"
        
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Should either sanitize or reject
        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            assert "<script>" not in data["first_name"]