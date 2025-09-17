"""
Notification-related background tasks
"""

from celery import current_task
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from app.tasks.celery_app import celery_app
from app.database import get_db_context
from app.models.notification import Notification, NotificationStatus, NotificationChannel, NotificationPriority
from app.models.user import User
from app.models.patient import Patient
from app.services.email_service import EmailService
from app.services.sms_service import SMSService

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='send_notification')
def send_notification(self, notification_id: int):
    """Send a single notification via appropriate channel"""
    try:
        with get_db_context() as db:
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            
            if not notification:
                logger.error(f'Notification not found: {notification_id}')
                return {'status': 'failed', 'error': 'Notification not found'}
            
            if notification.status != NotificationStatus.PENDING:
                logger.warning(f'Notification {notification_id} is not pending (status: {notification.status})')
                return {'status': 'skipped', 'reason': f'Status is {notification.status}'}
            
            # Check if notification has expired
            if notification.expires_at and datetime.utcnow() > notification.expires_at:
                notification.status = NotificationStatus.CANCELLED
                db.commit()
                logger.info(f'Notification {notification_id} expired')
                return {'status': 'expired'}
            
            # Send via appropriate channel
            success = False
            error_message = None
            
            if notification.channel == NotificationChannel.EMAIL:
                success, error_message = send_email_notification(notification)
            elif notification.channel == NotificationChannel.SMS:
                success, error_message = send_sms_notification(notification)
            elif notification.channel == NotificationChannel.PUSH:
                success, error_message = send_push_notification(notification)
            elif notification.channel == NotificationChannel.IN_APP:
                success = True  # In-app notifications are already stored in DB
            else:
                error_message = f'Unsupported notification channel: {notification.channel}'
            
            # Update notification status
            if success:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
                logger.info(f'Notification {notification_id} sent successfully via {notification.channel}')
            else:
                notification.mark_as_failed(error_message)
                logger.error(f'Failed to send notification {notification_id}: {error_message}')
            
            db.commit()
            
            return {
                'status': 'success' if success else 'failed',
                'notification_id': notification_id,
                'channel': notification.channel.value,
                'error': error_message if not success else None
            }
            
    except Exception as e:
        logger.error(f'Notification task failed: {e}')
        raise self.retry(exc=e, countdown=60, max_retries=3)

def send_email_notification(notification: Notification) -> tuple[bool, Optional[str]]:
    """Send notification via email"""
    try:
        if not notification.user or not notification.user.email:
            return False, "User email not found"
        
        email_service = EmailService()
        
        # Create email content
        subject = notification.title
        body = notification.message
        
        # Add action button if available
        if notification.action_url and notification.action_text:
            body += f"\n\n{notification.action_text}: {notification.action_url}"
        
        success = email_service.send_email(
            notification.user.email,
            subject,
            body
        )
        
        return success, None if success else "Failed to send email"
        
    except Exception as e:
        return False, str(e)

def send_sms_notification(notification: Notification) -> tuple[bool, Optional[str]]:
    """Send notification via SMS"""
    try:
        if not notification.user or not notification.user.phone_number:
            return False, "User phone number not found"
        
        sms_service = SMSService()
        
        # Create SMS content (keep it short)
        message = f"{notification.title}: {notification.message}"
        if len(message) > 160:
            message = message[:157] + "..."
        
        success = sms_service.send_sms(
            notification.user.phone_number,
            message
        )
        
        return success, None if success else "Failed to send SMS"
        
    except Exception as e:
        return False, str(e)

def send_push_notification(notification: Notification) -> tuple[bool, Optional[str]]:
    """Send push notification"""
    try:
        # Placeholder for push notification implementation
        # This would integrate with services like Firebase Cloud Messaging
        logger.info(f'Push notification would be sent: {notification.title}')
        return True, None
        
    except Exception as e:
        return False, str(e)

@celery_app.task(bind=True, name='process_notification_queue')
def process_notification_queue(self, batch_size: int = 100):
    """Process pending notifications in batches"""
    try:
        with get_db_context() as db:
            # Get pending notifications that are ready to be sent
            now = datetime.utcnow()
            
            pending_notifications = db.query(Notification).filter(
                Notification.status == NotificationStatus.PENDING,
                (Notification.scheduled_for.is_(None)) | (Notification.scheduled_for <= now),
                (Notification.expires_at.is_(None)) | (Notification.expires_at > now)
            ).limit(batch_size).all()
            
            processed = 0
            failed = 0
            
            for notification in pending_notifications:
                try:
                    # Queue notification for sending
                    send_notification.delay(notification.id)
                    processed += 1
                    
                except Exception as e:
                    logger.error(f'Failed to queue notification {notification.id}: {e}')
                    failed += 1
            
            logger.info(f'Notification queue processed: {processed} queued, {failed} failed')
            
            return {
                'status': 'completed',
                'processed': processed,
                'failed': failed,
                'batch_size': batch_size
            }
            
    except Exception as e:
        logger.error(f'Notification queue processing failed: {e}')
        raise self.retry(exc=e, countdown=120, max_retries=2)

@celery_app.task(bind=True, name='retry_failed_notifications')
def retry_failed_notifications(self):
    """Retry failed notifications that can be retried"""
    try:
        with get_db_context() as db:
            now = datetime.utcnow()
            
            # Get failed notifications that can be retried
            failed_notifications = db.query(Notification).filter(
                Notification.status == NotificationStatus.FAILED,
                Notification.retry_count < Notification.max_retries,
                (Notification.next_retry_at.is_(None)) | (Notification.next_retry_at <= now),
                (Notification.expires_at.is_(None)) | (Notification.expires_at > now)
            ).limit(50).all()
            
            retried = 0
            
            for notification in failed_notifications:
                try:
                    # Reset status to pending for retry
                    notification.status = NotificationStatus.PENDING
                    notification.next_retry_at = None
                    db.commit()
                    
                    # Queue for sending
                    send_notification.delay(notification.id)
                    retried += 1
                    
                except Exception as e:
                    logger.error(f'Failed to retry notification {notification.id}: {e}')
            
            logger.info(f'Retried {retried} failed notifications')
            
            return {
                'status': 'completed',
                'retried': retried
            }
            
    except Exception as e:
        logger.error(f'Retry failed notifications task failed: {e}')
        raise self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True, name='create_medication_reminder_notifications')
def create_medication_reminder_notifications(self, patient_id: int, medication_name: str, 
                                           dosage: str, scheduled_times: List[str]):
    """Create medication reminder notifications for a patient"""
    try:
        with get_db_context() as db:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            
            if not patient or not patient.user:
                logger.error(f'Patient not found: {patient_id}')
                return {'status': 'failed', 'error': 'Patient not found'}
            
            created_notifications = []
            
            for time_str in scheduled_times:
                try:
                    # Parse time and create notification for today and future days
                    from datetime import datetime, time
                    
                    hour, minute = map(int, time_str.split(':'))
                    reminder_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    # If time has passed today, schedule for tomorrow
                    if reminder_time <= datetime.now():
                        reminder_time += timedelta(days=1)
                    
                    # Create notification
                    notification = Notification.create_medication_reminder(
                        user_id=patient.user_id,
                        medication_id=None,  # Would be set if we have medication ID
                        scheduled_for=reminder_time
                    )
                    
                    notification.message = f"Time to take your {medication_name} ({dosage})"
                    notification.patient_id = patient_id
                    
                    db.add(notification)
                    created_notifications.append(notification.id)
                    
                except Exception as e:
                    logger.error(f'Failed to create reminder for time {time_str}: {e}')
            
            db.commit()
            
            logger.info(f'Created {len(created_notifications)} medication reminders for patient {patient_id}')
            
            return {
                'status': 'success',
                'patient_id': patient_id,
                'notifications_created': len(created_notifications),
                'notification_ids': created_notifications
            }
            
    except Exception as e:
        logger.error(f'Create medication reminders task failed: {e}')
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='send_bulk_notifications')
def send_bulk_notifications(self, user_ids: List[int], title: str, message: str, 
                          notification_type: str, priority: str = "medium", 
                          channel: str = "in_app"):
    """Send bulk notifications to multiple users"""
    try:
        from app.models.notification import NotificationType, NotificationPriority, NotificationChannel
        
        # Convert string enums
        try:
            notif_type = NotificationType(notification_type)
            notif_priority = NotificationPriority(priority)
            notif_channel = NotificationChannel(channel)
        except ValueError as e:
            logger.error(f'Invalid enum value: {e}')
            return {'status': 'failed', 'error': str(e)}
        
        created_notifications = []
        failed_users = []
        
        with get_db_context() as db:
            for user_id in user_ids:
                try:
                    # Verify user exists
                    user = db.query(User).filter(User.id == user_id).first()
                    if not user:
                        failed_users.append(user_id)
                        continue
                    
                    # Create notification
                    notification = Notification(
                        user_id=user_id,
                        title=title,
                        message=message,
                        notification_type=notif_type,
                        priority=notif_priority,
                        channel=notif_channel,
                        scheduled_for=datetime.utcnow()
                    )
                    
                    db.add(notification)
                    db.flush()  # Get the ID
                    
                    created_notifications.append(notification.id)
                    
                except Exception as e:
                    logger.error(f'Failed to create notification for user {user_id}: {e}')
                    failed_users.append(user_id)
            
            db.commit()
        
        # Queue notifications for sending
        for notification_id in created_notifications:
            try:
                send_notification.delay(notification_id)
            except Exception as e:
                logger.error(f'Failed to queue notification {notification_id}: {e}')
        
        logger.info(f'Bulk notifications: {len(created_notifications)} created, {len(failed_users)} failed')
        
        return {
            'status': 'completed',
            'total_users': len(user_ids),
            'notifications_created': len(created_notifications),
            'failed_users': len(failed_users),
            'notification_ids': created_notifications
        }
        
    except Exception as e:
        logger.error(f'Bulk notifications task failed: {e}')
        raise self.retry(exc=e, countdown=120, max_retries=2)

@celery_app.task(bind=True, name='cleanup_old_notifications')
def cleanup_old_notifications(self, days_old: int = 90):
    """Clean up old notifications"""
    try:
        with get_db_context() as db:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Delete old notifications that are read or expired
            deleted_count = db.query(Notification).filter(
                Notification.created_at < cutoff_date,
                (Notification.is_read == True) | 
                (Notification.expires_at < datetime.utcnow())
            ).delete()
            
            db.commit()
            
            logger.info(f'Cleaned up {deleted_count} old notifications')
            
            return {
                'status': 'completed',
                'deleted_count': deleted_count,
                'cutoff_date': cutoff_date.isoformat()
            }
            
    except Exception as e:
        logger.error(f'Cleanup old notifications task failed: {e}')
        raise self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True, name='send_notification_digest')
def send_notification_digest(self, user_id: int, digest_type: str = "daily"):
    """Send notification digest to user"""
    try:
        with get_db_context() as db:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.error(f'User not found for digest: {user_id}')
                return {'status': 'failed', 'error': 'User not found'}
            
            # Calculate time range for digest
            now = datetime.utcnow()
            if digest_type == "daily":
                start_time = now - timedelta(days=1)
            elif digest_type == "weekly":
                start_time = now - timedelta(days=7)
            else:
                start_time = now - timedelta(days=1)
            
            # Get unread notifications in time range
            notifications = db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.created_at >= start_time,
                Notification.is_read == False,
                Notification.status.in_([NotificationStatus.SENT, NotificationStatus.DELIVERED])
            ).order_by(Notification.priority.desc(), Notification.created_at.desc()).all()
            
            if not notifications:
                logger.info(f'No unread notifications for user {user_id} digest')
                return {'status': 'no_notifications'}
            
            # Group notifications by type
            grouped_notifications = {}
            for notification in notifications:
                notif_type = notification.notification_type.value
                if notif_type not in grouped_notifications:
                    grouped_notifications[notif_type] = []
                grouped_notifications[notif_type].append(notification)
            
            # Create digest content
            digest_title = f"{digest_type.title()} Notification Digest"
            digest_content = f"Hello {user.first_name},\n\nHere's your {digest_type} notification summary:\n\n"
            
            for notif_type, notifs in grouped_notifications.items():
                digest_content += f"{notif_type.replace('_', ' ').title()} ({len(notifs)}):\n"
                for notif in notifs[:5]:  # Limit to 5 per type
                    digest_content += f"- {notif.title}\n"
                if len(notifs) > 5:
                    digest_content += f"... and {len(notifs) - 5} more\n"
                digest_content += "\n"
            
            digest_content += "Please log in to view all your notifications.\n\nBest regards,\nAI Medicare System"
            
            # Send digest email
            email_service = EmailService()
            success = email_service.send_email(
                user.email,
                digest_title,
                digest_content
            )
            
            if success:
                logger.info(f'Notification digest sent to user {user_id}')
                return {
                    'status': 'success',
                    'user_id': user_id,
                    'digest_type': digest_type,
                    'notification_count': len(notifications)
                }
            else:
                raise Exception('Failed to send digest email')
                
    except Exception as e:
        logger.error(f'Send notification digest task failed: {e}')
        raise self.retry(exc=e, countdown=300, max_retries=2)

@celery_app.task(bind=True, name='update_notification_delivery_status')
def update_notification_delivery_status(self, notification_id: int, status: str, 
                                       delivery_info: Dict[str, Any] = None):
    """Update notification delivery status from external services"""
    try:
        with get_db_context() as db:
            notification = db.query(Notification).filter(Notification.id == notification_id).first()
            
            if not notification:
                logger.error(f'Notification not found for status update: {notification_id}')
                return {'status': 'failed', 'error': 'Notification not found'}
            
            # Update status based on delivery info
            if status == 'delivered':
                notification.status = NotificationStatus.DELIVERED
                notification.delivered_at = datetime.utcnow()
            elif status == 'read':
                notification.status = NotificationStatus.READ
                notification.read_at = datetime.utcnow()
                notification.is_read = True
            elif status == 'failed':
                notification.status = NotificationStatus.FAILED
                notification.failed_at = datetime.utcnow()
                if delivery_info and 'error' in delivery_info:
                    notification.failure_reason = delivery_info['error']
            
            # Store additional delivery info in metadata
            if delivery_info:
                if not notification.metadata:
                    notification.metadata = {}
                notification.metadata['delivery_info'] = delivery_info
            
            db.commit()
            
            logger.info(f'Updated notification {notification_id} status to {status}')
            
            return {
                'status': 'success',
                'notification_id': notification_id,
                'new_status': status
            }
            
    except Exception as e:
        logger.error(f'Update notification status task failed: {e}')
        return {'status': 'failed', 'error': str(e)}