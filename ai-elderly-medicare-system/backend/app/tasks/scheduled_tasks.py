"""
Scheduled background tasks for routine system operations
"""

from celery import current_task
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta, time, date

from app.tasks.celery_app import celery_app
from app.database import get_db_context, DatabaseManager
from app.models.medication import Medication, MedicationStatus
from app.models.appointment import Appointment, AppointmentStatus
from app.models.notification import Notification, NotificationStatus, NotificationType
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.models.health_record import HealthRecord
from app.models.prescription import Prescription, PrescriptionStatus
from app.tasks.email_tasks import send_medication_reminder_email, send_appointment_reminder_email
from app.tasks.notification_tasks import create_medication_reminder_notifications

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='send_medication_reminders')
def send_medication_reminders(self):
    """Send medication reminders for due doses"""
    try:
        with get_db_context() as db:
            now = datetime.now()
            
            # Get active medications that are due for a dose
            active_medications = db.query(Medication).filter(
                Medication.status == MedicationStatus.ACTIVE,
                Medication.patient_id.isnot(None)
            ).all()
            
            reminders_sent = 0
            
            for medication in active_medications:
                try:
                    # Check if it's time for a dose
                    if medication.is_time_for_dose():
                        # Get patient information
                        patient = medication.patient
                        if not patient or not patient.user:
                            continue
                        
                        # Create reminder notification
                        notification = Notification.create_medication_reminder(
                            user_id=patient.user_id,
                            medication_id=medication.id
                        )
                        
                        notification.message = f"Time to take your {medication.name}"
                        if medication.dosage_amount and medication.dosage_unit:
                            notification.message += f" ({medication.dosage_amount} {medication.dosage_unit})"
                        
                        notification.patient_id = patient.id
                        
                        db.add(notification)
                        db.flush()
                        
                        # Send email reminder
                        send_medication_reminder_email.delay(
                            patient.id,
                            medication.name,
                            f"{medication.dosage_amount} {medication.dosage_unit}" if medication.dosage_amount else "As prescribed",
                            now.strftime("%H:%M")
                        )
                        
                        reminders_sent += 1
                        
                except Exception as e:
                    logger.error(f'Failed to send reminder for medication {medication.id}: {e}')
            
            db.commit()
            
            logger.info(f'Sent {reminders_sent} medication reminders')
            
            return {
                'status': 'completed',
                'reminders_sent': reminders_sent,
                'timestamp': now.isoformat()
            }
            
    except Exception as e:
        logger.error(f'Send medication reminders task failed: {e}')
        raise self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True, name='send_appointment_reminders')
def send_appointment_reminders(self):
    """Send appointment reminders for upcoming appointments"""
    try:
        with get_db_context() as db:
            now = datetime.now()
            
            # Get appointments in the next 24 hours that haven't been reminded
            tomorrow = now + timedelta(days=1)
            
            upcoming_appointments = db.query(Appointment).filter(
                Appointment.appointment_date >= now,
                Appointment.appointment_date <= tomorrow,
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
                Appointment.reminder_sent == False
            ).all()
            
            reminders_sent = 0
            
            for appointment in upcoming_appointments:
                try:
                    patient = appointment.patient
                    provider = appointment.provider
                    
                    if not patient or not patient.user or not provider:
                        continue
                    
                    # Create reminder notification
                    notification = Notification.create_appointment_reminder(
                        user_id=patient.user_id,
                        appointment_id=appointment.id,
                        hours_before=24
                    )
                    
                    notification.patient_id = patient.id
                    
                    db.add(notification)
                    
                    # Prepare appointment details
                    appointment_details = {
                        'date': appointment.appointment_date.strftime('%Y-%m-%d'),
                        'time': appointment.appointment_date.strftime('%H:%M'),
                        'provider': provider.full_name,
                        'location': appointment.location or 'TBD',
                        'type': appointment.appointment_type.value.replace('_', ' ').title()
                    }
                    
                    # Send email reminder
                    send_appointment_reminder_email.delay(
                        patient.id,
                        appointment_details
                    )
                    
                    # Mark reminder as sent
                    appointment.reminder_sent = True
                    
                    reminders_sent += 1
                    
                except Exception as e:
                    logger.error(f'Failed to send reminder for appointment {appointment.id}: {e}')
            
            db.commit()
            
            logger.info(f'Sent {reminders_sent} appointment reminders')
            
            return {
                'status': 'completed',
                'reminders_sent': reminders_sent,
                'timestamp': now.isoformat()
            }
            
    except Exception as e:
        logger.error(f'Send appointment reminders task failed: {e}')
        raise self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True, name='check_health_alerts')
def check_health_alerts(self):
    """Check for health alerts based on patient data"""
    try:
        with get_db_context() as db:
            alerts_created = 0
            
            # Get recent health records that might need alerts
            recent_cutoff = datetime.now() - timedelta(hours=2)
            
            recent_records = db.query(HealthRecord).filter(
                HealthRecord.recorded_at >= recent_cutoff,
                HealthRecord.anomaly_detected == False  # Not already processed
            ).all()
            
            for record in recent_records:
                try:
                    patient = record.patient
                    if not patient or not patient.user:
                        continue
                    
                    alerts = []
                    
                    # Check for critical vital signs
                    if record.is_critical:
                        alerts.append({
                            'type': 'critical_vitals',
                            'message': f'Critical vital signs detected: {record.vital_signs_summary}',
                            'priority': 'critical'
                        })
                    
                    # Check blood pressure
                    if record.systolic_bp and record.diastolic_bp:
                        if record.systolic_bp > 180 or record.diastolic_bp > 120:
                            alerts.append({
                                'type': 'hypertensive_crisis',
                                'message': f'Hypertensive crisis detected: {record.systolic_bp}/{record.diastolic_bp} mmHg',
                                'priority': 'critical'
                            })
                        elif record.systolic_bp > 160 or record.diastolic_bp > 100:
                            alerts.append({
                                'type': 'severe_hypertension',
                                'message': f'Severe hypertension: {record.systolic_bp}/{record.diastolic_bp} mmHg',
                                'priority': 'high'
                            })
                    
                    # Check heart rate
                    if record.heart_rate:
                        if record.heart_rate > 120:
                            alerts.append({
                                'type': 'tachycardia',
                                'message': f'Elevated heart rate: {record.heart_rate} bpm',
                                'priority': 'high'
                            })
                        elif record.heart_rate < 50:
                            alerts.append({
                                'type': 'bradycardia',
                                'message': f'Low heart rate: {record.heart_rate} bpm',
                                'priority': 'high'
                            })
                    
                    # Check oxygen saturation
                    if record.oxygen_saturation and record.oxygen_saturation < 90:
                        alerts.append({
                            'type': 'hypoxemia',
                            'message': f'Low oxygen saturation: {record.oxygen_saturation}%',
                            'priority': 'critical'
                        })
                    
                    # Check blood sugar
                    if record.blood_sugar:
                        if record.blood_sugar > 400:
                            alerts.append({
                                'type': 'severe_hyperglycemia',
                                'message': f'Severe high blood sugar: {record.blood_sugar} mg/dL',
                                'priority': 'critical'
                            })
                        elif record.blood_sugar < 70:
                            alerts.append({
                                'type': 'hypoglycemia',
                                'message': f'Low blood sugar: {record.blood_sugar} mg/dL',
                                'priority': 'high'
                            })
                    
                    # Create notifications for alerts
                    for alert in alerts:
                        notification = Notification.create_health_alert(
                            user_id=patient.user_id,
                            patient_id=patient.id,
                            alert_message=alert['message'],
                            priority=getattr(NotificationPriority, alert['priority'].upper())
                        )
                        
                        db.add(notification)
                        alerts_created += 1
                        
                        # Also notify healthcare providers
                        if patient.primary_physician:
                            provider_notification = Notification.create_health_alert(
                                user_id=patient.primary_physician.id,
                                patient_id=patient.id,
                                alert_message=f"Patient {patient.user.full_name}: {alert['message']}",
                                priority=getattr(NotificationPriority, alert['priority'].upper())
                            )
                            db.add(provider_notification)
                            alerts_created += 1
                    
                    # Mark record as processed
                    record.anomaly_detected = len(alerts) > 0
                    
                except Exception as e:
                    logger.error(f'Failed to process health record {record.id}: {e}')
            
            db.commit()
            
            logger.info(f'Created {alerts_created} health alerts')
            
            return {
                'status': 'completed',
                'alerts_created': alerts_created,
                'records_processed': len(recent_records)
            }
            
    except Exception as e:
        logger.error(f'Check health alerts task failed: {e}')
        raise self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True, name='process_delivery_updates')
def process_delivery_updates(self):
    """Process delivery status updates"""
    try:
        # This would integrate with delivery service APIs
        # For now, it's a placeholder
        
        logger.info('Processing delivery updates...')
        
        return {
            'status': 'completed',
            'updates_processed': 0,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f'Process delivery updates task failed: {e}')
        raise self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True, name='generate_daily_reports')
def generate_daily_reports(self):
    """Generate daily system reports"""
    try:
        with get_db_context() as db:
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            # Generate statistics
            stats = {
                'date': today.isoformat(),
                'patients': {
                    'total': db.query(Patient).count(),
                    'active': db.query(Patient).filter(Patient.is_active_patient == True).count()
                },
                'appointments': {
                    'scheduled_today': db.query(Appointment).filter(
                        Appointment.appointment_date >= datetime.combine(today, time.min),
                        Appointment.appointment_date < datetime.combine(today + timedelta(days=1), time.min)
                    ).count(),
                    'completed_yesterday': db.query(Appointment).filter(
                        Appointment.appointment_date >= datetime.combine(yesterday, time.min),
                        Appointment.appointment_date < datetime.combine(today, time.min),
                        Appointment.status == AppointmentStatus.COMPLETED
                    ).count()
                },
                'medications': {
                    'active': db.query(Medication).filter(Medication.status == MedicationStatus.ACTIVE).count(),
                    'due_for_refill': db.query(Medication).filter(
                        Medication.status == MedicationStatus.ACTIVE,
                        Medication.next_refill_due <= datetime.now()
                    ).count()
                },
                'notifications': {
                    'sent_yesterday': db.query(Notification).filter(
                        Notification.sent_at >= datetime.combine(yesterday, time.min),
                        Notification.sent_at < datetime.combine(today, time.min)
                    ).count(),
                    'pending': db.query(Notification).filter(
                        Notification.status == NotificationStatus.PENDING
                    ).count()
                }
            }
            
            # Send report to administrators
            admin_users = db.query(User).filter(User.role == UserRole.ADMIN).all()
            
            for admin in admin_users:
                try:
                    from app.tasks.email_tasks import send_daily_summary_email
                    send_daily_summary_email.delay(admin.id, stats)
                except Exception as e:
                    logger.error(f'Failed to send daily report to admin {admin.id}: {e}')
            
            logger.info(f'Generated daily reports: {stats}')
            
            return {
                'status': 'completed',
                'stats': stats,
                'admins_notified': len(admin_users)
            }
            
    except Exception as e:
        logger.error(f'Generate daily reports task failed: {e}')
        raise self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True, name='cleanup_expired_notifications')
def cleanup_expired_notifications(self):
    """Clean up expired notifications"""
    try:
        with get_db_context() as db:
            now = datetime.now()
            
            # Mark expired notifications as cancelled
            expired_count = db.query(Notification).filter(
                Notification.expires_at < now,
                Notification.status == NotificationStatus.PENDING
            ).update({
                'status': NotificationStatus.CANCELLED
            })
            
            # Delete old read notifications (older than 30 days)
            old_cutoff = now - timedelta(days=30)
            deleted_count = db.query(Notification).filter(
                Notification.created_at < old_cutoff,
                Notification.is_read == True
            ).delete()
            
            db.commit()
            
            logger.info(f'Cleaned up notifications: {expired_count} expired, {deleted_count} deleted')
            
            return {
                'status': 'completed',
                'expired_count': expired_count,
                'deleted_count': deleted_count
            }
            
    except Exception as e:
        logger.error(f'Cleanup expired notifications task failed: {e}')
        raise self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True, name='update_medication_adherence_scores')
def update_medication_adherence_scores(self):
    """Update medication adherence scores for all active medications"""
    try:
        with get_db_context() as db:
            active_medications = db.query(Medication).filter(
                Medication.status == MedicationStatus.ACTIVE
            ).all()
            
            updated_count = 0
            
            for medication in active_medications:
                try:
                    medication.update_adherence_score()
                    updated_count += 1
                except Exception as e:
                    logger.error(f'Failed to update adherence for medication {medication.id}: {e}')
            
            db.commit()
            
            logger.info(f'Updated adherence scores for {updated_count} medications')
            
            return {
                'status': 'completed',
                'updated_count': updated_count
            }
            
    except Exception as e:
        logger.error(f'Update medication adherence task failed: {e}')
        raise self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True, name='check_prescription_refills')
def check_prescription_refills(self):
    """Check for prescriptions that need refills"""
    try:
        with get_db_context() as db:
            now = datetime.now()
            
            # Get prescriptions due for refill
            due_prescriptions = db.query(Prescription).filter(
                Prescription.status == PrescriptionStatus.ACTIVE,
                Prescription.refills_remaining > 0,
                Prescription.next_fill_date <= now
            ).all()
            
            notifications_created = 0
            
            for prescription in due_prescriptions:
                try:
                    patient = prescription.patient
                    if not patient or not patient.user:
                        continue
                    
                    # Create refill reminder notification
                    notification = Notification(
                        user_id=patient.user_id,
                        title="Prescription Refill Due",
                        message=f"Your prescription for {prescription.medication_name} is due for refill",
                        notification_type=NotificationType.REFILL_REMINDER,
                        priority=NotificationPriority.MEDIUM,
                        patient_id=patient.id
                    )
                    
                    db.add(notification)
                    notifications_created += 1
                    
                except Exception as e:
                    logger.error(f'Failed to create refill reminder for prescription {prescription.id}: {e}')
            
            db.commit()
            
            logger.info(f'Created {notifications_created} prescription refill reminders')
            
            return {
                'status': 'completed',
                'notifications_created': notifications_created,
                'prescriptions_checked': len(due_prescriptions)
            }
            
    except Exception as e:
        logger.error(f'Check prescription refills task failed: {e}')
        raise self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True, name='backup_database')
def backup_database(self):
    """Create database backup"""
    try:
        db_manager = DatabaseManager()
        backup_path = db_manager.backup_database()
        
        logger.info(f'Database backup created: {backup_path}')
        
        return {
            'status': 'completed',
            'backup_path': backup_path,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f'Database backup task failed: {e}')
        raise self.retry(exc=e, countdown=600, max_retries=1)

@celery_app.task(bind=True, name='generate_weekly_reports')
def generate_weekly_reports(self):
    """Generate weekly system reports"""
    try:
        with get_db_context() as db:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())  # Monday
            week_end = week_start + timedelta(days=6)  # Sunday
            
            # Generate weekly statistics
            stats = {
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'appointments': {
                    'total': db.query(Appointment).filter(
                        Appointment.appointment_date >= datetime.combine(week_start, time.min),
                        Appointment.appointment_date <= datetime.combine(week_end, time.max)
                    ).count(),
                    'completed': db.query(Appointment).filter(
                        Appointment.appointment_date >= datetime.combine(week_start, time.min),
                        Appointment.appointment_date <= datetime.combine(week_end, time.max),
                        Appointment.status == AppointmentStatus.COMPLETED
                    ).count()
                },
                'health_records': db.query(HealthRecord).filter(
                    HealthRecord.recorded_at >= datetime.combine(week_start, time.min),
                    HealthRecord.recorded_at <= datetime.combine(week_end, time.max)
                ).count(),
                'notifications_sent': db.query(Notification).filter(
                    Notification.sent_at >= datetime.combine(week_start, time.min),
                    Notification.sent_at <= datetime.combine(week_end, time.max)
                ).count()
            }
            
            # Send to administrators
            admin_users = db.query(User).filter(User.role == UserRole.ADMIN).all()
            
            for admin in admin_users:
                try:
                    from app.tasks.email_tasks import send_email
                    
                    subject = f"Weekly Report - {week_start} to {week_end}"
                    body = f"""
Weekly System Report

Period: {week_start} to {week_end}

Appointments:
- Total: {stats['appointments']['total']}
- Completed: {stats['appointments']['completed']}

Health Records: {stats['health_records']}
Notifications Sent: {stats['notifications_sent']}

Best regards,
AI Medicare System
                    """.strip()
                    
                    send_email.delay(admin.email, subject, body)
                    
                except Exception as e:
                    logger.error(f'Failed to send weekly report to admin {admin.id}: {e}')
            
            logger.info(f'Generated weekly reports: {stats}')
            
            return {
                'status': 'completed',
                'stats': stats,
                'admins_notified': len(admin_users)
            }
            
    except Exception as e:
        logger.error(f'Generate weekly reports task failed: {e}')
        raise self.retry(exc=e, countdown=300, max_retries=2)