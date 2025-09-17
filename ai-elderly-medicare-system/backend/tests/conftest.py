"""
Pytest configuration and fixtures for AI Elderly Medicare System tests
"""

import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, date

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole, UserStatus
from app.models.patient import Patient, Gender, BloodType
from app.models.medication import Medication, MedicationType, MedicationStatus, FrequencyType
from app.models.appointment import Appointment, AppointmentType, AppointmentStatus, Priority
from app.models.notification import Notification, NotificationType, NotificationStatus, NotificationPriority
from app.security import get_password_hash, create_access_token

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_elderly_medicare.db"

@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    """Create database session for each test"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database session override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db_session):
    """Create admin user for testing"""
    user = User(
        username="admin_test",
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def doctor_user(db_session):
    """Create doctor user for testing"""
    user = User(
        username="doctor_test",
        email="doctor@test.com",
        hashed_password=get_password_hash("doctor123"),
        first_name="Dr. John",
        last_name="Smith",
        role=UserRole.DOCTOR,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_verified=True,
        license_number="MD123456",
        specialization="Geriatrics"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def patient_user(db_session):
    """Create patient user for testing"""
    user = User(
        username="patient_test",
        email="patient@test.com",
        hashed_password=get_password_hash("patient123"),
        first_name="Mary",
        last_name="Johnson",
        role=UserRole.PATIENT,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def patient_record(db_session, patient_user):
    """Create patient record for testing"""
    from app.security import generate_patient_id
    
    patient = Patient(
        user_id=patient_user.id,
        patient_id=generate_patient_id(),
        date_of_birth=date(1950, 5, 15),
        gender=Gender.FEMALE,
        blood_type=BloodType.A_POSITIVE,
        height=165.0,
        weight=70.0,
        address="123 Main St",
        city="Springfield",
        state="IL",
        zip_code="62701",
        medical_record_number="MRN123456",
        insurance_number="INS789012",
        medicare_number="1AB2-CD3-EF45"
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient

@pytest.fixture
def medication_record(db_session, patient_record, doctor_user):
    """Create medication record for testing"""
    medication = Medication(
        patient_id=patient_record.id,
        prescribed_by_id=doctor_user.id,
        name="Lisinopril",
        generic_name="Lisinopril",
        brand_name="Prinivil",
        medication_type=MedicationType.TABLET,
        strength="10mg",
        dosage_amount=1.0,
        dosage_unit="tablet",
        frequency=FrequencyType.ONCE_DAILY,
        route_of_administration="oral",
        instructions="Take once daily with water",
        start_date=datetime.now(),
        status=MedicationStatus.ACTIVE,
        quantity_prescribed=30,
        quantity_remaining=25,
        refills_remaining=2
    )
    db_session.add(medication)
    db_session.commit()
    db_session.refresh(medication)
    return medication

@pytest.fixture
def appointment_record(db_session, patient_record, doctor_user):
    """Create appointment record for testing"""
    from datetime import timedelta
    
    appointment = Appointment(
        patient_id=patient_record.id,
        provider_id=doctor_user.id,
        appointment_date=datetime.now() + timedelta(days=7),
        duration_minutes=30,
        appointment_type=AppointmentType.ROUTINE_CHECKUP,
        status=AppointmentStatus.SCHEDULED,
        priority=Priority.MEDIUM,
        location="Room 101",
        reason_for_visit="Routine checkup"
    )
    db_session.add(appointment)
    db_session.commit()
    db_session.refresh(appointment)
    return appointment

@pytest.fixture
def notification_record(db_session, patient_user):
    """Create notification record for testing"""
    notification = Notification(
        user_id=patient_user.id,
        title="Test Notification",
        message="This is a test notification",
        notification_type=NotificationType.MEDICATION_REMINDER,
        priority=NotificationPriority.MEDIUM,
        status=NotificationStatus.PENDING
    )
    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification)
    return notification

@pytest.fixture
def admin_token(admin_user):
    """Create admin access token for testing"""
    return create_access_token(data={"sub": str(admin_user.id), "username": admin_user.username})

@pytest.fixture
def doctor_token(doctor_user):
    """Create doctor access token for testing"""
    return create_access_token(data={"sub": str(doctor_user.id), "username": doctor_user.username})

@pytest.fixture
def patient_token(patient_user):
    """Create patient access token for testing"""
    return create_access_token(data={"sub": str(patient_user.id), "username": patient_user.username})

@pytest.fixture
def auth_headers_admin(admin_token):
    """Create authorization headers for admin"""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def auth_headers_doctor(doctor_token):
    """Create authorization headers for doctor"""
    return {"Authorization": f"Bearer {doctor_token}"}

@pytest.fixture
def auth_headers_patient(patient_token):
    """Create authorization headers for patient"""
    return {"Authorization": f"Bearer {patient_token}"}

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "555-0123",
        "role": "patient"
    }

@pytest.fixture
def sample_patient_data(patient_user):
    """Sample patient data for testing"""
    return {
        "user_id": patient_user.id,
        "date_of_birth": "1950-05-15",
        "gender": "female",
        "blood_type": "A_POSITIVE",
        "height": 165.0,
        "weight": 70.0,
        "address": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "zip_code": "12345",
        "medical_record_number": "TEST123",
        "insurance_number": "INS456",
        "medicare_number": "1AB2-CD3-EF45"
    }

@pytest.fixture
def sample_medication_data(patient_record):
    """Sample medication data for testing"""
    return {
        "patient_id": patient_record.id,
        "name": "Test Medication",
        "medication_type": "tablet",
        "strength": "5mg",
        "dosage_amount": 1.0,
        "dosage_unit": "tablet",
        "frequency": "once_daily",
        "instructions": "Take with food",
        "start_date": datetime.now().isoformat(),
        "quantity_prescribed": 30,
        "refills_remaining": 2
    }

@pytest.fixture
def sample_appointment_data(patient_record, doctor_user):
    """Sample appointment data for testing"""
    from datetime import timedelta
    
    return {
        "patient_id": patient_record.id,
        "provider_id": doctor_user.id,
        "appointment_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "duration_minutes": 30,
        "appointment_type": "routine_checkup",
        "priority": "medium",
        "location": "Test Room",
        "reason_for_visit": "Test appointment"
    }

@pytest.fixture
def sample_notification_data(patient_user):
    """Sample notification data for testing"""
    return {
        "user_id": patient_user.id,
        "title": "Test Notification",
        "message": "This is a test notification message",
        "notification_type": "medication_reminder",
        "priority": "medium"
    }

# Utility functions for tests
def create_test_file(content: str = "test content", filename: str = "test.txt"):
    """Create a temporary test file"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=filename)
    temp_file.write(content)
    temp_file.close()
    return temp_file.name

def cleanup_test_file(filepath: str):
    """Clean up test file"""
    try:
        os.unlink(filepath)
    except FileNotFoundError:
        pass

# Test data generators
class TestDataGenerator:
    """Generate test data for various entities"""
    
    @staticmethod
    def user_data(role: str = "patient", **kwargs):
        """Generate user test data"""
        base_data = {
            "username": f"test_{role}_{datetime.now().timestamp()}",
            "email": f"test_{role}@example.com",
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "555-0123",
            "role": role
        }
        base_data.update(kwargs)
        return base_data
    
    @staticmethod
    def patient_data(user_id: int, **kwargs):
        """Generate patient test data"""
        base_data = {
            "user_id": user_id,
            "date_of_birth": "1950-01-01",
            "gender": "male",
            "height": 175.0,
            "weight": 80.0,
            "address": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345"
        }
        base_data.update(kwargs)
        return base_data
    
    @staticmethod
    def medication_data(patient_id: int, **kwargs):
        """Generate medication test data"""
        base_data = {
            "patient_id": patient_id,
            "name": "Test Medication",
            "medication_type": "tablet",
            "frequency": "once_daily",
            "start_date": datetime.now().isoformat(),
            "quantity_prescribed": 30
        }
        base_data.update(kwargs)
        return base_data

# Mock services for testing
class MockEmailService:
    """Mock email service for testing"""
    
    def __init__(self):
        self.sent_emails = []
    
    def send_email(self, to_email: str, subject: str, body: str, **kwargs):
        """Mock send email"""
        self.sent_emails.append({
            "to": to_email,
            "subject": subject,
            "body": body,
            "kwargs": kwargs
        })
        return True
    
    def clear(self):
        """Clear sent emails"""
        self.sent_emails = []

@pytest.fixture
def mock_email_service():
    """Mock email service fixture"""
    return MockEmailService()

# Test database utilities
def clear_database(db_session):
    """Clear all data from test database"""
    # Delete in reverse order of dependencies
    db_session.query(Notification).delete()
    db_session.query(Medication).delete()
    db_session.query(Appointment).delete()
    db_session.query(Patient).delete()
    db_session.query(User).delete()
    db_session.commit()

def count_records(db_session, model):
    """Count records in a table"""
    return db_session.query(model).count()

# Test assertions
def assert_user_response(response_data: dict, expected_user: User):
    """Assert user response data matches expected user"""
    assert response_data["id"] == expected_user.id
    assert response_data["username"] == expected_user.username
    assert response_data["email"] == expected_user.email
    assert response_data["first_name"] == expected_user.first_name
    assert response_data["last_name"] == expected_user.last_name
    assert response_data["role"] == expected_user.role.value

def assert_patient_response(response_data: dict, expected_patient: Patient):
    """Assert patient response data matches expected patient"""
    assert response_data["id"] == expected_patient.id
    assert response_data["patient_id"] == expected_patient.patient_id
    assert response_data["user_id"] == expected_patient.user_id
    assert response_data["gender"] == expected_patient.gender.value

def assert_medication_response(response_data: dict, expected_medication: Medication):
    """Assert medication response data matches expected medication"""
    assert response_data["id"] == expected_medication.id
    assert response_data["name"] == expected_medication.name
    assert response_data["patient_id"] == expected_medication.patient_id
    assert response_data["status"] == expected_medication.status.value