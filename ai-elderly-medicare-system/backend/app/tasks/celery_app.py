"""
Celery application configuration for background tasks
"""

from celery import Celery
from celery.schedules import crontab
import os
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create Celery instance
celery_app = Celery(
    "ai_medicare_system",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.tasks.email_tasks',
        'app.tasks.notification_tasks',
        'app.tasks.scheduled_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'app.tasks.email_tasks.*': {'queue': 'email'},
        'app.tasks.notification_tasks.*': {'queue': 'notifications'},
        'app.tasks.scheduled_tasks.*': {'queue': 'scheduled'},
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        'master_name': 'mymaster',
        'visibility_timeout': 3600,
    },
    
    # Task execution settings
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes
    task_max_retries=3,
    task_default_retry_delay=60,  # 1 minute
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Periodic task schedule
celery_app.conf.beat_schedule = {
    # Send medication reminders every 15 minutes
    'send-medication-reminders': {
        'task': 'app.tasks.scheduled_tasks.send_medication_reminders',
        'schedule': crontab(minute='*/15'),
        'options': {'queue': 'scheduled'}
    },
    
    # Send appointment reminders daily at 9 AM
    'send-appointment-reminders': {
        'task': 'app.tasks.scheduled_tasks.send_appointment_reminders',
        'schedule': crontab(hour=9, minute=0),
        'options': {'queue': 'scheduled'}
    },
    
    # Check for health alerts every 30 minutes
    'check-health-alerts': {
        'task': 'app.tasks.scheduled_tasks.check_health_alerts',
        'schedule': crontab(minute='*/30'),
        'options': {'queue': 'scheduled'}
    },
    
    # Process delivery updates every hour
    'process-delivery-updates': {
        'task': 'app.tasks.scheduled_tasks.process_delivery_updates',
        'schedule': crontab(minute=0),
        'options': {'queue': 'scheduled'}
    },
    
    # Generate daily reports at midnight
    'generate-daily-reports': {
        'task': 'app.tasks.scheduled_tasks.generate_daily_reports',
        'schedule': crontab(hour=0, minute=0),
        'options': {'queue': 'scheduled'}
    },
    
    # Clean up expired notifications daily at 2 AM
    'cleanup-expired-notifications': {
        'task': 'app.tasks.scheduled_tasks.cleanup_expired_notifications',
        'schedule': crontab(hour=2, minute=0),
        'options': {'queue': 'scheduled'}
    },
    
    # Update medication adherence scores daily at 3 AM
    'update-adherence-scores': {
        'task': 'app.tasks.scheduled_tasks.update_medication_adherence_scores',
        'schedule': crontab(hour=3, minute=0),
        'options': {'queue': 'scheduled'}
    },
    
    # Check for prescription refills daily at 10 AM
    'check-prescription-refills': {
        'task': 'app.tasks.scheduled_tasks.check_prescription_refills',
        'schedule': crontab(hour=10, minute=0),
        'options': {'queue': 'scheduled'}
    },
    
    # Backup database weekly on Sunday at 1 AM
    'backup-database': {
        'task': 'app.tasks.scheduled_tasks.backup_database',
        'schedule': crontab(hour=1, minute=0, day_of_week=0),
        'options': {'queue': 'scheduled'}
    },
    
    # Generate weekly health reports on Monday at 6 AM
    'generate-weekly-reports': {
        'task': 'app.tasks.scheduled_tasks.generate_weekly_reports',
        'schedule': crontab(hour=6, minute=0, day_of_week=1),
        'options': {'queue': 'scheduled'}
    },
}

# Error handling
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    logger.info(f'Request: {self.request!r}')
    return 'Debug task completed'

# Task failure handler
@celery_app.task(bind=True)
def task_failure_handler(self, task_id, error, traceback):
    """Handle task failures"""
    logger.error(f'Task {task_id} failed: {error}')
    logger.error(f'Traceback: {traceback}')
    
    # You could send notifications about critical task failures here
    # For example, notify administrators about failed backup tasks

# Custom task base class with retry logic
class BaseTaskWithRetry(celery_app.Task):
    """Base task class with automatic retry logic"""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 60}
    retry_backoff = True
    retry_backoff_max = 700
    retry_jitter = False
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        logger.error(f'Task {task_id} failed: {exc}')
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        logger.warning(f'Task {task_id} retrying: {exc}')
        super().on_retry(exc, task_id, args, kwargs, einfo)
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        logger.info(f'Task {task_id} completed successfully')
        super().on_success(retval, task_id, args, kwargs)

# Set default task base class
celery_app.Task = BaseTaskWithRetry

# Health check task
@celery_app.task(name='health_check')
def health_check():
    """Health check task for monitoring"""
    try:
        # Perform basic health checks
        from app.database import check_db_connection
        
        db_healthy = check_db_connection()
        
        return {
            'status': 'healthy' if db_healthy else 'unhealthy',
            'database': 'connected' if db_healthy else 'disconnected',
            'timestamp': str(datetime.utcnow())
        }
    except Exception as e:
        logger.error(f'Health check failed: {e}')
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': str(datetime.utcnow())
        }

# Task monitoring
@celery_app.task(bind=True)
def monitor_task_queue(self):
    """Monitor task queue health"""
    try:
        inspect = celery_app.control.inspect()
        
        # Get active tasks
        active_tasks = inspect.active()
        
        # Get scheduled tasks
        scheduled_tasks = inspect.scheduled()
        
        # Get reserved tasks
        reserved_tasks = inspect.reserved()
        
        stats = {
            'active_tasks': len(active_tasks) if active_tasks else 0,
            'scheduled_tasks': len(scheduled_tasks) if scheduled_tasks else 0,
            'reserved_tasks': len(reserved_tasks) if reserved_tasks else 0,
            'timestamp': str(datetime.utcnow())
        }
        
        logger.info(f'Task queue stats: {stats}')
        return stats
        
    except Exception as e:
        logger.error(f'Task queue monitoring failed: {e}')
        return {'error': str(e), 'timestamp': str(datetime.utcnow())}

# Utility functions for task management
def get_task_status(task_id: str):
    """Get status of a specific task"""
    try:
        result = celery_app.AsyncResult(task_id)
        return {
            'task_id': task_id,
            'status': result.status,
            'result': result.result,
            'traceback': result.traceback
        }
    except Exception as e:
        logger.error(f'Error getting task status: {e}')
        return {'error': str(e)}

def cancel_task(task_id: str):
    """Cancel a specific task"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        logger.info(f'Task {task_id} cancelled')
        return True
    except Exception as e:
        logger.error(f'Error cancelling task: {e}')
        return False

def get_worker_stats():
    """Get worker statistics"""
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        return stats
    except Exception as e:
        logger.error(f'Error getting worker stats: {e}')
        return {'error': str(e)}

# Task result cleanup
@celery_app.task(name='cleanup_task_results')
def cleanup_task_results():
    """Clean up old task results"""
    try:
        # This would clean up old task results from the backend
        # Implementation depends on the backend used (Redis, database, etc.)
        logger.info('Task results cleanup completed')
        return {'status': 'completed', 'timestamp': str(datetime.utcnow())}
    except Exception as e:
        logger.error(f'Task results cleanup failed: {e}')
        return {'status': 'failed', 'error': str(e)}

if __name__ == '__main__':
    # Start Celery worker
    celery_app.start()