"""
Patient management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import logging

from app.database import get_db
from app.models.patient import Patient, Gender, BloodType
from app.models.user import User, UserRole
from app.security import verify_token
from app.services.auth_service import AuthService
from app.utils.exceptions import ValidationError, PermissionError

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Pydantic models
from pydantic import BaseModel, validator

class PatientCreate(BaseModel):
    user_id: int
    date_of_birth: date
    gender: Gender
    blood_type: Optional[BloodType] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    medical_record_number: Optional[str] = None
    insurance_number: Optional[str] = None
    medicare_number: Optional[str] = None
    primary_physician_id: Optional[int] = None
    assigned_caregiver_id: Optional[int] = None
    care_plan: Optional[str] = None
    special_needs: Optional[str] = None
    
    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        if v > date.today():
            raise ValueError('Birth date cannot be in the future')
        return v
    
    @validator('height')
    def validate_height(cls, v):
        if v is not None and (v < 50 or v > 250):
            raise ValueError('Height must be between 50-250 cm')
        return v
    
    @validator('weight')
    def validate_weight(cls, v):
        if v is not None and (v < 20 or v > 300):
            raise ValueError('Weight must be between 20-300 kg')
        return v

class PatientUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    blood_type: Optional[BloodType] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    medical_record_number: Optional[str] = None
    insurance_number: Optional[str] = None
    medicare_number: Optional[str] = None
    primary_physician_id: Optional[int] = None
    assigned_caregiver_id: Optional[int] = None
    care_plan: Optional[str] = None
    special_needs: Optional[str] = None
    risk_level: Optional[str] = None
    mobility_status: Optional[str] = None
    cognitive_status: Optional[str] = None

class PatientResponse(BaseModel):
    id: int
    patient_id: str
    user_id: int
    date_of_birth: date
    gender: Gender
    blood_type: Optional[BloodType]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    medical_record_number: Optional[str]
    insurance_number: Optional[str]
    medicare_number: Optional[str]
    risk_level: str
    mobility_status: Optional[str]
    cognitive_status: Optional[str]
    care_plan: Optional[str]
    special_needs: Optional[str]
    is_active_patient: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_visit: Optional[datetime]
    
    # Computed fields
    age: Optional[int]
    bmi: Optional[float]
    is_elderly: Optional[bool]
    full_address: Optional[str]
    
    # User information
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str]
    
    class Config:
        from_attributes = True

class PatientListResponse(BaseModel):
    patients: List[PatientResponse]
    total: int
    page: int
    per_page: int
    pages: int

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(int(user_id))
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new patient"""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create patient"
            )
        
        # Verify user exists
        user = db.query(User).filter(User.id == patient_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if patient already exists for this user
        existing_patient = db.query(Patient).filter(Patient.user_id == patient_data.user_id).first()
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient profile already exists for this user"
            )
        
        # Generate patient ID
        from app.security import generate_patient_id
        patient_id = generate_patient_id()
        
        # Create patient
        patient = Patient(
            patient_id=patient_id,
            **patient_data.dict()
        )
        
        db.add(patient)
        db.commit()
        db.refresh(patient)
        
        # Prepare response with user data
        response_data = PatientResponse.from_orm(patient)
        response_data.first_name = user.first_name
        response_data.last_name = user.last_name
        response_data.email = user.email
        response_data.phone_number = user.phone_number
        
        logger.info(f"Patient created: {patient.patient_id} by user {current_user.username}")
        return response_data
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Create patient error: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create patient")

@router.get("/", response_model=PatientListResponse)
async def get_patients(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of patients with pagination and filtering"""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE, UserRole.CAREGIVER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view patients"
            )
        
        # Build query
        query = db.query(Patient).join(User, Patient.user_id == User.id)
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.first_name.ilike(search_term)) |
                (User.last_name.ilike(search_term)) |
                (Patient.patient_id.ilike(search_term)) |
                (Patient.medical_record_number.ilike(search_term))
            )
        
        if risk_level:
            query = query.filter(Patient.risk_level == risk_level)
        
        if is_active is not None:
            query = query.filter(Patient.is_active_patient == is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        patients = query.offset(offset).limit(per_page).all()
        
        # Prepare response data
        patient_responses = []
        for patient in patients:
            response_data = PatientResponse.from_orm(patient)
            response_data.first_name = patient.user.first_name
            response_data.last_name = patient.user.last_name
            response_data.email = patient.user.email
            response_data.phone_number = patient.user.phone_number
            patient_responses.append(response_data)
        
        pages = (total + per_page - 1) // per_page
        
        return PatientListResponse(
            patients=patient_responses,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Get patients error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve patients")

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient by ID"""
    try:
        # Get patient
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check permissions
        if not current_user.can_access_patient(patient_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view this patient"
            )
        
        # Prepare response with user data
        response_data = PatientResponse.from_orm(patient)
        response_data.first_name = patient.user.first_name
        response_data.last_name = patient.user.last_name
        response_data.email = patient.user.email
        response_data.phone_number = patient.user.phone_number
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get patient error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve patient")

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update patient information"""
    try:
        # Get patient
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE]:
            if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to update this patient"
                )
        
        # Update patient data
        update_data = patient_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)
        
        patient.updated_at = datetime.now()
        
        db.commit()
        db.refresh(patient)
        
        # Prepare response with user data
        response_data = PatientResponse.from_orm(patient)
        response_data.first_name = patient.user.first_name
        response_data.last_name = patient.user.last_name
        response_data.email = patient.user.email
        response_data.phone_number = patient.user.phone_number
        
        logger.info(f"Patient updated: {patient.patient_id} by user {current_user.username}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update patient error: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update patient")

@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete patient (soft delete by deactivating)"""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete patient"
            )
        
        # Get patient
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Soft delete by deactivating
        patient.is_active_patient = False
        patient.updated_at = datetime.now()
        
        db.commit()
        
        logger.info(f"Patient deactivated: {patient.patient_id} by user {current_user.username}")
        return {"message": "Patient deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete patient error: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete patient")

@router.get("/{patient_id}/summary")
async def get_patient_summary(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get patient summary with health metrics"""
    try:
        # Get patient
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check permissions
        if not current_user.can_access_patient(patient_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view this patient"
            )
        
        # Get latest health record
        latest_health_record = patient.get_latest_health_record()
        
        # Get current medications
        current_medications = patient.get_current_medications()
        
        # Get upcoming appointments
        upcoming_appointments = patient.get_upcoming_appointments()
        
        summary = {
            "patient_info": {
                "id": patient.id,
                "patient_id": patient.patient_id,
                "name": patient.user.full_name,
                "age": patient.age,
                "gender": patient.gender.value if patient.gender else None,
                "risk_level": patient.risk_level
            },
            "health_metrics": {
                "bmi": patient.bmi,
                "latest_vitals": latest_health_record.vital_signs_summary if latest_health_record else None,
                "health_score": latest_health_record.calculate_health_score() if latest_health_record else None
            },
            "care_summary": {
                "active_medications": len(current_medications),
                "upcoming_appointments": len(upcoming_appointments),
                "primary_physician": patient.primary_physician.full_name if patient.primary_physician else None,
                "assigned_caregiver": patient.assigned_caregiver.full_name if patient.assigned_caregiver else None
            },
            "alerts": []
        }
        
        # Add alerts based on health data
        if latest_health_record and latest_health_record.is_critical:
            summary["alerts"].append("Critical vital signs detected")
        
        if patient.risk_level in ["high", "critical"]:
            summary["alerts"].append(f"Patient has {patient.risk_level} risk level")
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get patient summary error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve patient summary")

@router.post("/{patient_id}/assign-caregiver")
async def assign_caregiver(
    patient_id: int,
    caregiver_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign caregiver to patient"""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to assign caregiver"
            )
        
        # Get patient
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Verify caregiver exists
        caregiver = db.query(User).filter(
            User.id == caregiver_id,
            User.role == UserRole.CAREGIVER
        ).first()
        if not caregiver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Caregiver not found"
            )
        
        # Assign caregiver
        patient.assigned_caregiver_id = caregiver_id
        patient.updated_at = datetime.now()
        
        db.commit()
        
        logger.info(f"Caregiver {caregiver_id} assigned to patient {patient.patient_id}")
        return {"message": "Caregiver assigned successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Assign caregiver error: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to assign caregiver")