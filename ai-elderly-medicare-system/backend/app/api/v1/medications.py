"""
Medication management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import logging

from app.database import get_db
from app.models.medication import Medication, MedicationType, MedicationStatus, FrequencyType
from app.models.user import User, UserRole
from app.models.patient import Patient
from app.security import verify_token
from app.services.auth_service import AuthService
from app.services.medication_service import MedicationService
from app.services.notification_service import NotificationService
from app.utils.exceptions import ValidationError, PermissionError

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Pydantic models
from pydantic import BaseModel, validator

class MedicationCreate(BaseModel):
    patient_id: int
    name: str
    generic_name: Optional[str] = None
    brand_name: Optional[str] = None
    medication_type: MedicationType
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    dosage_amount: Optional[float] = None
    dosage_unit: Optional[str] = None
    frequency: FrequencyType
    frequency_details: Optional[str] = None
    route_of_administration: Optional[str] = None
    instructions: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    duration_days: Optional[int] = None
    quantity_prescribed: Optional[int] = None
    refills_remaining: Optional[int] = 0
    is_critical: Optional[bool] = False
    requires_monitoring: Optional[bool] = False
    notes: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Medication name must be at least 2 characters')
        return v.strip()
    
    @validator('dosage_amount')
    def validate_dosage(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Dosage amount must be positive')
        return v

class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    generic_name: Optional[str] = None
    brand_name: Optional[str] = None
    medication_type: Optional[MedicationType] = None
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    dosage_amount: Optional[float] = None
    dosage_unit: Optional[str] = None
    frequency: Optional[FrequencyType] = None
    frequency_details: Optional[str] = None
    route_of_administration: Optional[str] = None
    instructions: Optional[str] = None
    end_date: Optional[datetime] = None
    duration_days: Optional[int] = None
    quantity_prescribed: Optional[int] = None
    quantity_remaining: Optional[int] = None
    refills_remaining: Optional[int] = None
    status: Optional[MedicationStatus] = None
    is_critical: Optional[bool] = None
    requires_monitoring: Optional[bool] = None
    notes: Optional[str] = None

class MedicationResponse(BaseModel):
    id: int
    patient_id: int
    name: str
    generic_name: Optional[str]
    brand_name: Optional[str]
    medication_type: MedicationType
    strength: Optional[str]
    dosage_form: Optional[str]
    dosage_amount: Optional[float]
    dosage_unit: Optional[str]
    frequency: FrequencyType
    frequency_details: Optional[str]
    route_of_administration: Optional[str]
    instructions: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    duration_days: Optional[int]
    status: MedicationStatus
    quantity_prescribed: Optional[int]
    quantity_remaining: Optional[int]
    refills_remaining: Optional[int]
    is_critical: bool
    requires_monitoring: bool
    adherence_score: Optional[float]
    missed_doses: int
    last_taken: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed fields
    is_active: bool
    is_due_for_refill: bool
    days_supply_remaining: int
    is_expired: bool
    full_name: str
    
    class Config:
        from_attributes = True

class MedicationListResponse(BaseModel):
    medications: List[MedicationResponse]
    total: int
    page: int
    per_page: int
    pages: int

class DoseTakenRequest(BaseModel):
    taken_at: Optional[datetime] = None
    notes: Optional[str] = None

class RefillRequest(BaseModel):
    quantity: int
    refills: Optional[int] = 0
    pharmacy_notes: Optional[str] = None

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

@router.post("/", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
async def create_medication(
    medication_data: MedicationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new medication"""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create medication"
            )
        
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == medication_data.patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Create medication
        medication = Medication(
            prescribed_by_id=current_user.id,
            **medication_data.dict()
        )
        
        db.add(medication)
        db.commit()
        db.refresh(medication)
        
        # Set up medication reminders
        medication_service = MedicationService(db)
        background_tasks.add_task(
            medication_service.setup_medication_reminders,
            medication.id
        )
        
        logger.info(f"Medication created: {medication.name} for patient {patient.patient_id}")
        return MedicationResponse.from_orm(medication)
        
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Create medication error: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create medication")

@router.get("/", response_model=MedicationListResponse)
async def get_medications(
    patient_id: Optional[int] = Query(None),
    status_filter: Optional[MedicationStatus] = Query(None),
    is_critical: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of medications with filtering"""
    try:
        # Build query
        query = db.query(Medication)
        
        # Apply patient filter based on user role
        if current_user.role == UserRole.PATIENT:
            # Patients can only see their own medications
            patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
            if patient:
                query = query.filter(Medication.patient_id == patient.id)
            else:
                return MedicationListResponse(medications=[], total=0, page=page, per_page=per_page, pages=0)
        elif patient_id:
            # Healthcare providers can filter by patient
            query = query.filter(Medication.patient_id == patient_id)
        
        # Apply other filters
        if status_filter:
            query = query.filter(Medication.status == status_filter)
        
        if is_critical is not None:
            query = query.filter(Medication.is_critical == is_critical)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        medications = query.offset(offset).limit(per_page).all()
        
        pages = (total + per_page - 1) // per_page
        
        return MedicationListResponse(
            medications=[MedicationResponse.from_orm(med) for med in medications],
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Get medications error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve medications")

@router.get("/{medication_id}", response_model=MedicationResponse)
async def get_medication(
    medication_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get medication by ID"""
    try:
        # Get medication
        medication = db.query(Medication).filter(Medication.id == medication_id).first()
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )
        
        # Check permissions
        if current_user.role == UserRole.PATIENT:
            patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
            if not patient or medication.patient_id != patient.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to view this medication"
                )
        
        return MedicationResponse.from_orm(medication)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get medication error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve medication")

@router.put("/{medication_id}", response_model=MedicationResponse)
async def update_medication(
    medication_id: int,
    medication_data: MedicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update medication information"""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update medication"
            )
        
        # Get medication
        medication = db.query(Medication).filter(Medication.id == medication_id).first()
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )
        
        # Update medication data
        update_data = medication_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(medication, field, value)
        
        medication.updated_at = datetime.now()
        
        db.commit()
        db.refresh(medication)
        
        logger.info(f"Medication updated: {medication.name} by user {current_user.username}")
        return MedicationResponse.from_orm(medication)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update medication error: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update medication")

@router.post("/{medication_id}/take-dose")
async def record_dose_taken(
    medication_id: int,
    dose_data: DoseTakenRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record that a medication dose was taken"""
    try:
        # Get medication
        medication = db.query(Medication).filter(Medication.id == medication_id).first()
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )
        
        # Check permissions
        if current_user.role == UserRole.PATIENT:
            patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
            if not patient or medication.patient_id != patient.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to record dose for this medication"
                )
        
        # Record dose taken
        medication.record_dose_taken()
        
        if dose_data.taken_at:
            medication.last_taken = dose_data.taken_at
        
        if dose_data.notes:
            current_notes = medication.patient_notes or ""
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            medication.patient_notes = f"{current_notes}\n[{timestamp}] Dose taken: {dose_data.notes}".strip()
        
        db.commit()
        
        # Send confirmation notification
        notification_service = NotificationService(db)
        background_tasks.add_task(
            notification_service.send_dose_confirmation,
            medication.patient_id,
            medication.name
        )
        
        logger.info(f"Dose recorded for medication: {medication.name}")
        return {"message": "Dose recorded successfully", "next_dose_due": medication.is_time_for_dose()}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Record dose error: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to record dose")

@router.post("/{medication_id}/missed-dose")
async def record_missed_dose(
    medication_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a missed medication dose"""
    try:
        # Get medication
        medication = db.query(Medication).filter(Medication.id == medication_id).first()
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )
        
        # Check permissions
        if current_user.role == UserRole.PATIENT:
            patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
            if not patient or medication.patient_id != patient.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to record missed dose for this medication"
                )
        
        # Record missed dose
        medication.record_missed_dose()
        
        db.commit()
        
        logger.info(f"Missed dose recorded for medication: {medication.name}")
        return {"message": "Missed dose recorded", "adherence_score": medication.adherence_score}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Record missed dose error: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to record missed dose")

@router.post("/{medication_id}/refill")
async def add_refill(
    medication_id: int,
    refill_data: RefillRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add refill to medication"""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to add refill"
            )
        
        # Get medication
        medication = db.query(Medication).filter(Medication.id == medication_id).first()
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )
        
        # Add refill
        medication.add_refill(refill_data.quantity, refill_data.refills)
        
        if refill_data.pharmacy_notes:
            medication.pharmacy_notes = refill_data.pharmacy_notes
        
        db.commit()
        
        logger.info(f"Refill added for medication: {medication.name}")
        return {
            "message": "Refill added successfully",
            "quantity_remaining": medication.quantity_remaining,
            "refills_remaining": medication.refills_remaining,
            "next_refill_due": medication.next_refill_due
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add refill error: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add refill")

@router.post("/{medication_id}/discontinue")
async def discontinue_medication(
    medication_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Discontinue medication"""
    try:
        # Check permissions
        if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.NURSE]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to discontinue medication"
            )
        
        # Get medication
        medication = db.query(Medication).filter(Medication.id == medication_id).first()
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )
        
        # Discontinue medication
        medication.discontinue(reason)
        
        db.commit()
        
        logger.info(f"Medication discontinued: {medication.name} by user {current_user.username}")
        return {"message": "Medication discontinued successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Discontinue medication error: {e}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to discontinue medication")

@router.get("/{medication_id}/interactions")
async def check_drug_interactions(
    medication_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check drug interactions for medication"""
    try:
        # Get medication
        medication = db.query(Medication).filter(Medication.id == medication_id).first()
        if not medication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found"
            )
        
        # Check permissions
        if current_user.role == UserRole.PATIENT:
            patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
            if not patient or medication.patient_id != patient.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to view interactions for this medication"
                )
        
        # Get other medications for the patient
        other_medications = db.query(Medication).filter(
            Medication.patient_id == medication.patient_id,
            Medication.id != medication.id,
            Medication.status == MedicationStatus.ACTIVE
        ).all()
        
        # Check interactions
        interactions = medication.check_drug_interactions(other_medications)
        
        return {
            "medication": medication.name,
            "interactions": interactions,
            "total_interactions": len(interactions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Check interactions error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to check interactions")

@router.get("/patient/{patient_id}/adherence")
async def get_medication_adherence(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get medication adherence report for patient"""
    try:
        # Check permissions
        if current_user.role == UserRole.PATIENT:
            patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
            if not patient or patient.id != patient_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to view adherence for this patient"
                )
        
        # Get patient medications
        medications = db.query(Medication).filter(
            Medication.patient_id == patient_id,
            Medication.status == MedicationStatus.ACTIVE
        ).all()
        
        adherence_data = []
        total_adherence = 0
        
        for medication in medications:
            medication.update_adherence_score()
            adherence_data.append({
                "medication_id": medication.id,
                "medication_name": medication.name,
                "adherence_score": medication.adherence_score or 0,
                "missed_doses": medication.missed_doses,
                "is_critical": medication.is_critical
            })
            total_adherence += (medication.adherence_score or 0)
        
        average_adherence = total_adherence / len(medications) if medications else 0
        
        return {
            "patient_id": patient_id,
            "average_adherence": round(average_adherence, 2),
            "total_medications": len(medications),
            "medications": adherence_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get adherence error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get adherence data")