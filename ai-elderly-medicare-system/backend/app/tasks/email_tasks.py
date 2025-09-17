"""
Email-related background tasks
"""

from celery import current_task
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.tasks.celery_app import celery_app
from app.services.email_service import EmailService
from app.database import get_db_context
from app.models.user import User
from app.models.patient import Patient
from app.models.notification import Notification, NotificationStatus

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='send_email')
def send_email(self, to_email: str, subject: str, body: str, 
               html_body: Optional[str] = None, attachments: Optional[List[str]] = None):
    """Send a single email"""
    try:
        email_service = EmailService()
        success = email_service.send_email(to_email, subject, body, html_body, attachments)
        
        if success:
            logger.info(f'Email sent successfully to {to_email}')
            return {'status': 'success', 'recipient': to_email}
        else:
            logger.error(f'Failed to send email to {to_email}')
            raise Exception(f'Failed to send email to {to_email}')
            
    except Exception as e:
        logger.error(f'Email task failed: {e}')
        # Retry the task
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='send_bulk_email')
def send_bulk_email(self, recipients: List[str], subject: str, body: str, 
                   html_body: Optional[str] = None):
    """Send bulk email to multiple recipients"""
    try:
        email_service = EmailService()
        results = email_service.send_bulk_email(recipients, subject, body, html_body)
        
        successful = sum(1 for success in results.values() if success)
        failed = len(recipients) - successful
        
        logger.info(f'Bulk email completed: {successful} successful, {failed} failed')
        
        return {
            'status': 'completed',
            'total_recipients': len(recipients),
            'successful': successful,
            'failed': failed,
            'results': results
        }
        
    except Exception as e:
        logger.error(f'Bulk email task failed: {e}')
        raise self.retry(exc=e, countdown=120, max_retries=2)

@celery_app.task(bind=True, name='send_verification_email')
def send_verification_email(self, user_id: int, verification_token: str):
    """Send email verification email to user"""
    try:
        with get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.error(f'User not found for verification email: {user_id}')
                return {'status': 'failed', 'error': 'User not found'}
            
            email_service = EmailService()
            success = email_service.send_verification_email(
                user.email, 
                user.first_name, 
                verification_token
            )
            
            if success:
                logger.info(f'Verification email sent to user {user_id}')
                return {'status': 'success', 'user_id': user_id}
            else:
                raise Exception('Failed to send verification email')
                
    except Exception as e:
        logger.error(f'Verification email task failed: {e}')
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='send_password_reset_email')
def send_password_reset_email(self, user_id: int, reset_token: str):
    """Send password reset email to user"""
    try:
        with get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.error(f'User not found for password reset email: {user_id}')
                return {'status': 'failed', 'error': 'User not found'}
            
            email_service = EmailService()
            success = email_service.send_password_reset_email(
                user.email, 
                user.first_name, 
                reset_token
            )
            
            if success:
                logger.info(f'Password reset email sent to user {user_id}')
                return {'status': 'success', 'user_id': user_id}
            else:
                raise Exception('Failed to send password reset email')
                
    except Exception as e:
        logger.error(f'Password reset email task failed: {e}')
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='send_welcome_email')
def send_welcome_email(self, user_id: int):
    """Send welcome email to new user"""
    try:
        with get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.error(f'User not found for welcome email: {user_id}')
                return {'status': 'failed', 'error': 'User not found'}
            
            email_service = EmailService()
            success = email_service.send_welcome_email(
                user.email, 
                user.first_name, 
                user.role.value
            )
            
            if success:
                logger.info(f'Welcome email sent to user {user_id}')
                return {'status': 'success', 'user_id': user_id}
            else:
                raise Exception('Failed to send welcome email')
                
    except Exception as e:
        logger.error(f'Welcome email task failed: {e}')
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='send_appointment_reminder_email')
def send_appointment_reminder_email(self, patient_id: int, appointment_details: Dict[str, Any]):
    """Send appointment reminder email"""
    try:
        with get_db_context() as db:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            
            if not patient or not patient.user:
                logger.error(f'Patient not found for appointment reminder: {patient_id}')
                return {'status': 'failed', 'error': 'Patient not found'}
            
            email_service = EmailService()
            success = email_service.send_appointment_reminder(
                patient.user.email,
                patient.user.full_name,
                appointment_details
            )
            
            if success:
                logger.info(f'Appointment reminder sent to patient {patient_id}')
                return {'status': 'success', 'patient_id': patient_id}
            else:
                raise Exception('Failed to send appointment reminder')
                
    except Exception as e:
        logger.error(f'Appointment reminder email task failed: {e}')
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='send_medication_reminder_email')
def send_medication_reminder_email(self, patient_id: int, medication_name: str, 
                                 dosage: str, time: str):
    """Send medication reminder email"""
    try:
        with get_db_context() as db:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            
            if not patient or not patient.user:
                logger.error(f'Patient not found for medication reminder: {patient_id}')
                return {'status': 'failed', 'error': 'Patient not found'}
            
            email_service = EmailService()
            success = email_service.send_medication_reminder(
                patient.user.email,
                patient.user.full_name,
                medication_name,
                dosage,
                time
            )
            
            if success:
                logger.info(f'Medication reminder sent to patient {patient_id}')
                return {'status': 'success', 'patient_id': patient_id}
            else:
                raise Exception('Failed to send medication reminder')
                
    except Exception as e:
        logger.error(f'Medication reminder email task failed: {e}')
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='send_health_alert_email')
def send_health_alert_email(self, patient_id: int, alert_message: str, severity: str = "medium"):
    """Send health alert email"""
    try:
        with get_db_context() as db:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            
            if not patient or not patient.user:
                logger.error(f'Patient not found for health alert: {patient_id}')
                return {'status': 'failed', 'error': 'Patient not found'}
            
            email_service = EmailService()
            success = email_service.send_health_alert(
                patient.user.email,
                patient.user.full_name,
                alert_message,
                severity
            )
            
            if success:
                logger.info(f'Health alert sent to patient {patient_id}')
                return {'status': 'success', 'patient_id': patient_id}
            else:
                raise Exception('Failed to send health alert')
                
    except Exception as e:
        logger.error(f'Health alert email task failed: {e}')
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='send_notification_email')
def send_notification_email(self, notification_id: int):
    """Send notification via email"""
    try:
        with get_db_context() as db:
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            
            if not notification:
                logger.error(f'Notification not found: {notification_id}')
                return {'status': 'failed', 'error': 'Notification not found'}
            
            if not notification.user:
                logger.error(f'User not found for notification: {notification_id}')
                return {'status': 'failed', 'error': 'User not found'}
            
            # Create email content
            subject = notification.title
            body = notification.message
            
            # Add action button if available
            if notification.action_url and notification.action_text:
                body += f"\n\n{notification.action_text}: {notification.action_url}"
            
            email_service = EmailService()
            success = email_service.send_email(
                notification.user.email,
                subject,
                body
            )
            
            if success:
                # Update notification status
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
                db.commit()
                
                logger.info(f'Notification email sent: {notification_id}')
                return {'status': 'success', 'notification_id': notification_id}
            else:
                raise Exception('Failed to send notification email')
                
    except Exception as e:
        logger.error(f'Notification email task failed: {e}')
        
        # Update notification status to failed
        try:
            with get_db_context() as db:
                notification = db.query(Notification).filter(Notification.id == notification_id).first()
                if notification:
                    notification.status = NotificationStatus.FAILED
                    notification.failed_at = datetime.utcnow()
                    notification.failure_reason = str(e)
                    db.commit()
        except Exception as update_error:
            logger.error(f'Failed to update notification status: {update_error}')
        
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='send_daily_summary_email')
def send_daily_summary_email(self, user_id: int, summary_data: Dict[str, Any]):
    """Send daily summary email to healthcare providers"""
    try:
        with get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.error(f'User not found for daily summary: {user_id}')
                return {'status': 'failed', 'error': 'User not found'}
            
            # Create summary email content
            subject = f"Daily Summary - {datetime.now().strftime('%Y-%m-%d')}"
            
            body = f"""
Hello {user.first_name},

Here's your daily summary for {datetime.now().strftime('%B %d, %Y')}:

Patients: {summary_data.get('total_patients', 0)}
Appointments Today: {summary_data.get('appointments_today', 0)}
Critical Alerts: {summary_data.get('critical_alerts', 0)}
Medication Reminders Sent: {summary_data.get('medication_reminders', 0)}

Best regards,
AI Medicare System Team
            """.strip()
            
            email_service = EmailService()
            success = email_service.send_email(user.email, subject, body)
            
            if success:
                logger.info(f'Daily summary email sent to user {user_id}')
                return {'status': 'success', 'user_id': user_id}
            else:
                raise Exception('Failed to send daily summary email')
                
    except Exception as e:
        logger.error(f'Daily summary email task failed: {e}')
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='send_system_alert_email')
def send_system_alert_email(self, admin_emails: List[str], alert_type: str, 
                           alert_message: str, severity: str = "medium"):
    """Send system alert email to administrators"""
    try:
        subject = f"System Alert - {alert_type.upper()}"
        
        body = f"""
SYSTEM ALERT - {severity.upper()} PRIORITY

Alert Type: {alert_type}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Message:
{alert_message}

Please investigate and take appropriate action.

AI Medicare System
        """.strip()
        
        email_service = EmailService()
        results = email_service.send_bulk_email(admin_emails, subject, body)
        
        successful = sum(1 for success in results.values() if success)
        
        logger.info(f'System alert sent to {successful}/{len(admin_emails)} administrators')
        
        return {
            'status': 'completed',
            'alert_type': alert_type,
            'recipients': len(admin_emails),
            'successful': successful,
            'results': results
        }
        
    except Exception as e:
        logger.error(f'System alert email task failed: {e}')
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='process_email_queue')
def process_email_queue(self, batch_size: int = 50):
    """Process queued emails in batches"""
    try:
        with get_db_context() as db:
            # Get pending email notifications
            pending_notifications = db.query(Notification).filter(
                Notification.status == NotificationStatus.PENDING,
                Notification.channel == 'email'
            ).limit(batch_size).all()
            
            processed = 0
            failed = 0
            
            for notification in pending_notifications:
                try:
                    # Send notification email
                    result = send_notification_email.delay(notification.id)
                    processed += 1
                    
                except Exception as e:
                    logger.error(f'Failed to queue notification email {notification.id}: {e}')
                    failed += 1
            
            logger.info(f'Email queue processed: {processed} queued, {failed} failed')
            
            return {
                'status': 'completed',
                'processed': processed,
                'failed': failed,
                'batch_size': batch_size
            }
            
    except Exception as e:
        logger.error(f'Email queue processing failed: {e}')
        raise self.retry(exc=e, countdown=120, max_retries=2)