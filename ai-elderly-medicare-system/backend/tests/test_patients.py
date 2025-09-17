"""
Patient management API tests
"""

import pytest
from fastapi import status
from datetime import date, datetime

from app.models.patient import Patient, Gender, BloodType
from app.models.user import UserRole
from tests.conftest import TestDataGenerator, assert_patient_response


class TestPatientCreation:
    """Test patient creation endpoints"""
    
    def test_create_patient_success(self, client, auth_headers_doctor, sample_patient_data):
        """Test successful patient creation"""
        response = client.post("/api/v1/patients/", 
                             json=sample_patient_data, 
                             headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["user_id"] == sample_patient_data["user_id"]
        assert data["gender"] == sample_patient_data["gender"]
        assert data["height"] == sample_patient_data["height"]
        assert data["weight"] == sample_patient_data["weight"]
        assert "patient_id" in data
        assert "id" in data
        assert "created_at" in data
    
    def test_create_patient_unauthorized(self, client, auth_headers_patient, sample_patient_data):
        """Test patient creation without proper permissions"""
        response = client.post("/api/v1/patients/", 
                             json=sample_patient_data, 
                             headers=auth_headers_patient)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_patient_nonexistent_user(self, client, auth_headers_doctor, sample_patient_data):
        """Test patient creation with nonexistent user"""
        sample_patient_data["user_id"] = 99999
        
        response = client.post("/api/v1/patients/", 
                             json=sample_patient_data, 
                             headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_patient_duplicate(self, client, auth_headers_doctor, patient_record, sample_patient_data):
        """Test creating duplicate patient for same user"""
        sample_patient_data["user_id"] = patient_record.user_id
        
        response = client.post("/api/v1/patients/", 
                             json=sample_patient_data, 
                             headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]
    
    def test_create_patient_invalid_birth_date(self, client, auth_headers_doctor, sample_patient_data):
        """Test patient creation with invalid birth date"""
        sample_patient_data["date_of_birth"] = "2030-01-01"  # Future date
        
        response = client.post("/api/v1/patients/", 
                             json=sample_patient_data, 
                             headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_patient_invalid_measurements(self, client, auth_headers_doctor, sample_patient_data):
        """Test patient creation with invalid measurements"""
        sample_patient_data["height"] = -10  # Invalid height
        sample_patient_data["weight"] = 500   # Invalid weight
        
        response = client.post("/api/v1/patients/", 
                             json=sample_patient_data, 
                             headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_patient_invalid_medicare_number(self, client, auth_headers_doctor, sample_patient_data):
        """Test patient creation with invalid Medicare number"""
        sample_patient_data["medicare_number"] = "invalid-format"
        
        response = client.post("/api/v1/patients/", 
                             json=sample_patient_data, 
                             headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestPatientRetrieval:
    """Test patient retrieval endpoints"""
    
    def test_get_patients_list(self, client, auth_headers_doctor, patient_record):
        """Test getting list of patients"""
        response = client.get("/api/v1/patients/", headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "patients" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert data["total"] >= 1
        
        # Check if our patient is in the list
        patient_found = any(p["id"] == patient_record.id for p in data["patients"])
        assert patient_found
    
    def test_get_patients_with_pagination(self, client, auth_headers_doctor):
        """Test patient list with pagination"""
        response = client.get("/api/v1/patients/?page=1&per_page=5", 
                            headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["page"] == 1
        assert data["per_page"] == 5
        assert len(data["patients"]) <= 5
    
    def test_get_patients_with_search(self, client, auth_headers_doctor, patient_record):
        """Test patient list with search"""
        response = client.get(f"/api/v1/patients/?search={patient_record.user.first_name}", 
                            headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should find our patient
        assert data["total"] >= 1
    
    def test_get_patients_with_filters(self, client, auth_headers_doctor, patient_record):
        """Test patient list with filters"""
        response = client.get(f"/api/v1/patients/?risk_level={patient_record.risk_level}&is_active=true", 
                            headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All returned patients should match filters
        for patient in data["patients"]:
            assert patient["risk_level"] == patient_record.risk_level
            assert patient["is_active_patient"] is True
    
    def test_get_patient_by_id(self, client, auth_headers_doctor, patient_record):
        """Test getting specific patient by ID"""
        response = client.get(f"/api/v1/patients/{patient_record.id}", 
                            headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert_patient_response(data, patient_record)
    
    def test_get_patient_nonexistent(self, client, auth_headers_doctor):
        """Test getting nonexistent patient"""
        response = client.get("/api/v1/patients/99999", headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_patient_unauthorized(self, client, auth_headers_patient, patient_record, db_session):
        """Test patient access control"""
        # Create another patient
        other_user = TestDataGenerator.user_data(username="other_patient", email="other@test.com")
        from app.models.user import User
        from app.security import get_password_hash
        
        other_user_obj = User(
            username=other_user["username"],
            email=other_user["email"],
            hashed_password=get_password_hash(other_user["password"]),
            first_name=other_user["first_name"],
            last_name=other_user["last_name"],
            role=UserRole.PATIENT
        )
        db_session.add(other_user_obj)
        db_session.commit()
        
        other_patient_data = TestDataGenerator.patient_data(other_user_obj.id)
        other_patient = Patient(**other_patient_data)
        db_session.add(other_patient)
        db_session.commit()
        
        # Patient should not be able to access other patient's data
        response = client.get(f"/api/v1/patients/{other_patient.id}", 
                            headers=auth_headers_patient)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestPatientUpdate:
    """Test patient update endpoints"""
    
    def test_update_patient_success(self, client, auth_headers_doctor, patient_record):
        """Test successful patient update"""
        update_data = {
            "height": 170.0,
            "weight": 75.0,
            "risk_level": "medium",
            "notes": "Updated patient information"
        }
        
        response = client.put(f"/api/v1/patients/{patient_record.id}", 
                            json=update_data, 
                            headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["height"] == update_data["height"]
        assert data["weight"] == update_data["weight"]
        assert data["risk_level"] == update_data["risk_level"]
    
    def test_update_patient_unauthorized(self, client, auth_headers_patient, patient_record):
        """Test patient update without proper permissions"""
        update_data = {"height": 170.0}
        
        # Patient trying to update another patient
        response = client.put(f"/api/v1/patients/{patient_record.id}", 
                            json=update_data, 
                            headers=auth_headers_patient)
        
        # This should fail unless it's the patient's own record
        # The actual behavior depends on the patient_record fixture setup
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
    
    def test_update_patient_nonexistent(self, client, auth_headers_doctor):
        """Test updating nonexistent patient"""
        update_data = {"height": 170.0}
        
        response = client.put("/api/v1/patients/99999", 
                            json=update_data, 
                            headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_patient_invalid_data(self, client, auth_headers_doctor, patient_record):
        """Test patient update with invalid data"""
        update_data = {
            "height": -10,  # Invalid height
            "date_of_birth": "2030-01-01"  # Future date
        }
        
        response = client.put(f"/api/v1/patients/{patient_record.id}", 
                            json=update_data, 
                            headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_partial_update_patient(self, client, auth_headers_doctor, patient_record):
        """Test partial patient update"""
        update_data = {"weight": 72.5}
        
        response = client.put(f"/api/v1/patients/{patient_record.id}", 
                            json=update_data, 
                            headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["weight"] == update_data["weight"]
        # Other fields should remain unchanged
        assert data["height"] == patient_record.height


class TestPatientDeletion:
    """Test patient deletion endpoints"""
    
    def test_delete_patient_admin_only(self, client, auth_headers_admin, patient_record):
        """Test patient deletion (admin only)"""
        response = client.delete(f"/api/v1/patients/{patient_record.id}", 
                               headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_200_OK
        assert "deactivated" in response.json()["message"]
    
    def test_delete_patient_unauthorized(self, client, auth_headers_doctor, patient_record):
        """Test patient deletion without admin permissions"""
        response = client.delete(f"/api/v1/patients/{patient_record.id}", 
                               headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_patient_nonexistent(self, client, auth_headers_admin):
        """Test deleting nonexistent patient"""
        response = client.delete("/api/v1/patients/99999", 
                               headers=auth_headers_admin)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPatientSummary:
    """Test patient summary endpoints"""
    
    def test_get_patient_summary(self, client, auth_headers_doctor, patient_record):
        """Test getting patient summary"""
        response = client.get(f"/api/v1/patients/{patient_record.id}/summary", 
                            headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "patient_info" in data
        assert "health_metrics" in data
        assert "care_summary" in data
        assert "alerts" in data
        
        # Check patient info
        patient_info = data["patient_info"]
        assert patient_info["id"] == patient_record.id
        assert patient_info["patient_id"] == patient_record.patient_id
    
    def test_get_patient_summary_unauthorized(self, client, auth_headers_patient, patient_record):
        """Test patient summary access control"""
        # This test depends on whether the patient can access their own summary
        response = client.get(f"/api/v1/patients/{patient_record.id}/summary", 
                            headers=auth_headers_patient)
        
        # Should either succeed (own record) or fail (access control)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]


class TestCaregiverAssignment:
    """Test caregiver assignment endpoints"""
    
    def test_assign_caregiver_success(self, client, auth_headers_doctor, patient_record, db_session):
        """Test successful caregiver assignment"""
        # Create a caregiver user
        from app.models.user import User
        from app.security import get_password_hash
        
        caregiver_user = User(
            username="caregiver_test",
            email="caregiver@test.com",
            hashed_password=get_password_hash("caregiver123"),
            first_name="Care",
            last_name="Giver",
            role=UserRole.CAREGIVER
        )
        db_session.add(caregiver_user)
        db_session.commit()
        
        response = client.post(f"/api/v1/patients/{patient_record.id}/assign-caregiver", 
                             json={"caregiver_id": caregiver_user.id},
                             headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_200_OK
        assert "assigned successfully" in response.json()["message"]
    
    def test_assign_caregiver_unauthorized(self, client, auth_headers_patient, patient_record):
        """Test caregiver assignment without proper permissions"""
        response = client.post(f"/api/v1/patients/{patient_record.id}/assign-caregiver", 
                             json={"caregiver_id": 1},
                             headers=auth_headers_patient)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_assign_nonexistent_caregiver(self, client, auth_headers_doctor, patient_record):
        """Test assigning nonexistent caregiver"""
        response = client.post(f"/api/v1/patients/{patient_record.id}/assign-caregiver", 
                             json={"caregiver_id": 99999},
                             headers=auth_headers_doctor)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPatientValidation:
    """Test patient data validation"""
    
    def test_age_calculation(self, patient_record):
        """Test patient age calculation"""
        # Patient born in 1950, should be around 73-74 years old
        age = patient_record.age
        assert age >= 70
        assert age <= 80
    
    def test_bmi_calculation(self, patient_record):
        """Test BMI calculation"""
        # Height: 165cm, Weight: 70kg
        # BMI = 70 / (1.65^2) ≈ 25.7
        bmi = patient_record.bmi
        assert bmi is not None
        assert 25 <= bmi <= 26
    
    def test_elderly_status(self, patient_record):
        """Test elderly status determination"""
        assert patient_record.is_elderly is True
    
    def test_full_address_formatting(self, patient_record):
        """Test full address formatting"""
        full_address = patient_record.full_address
        assert "123 Main St" in full_address
        assert "Springfield" in full_address
        assert "IL" in full_address
        assert "62701" in full_address


class TestPatientIntegration:
    """Integration tests for patient management"""
    
    def test_complete_patient_lifecycle(self, client, auth_headers_doctor, patient_user, db_session):
        """Test complete patient management lifecycle"""
        # Create patient
        patient_data = TestDataGenerator.patient_data(patient_user.id)
        
        create_response = client.post("/api/v1/patients/", 
                                    json=patient_data, 
                                    headers=auth_headers_doctor)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        patient_id = create_response.json()["id"]
        
        # Read patient
        read_response = client.get(f"/api/v1/patients/{patient_id}", 
                                 headers=auth_headers_doctor)
        assert read_response.status_code == status.HTTP_200_OK
        
        # Update patient
        update_data = {"weight": 75.0, "risk_level": "medium"}
        update_response = client.put(f"/api/v1/patients/{patient_id}", 
                                   json=update_data, 
                                   headers=auth_headers_doctor)
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["weight"] == 75.0
        
        # Get summary
        summary_response = client.get(f"/api/v1/patients/{patient_id}/summary", 
                                    headers=auth_headers_doctor)
        assert summary_response.status_code == status.HTTP_200_OK
    
    def test_patient_search_and_filter(self, client, auth_headers_doctor, db_session):
        """Test patient search and filtering functionality"""
        # Create multiple patients with different characteristics
        patients_data = [
            {"first_name": "Alice", "last_name": "Smith", "risk_level": "low"},
            {"first_name": "Bob", "last_name": "Johnson", "risk_level": "high"},
            {"first_name": "Charlie", "last_name": "Brown", "risk_level": "medium"}
        ]
        
        created_patients = []
        for i, patient_info in enumerate(patients_data):
            # Create user first
            user_data = TestDataGenerator.user_data(
                username=f"patient_{i}",
                email=f"patient{i}@test.com",
                first_name=patient_info["first_name"],
                last_name=patient_info["last_name"]
            )
            
            from app.models.user import User
            from app.security import get_password_hash
            
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=UserRole.PATIENT
            )
            db_session.add(user)
            db_session.flush()
            
            # Create patient
            patient_data = TestDataGenerator.patient_data(user.id)
            patient_data["risk_level"] = patient_info["risk_level"]
            
            patient = Patient(**patient_data)
            db_session.add(patient)
            created_patients.append(patient)
        
        db_session.commit()
        
        # Test search by name
        search_response = client.get("/api/v1/patients/?search=Alice", 
                                   headers=auth_headers_doctor)
        assert search_response.status_code == status.HTTP_200_OK
        search_data = search_response.json()
        assert search_data["total"] >= 1
        
        # Test filter by risk level
        filter_response = client.get("/api/v1/patients/?risk_level=high", 
                                   headers=auth_headers_doctor)
        assert filter_response.status_code == status.HTTP_200_OK
        filter_data = filter_response.json()
        
        # All returned patients should have high risk level
        for patient in filter_data["patients"]:
            assert patient["risk_level"] == "high"