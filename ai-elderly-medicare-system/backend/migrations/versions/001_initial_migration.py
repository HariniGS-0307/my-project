"""Initial migration - Create all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('role', sa.Enum('ADMIN', 'DOCTOR', 'NURSE', 'CAREGIVER', 'PATIENT', 'FAMILY_MEMBER', name='userrole'), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED', 'PENDING', name='userstatus'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('license_number', sa.String(length=50), nullable=True),
        sa.Column('specialization', sa.String(length=100), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('profile_picture', sa.String(length=255), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('preferences', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create patients table
    op.create_table('patients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.String(length=20), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('gender', sa.Enum('MALE', 'FEMALE', 'OTHER', name='gender'), nullable=False),
        sa.Column('blood_type', sa.Enum('A_POSITIVE', 'A_NEGATIVE', 'B_POSITIVE', 'B_NEGATIVE', 'AB_POSITIVE', 'AB_NEGATIVE', 'O_POSITIVE', 'O_NEGATIVE', name='bloodtype'), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('country', sa.String(length=50), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('medical_record_number', sa.String(length=50), nullable=True),
        sa.Column('insurance_number', sa.String(length=100), nullable=True),
        sa.Column('medicare_number', sa.String(length=50), nullable=True),
        sa.Column('is_active_patient', sa.Boolean(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('mobility_status', sa.String(length=50), nullable=True),
        sa.Column('cognitive_status', sa.String(length=50), nullable=True),
        sa.Column('primary_physician_id', sa.Integer(), nullable=True),
        sa.Column('assigned_caregiver_id', sa.Integer(), nullable=True),
        sa.Column('care_plan', sa.Text(), nullable=True),
        sa.Column('special_needs', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_visit', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_caregiver_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['primary_physician_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patients_id'), 'patients', ['id'], unique=False)
    op.create_index(op.f('ix_patients_patient_id'), 'patients', ['patient_id'], unique=True)

    # Create health_records table
    op.create_table('health_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('recorded_by_id', sa.Integer(), nullable=False),
        sa.Column('systolic_bp', sa.Integer(), nullable=True),
        sa.Column('diastolic_bp', sa.Integer(), nullable=True),
        sa.Column('heart_rate', sa.Integer(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('respiratory_rate', sa.Integer(), nullable=True),
        sa.Column('oxygen_saturation', sa.Float(), nullable=True),
        sa.Column('blood_sugar', sa.Float(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('bmi', sa.Float(), nullable=True),
        sa.Column('pain_level', sa.Integer(), nullable=True),
        sa.Column('mood_score', sa.Integer(), nullable=True),
        sa.Column('sleep_hours', sa.Float(), nullable=True),
        sa.Column('activity_level', sa.String(length=20), nullable=True),
        sa.Column('symptoms', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('diagnosis', sa.Text(), nullable=True),
        sa.Column('treatment_plan', sa.Text(), nullable=True),
        sa.Column('ai_risk_score', sa.Float(), nullable=True),
        sa.Column('ai_recommendations', sa.JSON(), nullable=True),
        sa.Column('anomaly_detected', sa.Boolean(), nullable=True),
        sa.Column('record_type', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('device_used', sa.String(length=100), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['recorded_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_health_records_id'), 'health_records', ['id'], unique=False)

    # Create appointments table
    op.create_table('appointments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('appointment_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('appointment_type', sa.Enum('ROUTINE_CHECKUP', 'FOLLOW_UP', 'EMERGENCY', 'CONSULTATION', 'MEDICATION_REVIEW', 'THERAPY', 'VACCINATION', 'DIAGNOSTIC', 'TELEHEALTH', name='appointmenttype'), nullable=False),
        sa.Column('status', sa.Enum('SCHEDULED', 'CONFIRMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'NO_SHOW', 'RESCHEDULED', name='appointmentstatus'), nullable=True),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', 'EMERGENCY', name='priority'), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('room_number', sa.String(length=20), nullable=True),
        sa.Column('is_virtual', sa.Boolean(), nullable=True),
        sa.Column('virtual_meeting_link', sa.String(length=500), nullable=True),
        sa.Column('chief_complaint', sa.Text(), nullable=True),
        sa.Column('reason_for_visit', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('preparation_instructions', sa.Text(), nullable=True),
        sa.Column('follow_up_required', sa.Boolean(), nullable=True),
        sa.Column('follow_up_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('follow_up_notes', sa.Text(), nullable=True),
        sa.Column('insurance_authorization', sa.String(length=100), nullable=True),
        sa.Column('copay_amount', sa.Integer(), nullable=True),
        sa.Column('billing_code', sa.String(length=20), nullable=True),
        sa.Column('reminder_sent', sa.Boolean(), nullable=True),
        sa.Column('confirmation_required', sa.Boolean(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['provider_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_appointments_id'), 'appointments', ['id'], unique=False)

    # Create prescriptions table
    op.create_table('prescriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('prescriber_id', sa.Integer(), nullable=False),
        sa.Column('prescription_number', sa.String(length=50), nullable=False),
        sa.Column('rx_number', sa.String(length=20), nullable=True),
        sa.Column('ndc_number', sa.String(length=20), nullable=True),
        sa.Column('prescription_type', sa.Enum('NEW', 'REFILL', 'RENEWAL', 'MODIFICATION', 'EMERGENCY', 'DISCHARGE', name='prescriptiontype'), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'ACTIVE', 'FILLED', 'PARTIALLY_FILLED', 'EXPIRED', 'CANCELLED', 'DISCONTINUED', 'ON_HOLD', name='prescriptionstatus'), nullable=True),
        sa.Column('priority', sa.Enum('ROUTINE', 'URGENT', 'STAT', 'ASAP', name='prescriptionpriority'), nullable=True),
        sa.Column('medication_name', sa.String(length=200), nullable=False),
        sa.Column('generic_name', sa.String(length=200), nullable=True),
        sa.Column('brand_name', sa.String(length=200), nullable=True),
        sa.Column('strength', sa.String(length=50), nullable=True),
        sa.Column('dosage_form', sa.String(length=50), nullable=True),
        sa.Column('sig', sa.Text(), nullable=False),
        sa.Column('dosage_instructions', sa.Text(), nullable=True),
        sa.Column('route_of_administration', sa.String(length=50), nullable=True),
        sa.Column('frequency', sa.String(length=100), nullable=True),
        sa.Column('quantity_prescribed', sa.Integer(), nullable=False),
        sa.Column('quantity_dispensed', sa.Integer(), nullable=True),
        sa.Column('days_supply', sa.Integer(), nullable=True),
        sa.Column('unit_of_measure', sa.String(length=20), nullable=True),
        sa.Column('refills_authorized', sa.Integer(), nullable=True),
        sa.Column('refills_remaining', sa.Integer(), nullable=True),
        sa.Column('refills_used', sa.Integer(), nullable=True),
        sa.Column('date_prescribed', sa.DateTime(timezone=True), nullable=False),
        sa.Column('date_filled', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expiration_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_fill_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_fill_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('diagnosis_code', sa.String(length=20), nullable=True),
        sa.Column('diagnosis_description', sa.String(length=200), nullable=True),
        sa.Column('indication', sa.Text(), nullable=True),
        sa.Column('contraindications', sa.JSON(), nullable=True),
        sa.Column('drug_interactions', sa.JSON(), nullable=True),
        sa.Column('allergies_checked', sa.Boolean(), nullable=True),
        sa.Column('requires_monitoring', sa.Boolean(), nullable=True),
        sa.Column('monitoring_parameters', sa.JSON(), nullable=True),
        sa.Column('pharmacy_id', sa.String(length=50), nullable=True),
        sa.Column('pharmacy_name', sa.String(length=200), nullable=True),
        sa.Column('pharmacy_phone', sa.String(length=20), nullable=True),
        sa.Column('pharmacy_address', sa.Text(), nullable=True),
        sa.Column('pharmacist_name', sa.String(length=100), nullable=True),
        sa.Column('insurance_plan', sa.String(length=100), nullable=True),
        sa.Column('insurance_group', sa.String(length=50), nullable=True),
        sa.Column('prior_authorization_required', sa.Boolean(), nullable=True),
        sa.Column('prior_authorization_number', sa.String(length=50), nullable=True),
        sa.Column('copay_amount', sa.Float(), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=True),
        sa.Column('insurance_covered_amount', sa.Float(), nullable=True),
        sa.Column('is_electronic', sa.Boolean(), nullable=True),
        sa.Column('electronic_signature', sa.Text(), nullable=True),
        sa.Column('transmission_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confirmation_number', sa.String(length=50), nullable=True),
        sa.Column('is_controlled_substance', sa.Boolean(), nullable=True),
        sa.Column('dea_schedule', sa.String(length=10), nullable=True),
        sa.Column('dea_number', sa.String(length=20), nullable=True),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.Column('patient_counseling_info', sa.Text(), nullable=True),
        sa.Column('pharmacy_notes', sa.Text(), nullable=True),
        sa.Column('drug_utilization_review', sa.Boolean(), nullable=True),
        sa.Column('dur_alerts', sa.JSON(), nullable=True),
        sa.Column('clinical_decision_support', sa.JSON(), nullable=True),
        sa.Column('adherence_score', sa.Float(), nullable=True),
        sa.Column('missed_doses_reported', sa.Integer(), nullable=True),
        sa.Column('side_effects_reported', sa.JSON(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=True),
        sa.Column('approved_by_id', sa.Integer(), nullable=True),
        sa.Column('approval_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('modified_by_id', sa.Integer(), nullable=True),
        sa.Column('prescriber_notes', sa.Text(), nullable=True),
        sa.Column('pharmacist_notes', sa.Text(), nullable=True),
        sa.Column('patient_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('discontinued_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['modified_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['prescriber_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prescriptions_id'), 'prescriptions', ['id'], unique=False)
    op.create_index(op.f('ix_prescriptions_prescription_number'), 'prescriptions', ['prescription_number'], unique=True)

    # Create medications table
    op.create_table('medications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('prescribed_by_id', sa.Integer(), nullable=False),
        sa.Column('prescription_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('generic_name', sa.String(length=200), nullable=True),
        sa.Column('brand_name', sa.String(length=200), nullable=True),
        sa.Column('ndc_number', sa.String(length=20), nullable=True),
        sa.Column('medication_type', sa.Enum('TABLET', 'CAPSULE', 'LIQUID', 'INJECTION', 'TOPICAL', 'INHALER', 'PATCH', 'DROPS', 'SUPPOSITORY', 'OTHER', name='medicationtype'), nullable=False),
        sa.Column('strength', sa.String(length=50), nullable=True),
        sa.Column('dosage_form', sa.String(length=50), nullable=True),
        sa.Column('dosage_amount', sa.Float(), nullable=True),
        sa.Column('dosage_unit', sa.String(length=20), nullable=True),
        sa.Column('frequency', sa.Enum('ONCE_DAILY', 'TWICE_DAILY', 'THREE_TIMES_DAILY', 'FOUR_TIMES_DAILY', 'AS_NEEDED', 'WEEKLY', 'MONTHLY', 'CUSTOM', name='frequencytype'), nullable=False),
        sa.Column('frequency_details', sa.String(length=100), nullable=True),
        sa.Column('route_of_administration', sa.String(length=50), nullable=True),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_days', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'DISCONTINUED', 'COMPLETED', 'ON_HOLD', name='medicationstatus'), nullable=True),
        sa.Column('is_critical', sa.Boolean(), nullable=True),
        sa.Column('requires_monitoring', sa.Boolean(), nullable=True),
        sa.Column('quantity_prescribed', sa.Integer(), nullable=True),
        sa.Column('quantity_remaining', sa.Integer(), nullable=True),
        sa.Column('refills_remaining', sa.Integer(), nullable=True),
        sa.Column('last_refill_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_refill_due', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cost_per_unit', sa.Float(), nullable=True),
        sa.Column('insurance_covered', sa.Boolean(), nullable=True),
        sa.Column('copay_amount', sa.Float(), nullable=True),
        sa.Column('known_side_effects', sa.JSON(), nullable=True),
        sa.Column('drug_interactions', sa.JSON(), nullable=True),
        sa.Column('allergies_warnings', sa.Text(), nullable=True),
        sa.Column('ai_risk_score', sa.Float(), nullable=True),
        sa.Column('ai_recommendations', sa.JSON(), nullable=True),
        sa.Column('interaction_alerts', sa.JSON(), nullable=True),
        sa.Column('adherence_score', sa.Float(), nullable=True),
        sa.Column('missed_doses', sa.Integer(), nullable=True),
        sa.Column('last_taken', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('pharmacy_notes', sa.Text(), nullable=True),
        sa.Column('patient_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('discontinued_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['prescribed_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_medications_id'), 'medications', ['id'], unique=False)
    op.create_index(op.f('ix_medications_name'), 'medications', ['name'], unique=False)

    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.Enum('MEDICATION_REMINDER', 'APPOINTMENT_REMINDER', 'HEALTH_ALERT', 'SYSTEM_ALERT', 'DELIVERY_UPDATE', 'EMERGENCY_ALERT', 'CARE_PLAN_UPDATE', 'LAB_RESULT', 'PRESCRIPTION_READY', 'REFILL_REMINDER', 'VITAL_SIGNS_ALERT', 'AI_RECOMMENDATION', name='notificationtype'), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', 'CRITICAL', name='notificationpriority'), nullable=True),
        sa.Column('channel', sa.Enum('EMAIL', 'SMS', 'PUSH', 'IN_APP', 'PHONE_CALL', 'PORTAL', name='notificationchannel'), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'SENT', 'DELIVERED', 'READ', 'FAILED', 'CANCELLED', name='notificationstatus'), nullable=True),
        sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('patient_id', sa.Integer(), nullable=True),
        sa.Column('appointment_id', sa.Integer(), nullable=True),
        sa.Column('medication_id', sa.Integer(), nullable=True),
        sa.Column('health_record_id', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('action_url', sa.String(length=500), nullable=True),
        sa.Column('action_text', sa.String(length=100), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('max_retries', sa.Integer(), nullable=True),
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('group_id', sa.String(length=100), nullable=True),
        sa.Column('thread_id', sa.String(length=100), nullable=True),
        sa.Column('parent_notification_id', sa.Integer(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('is_archived', sa.Boolean(), nullable=True),
        sa.Column('is_starred', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
        sa.ForeignKeyConstraint(['health_record_id'], ['health_records.id'], ),
        sa.ForeignKeyConstraint(['medication_id'], ['medications.id'], ),
        sa.ForeignKeyConstraint(['parent_notification_id'], ['notifications.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)

    # Create emergency_contacts table
    op.create_table('emergency_contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=50), nullable=False),
        sa.Column('last_name', sa.String(length=50), nullable=False),
        sa.Column('middle_name', sa.String(length=50), nullable=True),
        sa.Column('relationship', sa.Enum('SPOUSE', 'CHILD', 'PARENT', 'SIBLING', 'GRANDCHILD', 'GRANDPARENT', 'AUNT_UNCLE', 'COUSIN', 'FRIEND', 'NEIGHBOR', 'CAREGIVER', 'LEGAL_GUARDIAN', 'POWER_OF_ATTORNEY', 'HEALTHCARE_PROXY', 'OTHER', name='relationshiptype'), nullable=False),
        sa.Column('relationship_description', sa.String(length=100), nullable=True),
        sa.Column('primary_phone', sa.String(length=20), nullable=False),
        sa.Column('secondary_phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('address_line1', sa.String(length=200), nullable=True),
        sa.Column('address_line2', sa.String(length=200), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('zip_code', sa.String(length=10), nullable=True),
        sa.Column('country', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.Enum('PRIMARY', 'SECONDARY', 'TERTIARY', 'BACKUP', name='contactpriority'), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'UNAVAILABLE', 'DECEASED', name='contactstatus'), nullable=True),
        sa.Column('preferred_contact_method', sa.String(length=20), nullable=True),
        sa.Column('best_time_to_call', sa.String(length=100), nullable=True),
        sa.Column('time_zone', sa.String(length=50), nullable=True),
        sa.Column('is_authorized_for_medical_info', sa.Boolean(), nullable=True),
        sa.Column('is_healthcare_proxy', sa.Boolean(), nullable=True),
        sa.Column('is_power_of_attorney', sa.Boolean(), nullable=True),
        sa.Column('is_legal_guardian', sa.Boolean(), nullable=True),
        sa.Column('can_make_medical_decisions', sa.Boolean(), nullable=True),
        sa.Column('should_contact_in_emergency', sa.Boolean(), nullable=True),
        sa.Column('can_pick_up_patient', sa.Boolean(), nullable=True),
        sa.Column('has_key_to_home', sa.Boolean(), nullable=True),
        sa.Column('lives_with_patient', sa.Boolean(), nullable=True),
        sa.Column('employer', sa.String(length=100), nullable=True),
        sa.Column('work_phone', sa.String(length=20), nullable=True),
        sa.Column('work_address', sa.Text(), nullable=True),
        sa.Column('languages_spoken', sa.String(length=200), nullable=True),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.Column('medical_conditions', sa.Text(), nullable=True),
        sa.Column('last_contacted', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_contact_successful', sa.Boolean(), nullable=True),
        sa.Column('contact_attempts', sa.Integer(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verification_method', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_emergency_contacts_id'), 'emergency_contacts', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_emergency_contacts_id'), table_name='emergency_contacts')
    op.drop_table('emergency_contacts')
    
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    
    op.drop_index(op.f('ix_medications_name'), table_name='medications')
    op.drop_index(op.f('ix_medications_id'), table_name='medications')
    op.drop_table('medications')
    
    op.drop_index(op.f('ix_prescriptions_prescription_number'), table_name='prescriptions')
    op.drop_index(op.f('ix_prescriptions_id'), table_name='prescriptions')
    op.drop_table('prescriptions')
    
    op.drop_index(op.f('ix_appointments_id'), table_name='appointments')
    op.drop_table('appointments')
    
    op.drop_index(op.f('ix_health_records_id'), table_name='health_records')
    op.drop_table('health_records')
    
    op.drop_index(op.f('ix_patients_patient_id'), table_name='patients')
    op.drop_index(op.f('ix_patients_id'), table_name='patients')
    op.drop_table('patients')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')