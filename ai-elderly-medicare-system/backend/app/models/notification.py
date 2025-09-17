"""
Notification model for system alerts and communications
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.database import Base

class NotificationType(enum.Enum):
    """Types of notifications"""
    MEDICATION_REMINDER = "medication_reminder"
    APPOINTMENT_REMINDER = "appointment_reminder"
    HEALTH_ALERT = "health_alert"
    SYSTEM_ALERT = "system_alert"
    DELIVERY_UPDATE = "delivery_update"
    EMERGENCY_ALERT = "emergency_alert"
    CARE_PLAN_UPDATE = "care_plan_update"
    LAB_RESULT = "lab_result"
    PRESCRIPTION_READY = "prescription_ready"
    REFILL_REMINDER = "refill_reminder"
    VITAL_SIGNS_ALERT = "vital_signs_alert"
    AI_RECOMMENDATION = "ai_recommendation"

class NotificationStatus(enum.Enum):
    """Notification status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NotificationPriority(enum.Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class NotificationChannel(enum.Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    PHONE_CALL = "phone_call"
    PORTAL = "portal"

class Notification(Base):
    """Notification model for system communications"""
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Notification Content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    
    # Delivery Information
    channel = Column(Enum(NotificationChannel), default=NotificationChannel.IN_APP)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    
    # Scheduling
    scheduled_for = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    
    # Related Entities
    patient_id = Column(Integer, ForeignKey("patients.id"))
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    medication_id = Column(Integer, ForeignKey("medications.id"))
    health_record_id = Column(Integer, ForeignKey("health_records.id"))
    
    # Metadata
    metadata = Column(JSON)  # Additional notification data
    action_url = Column(String(500))  # URL for notification action
    action_text = Column(String(100))  # Text for action button
    
    # Delivery Tracking
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    failure_reason = Column(Text)
    
    # Retry Logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime(timezone=True))
    
    # Grouping and Threading
    group_id = Column(String(100))  # For grouping related notifications
    thread_id = Column(String(100))  # For threading conversations
    parent_notification_id = Column(Integer, ForeignKey("notifications.id"))
    
    # User Interaction
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    patient = relationship("Patient")
    appointment = relationship("Appointment")
    medication = relationship("Medication")
    health_record = relationship("HealthRecord")
    parent_notification = relationship("Notification", remote_side=[id])
    child_notifications = relationship("Notification", back_populates="parent_notification")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.notification_type.value}', user_id={self.user_id}, status='{self.status.value}')>"
    
    @property
    def is_pending(self):
        """Check if notification is pending"""
        return self.status == NotificationStatus.PENDING
    
    @property
    def is_sent(self):
        """Check if notification has been sent"""
        return self.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED, NotificationStatus.READ]
    
    @property
    def is_overdue(self):
        """Check if scheduled notification is overdue"""
        if self.scheduled_for and self.status == NotificationStatus.PENDING:
            return datetime.now() > self.scheduled_for
        return False
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False
    
    @property
    def can_retry(self):
        """Check if notification can be retried"""
        return (self.status == NotificationStatus.FAILED and 
                self.retry_count < self.max_retries and 
                not self.is_expired)
    
    @property
    def time_until_scheduled(self):
        """Get time remaining until scheduled delivery"""
        if self.scheduled_for:
            delta = self.scheduled_for - datetime.now()
            return delta if delta.total_seconds() > 0 else timedelta(0)
        return timedelta(0)
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.now()
    
    def mark_as_delivered(self):
        """Mark notification as delivered"""
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = datetime.now()
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.status = NotificationStatus.READ
        self.read_at = datetime.now()
        self.is_read = True
    
    def mark_as_failed(self, reason: str = None):
        """Mark notification as failed"""
        self.status = NotificationStatus.FAILED
        self.failed_at = datetime.now()
        self.failure_reason = reason
        self.retry_count += 1
        
        # Schedule retry if possible
        if self.can_retry:
            retry_delay = min(300 * (2 ** self.retry_count), 3600)  # Exponential backoff, max 1 hour
            self.next_retry_at = datetime.now() + timedelta(seconds=retry_delay)
    
    def cancel(self):
        """Cancel notification"""
        self.status = NotificationStatus.CANCELLED
    
    def archive(self):
        """Archive notification"""
        self.is_archived = True
    
    def star(self):
        """Star notification"""
        self.is_starred = True
    
    def unstar(self):
        """Unstar notification"""
        self.is_starred = False
    
    @classmethod
    def create_medication_reminder(cls, user_id: int, medication_id: int, 
                                 scheduled_for: datetime = None):
        """Create medication reminder notification"""
        if not scheduled_for:
            scheduled_for = datetime.now() + timedelta(minutes=5)
        
        return cls(
            user_id=user_id,
            medication_id=medication_id,
            title="Medication Reminder",
            message="It's time to take your medication",
            notification_type=NotificationType.MEDICATION_REMINDER,
            priority=NotificationPriority.HIGH,
            scheduled_for=scheduled_for,
            expires_at=scheduled_for + timedelta(hours=2),
            action_text="Mark as Taken",
            metadata={"reminder_type": "dose"}
        )
    
    @classmethod
    def create_appointment_reminder(cls, user_id: int, appointment_id: int, 
                                  hours_before: int = 24):
        """Create appointment reminder notification"""
        scheduled_for = datetime.now() + timedelta(hours=hours_before)
        
        return cls(
            user_id=user_id,
            appointment_id=appointment_id,
            title="Appointment Reminder",
            message=f"You have an appointment in {hours_before} hours",
            notification_type=NotificationType.APPOINTMENT_REMINDER,
            priority=NotificationPriority.MEDIUM,
            scheduled_for=scheduled_for,
            action_text="View Details"
        )
    
    @classmethod
    def create_health_alert(cls, user_id: int, patient_id: int, 
                          alert_message: str, priority: NotificationPriority = NotificationPriority.HIGH):
        """Create health alert notification"""
        return cls(
            user_id=user_id,
            patient_id=patient_id,
            title="Health Alert",
            message=alert_message,
            notification_type=NotificationType.HEALTH_ALERT,
            priority=priority,
            scheduled_for=datetime.now(),
            action_text="View Details"
        )
    
    @classmethod
    def create_ai_recommendation(cls, user_id: int, patient_id: int, 
                               recommendation: str, confidence_score: float = None):
        """Create AI recommendation notification"""
        metadata = {"ai_generated": True}
        if confidence_score:
            metadata["confidence_score"] = confidence_score
        
        return cls(
            user_id=user_id,
            patient_id=patient_id,
            title="AI Health Recommendation",
            message=recommendation,
            notification_type=NotificationType.AI_RECOMMENDATION,
            priority=NotificationPriority.MEDIUM,
            scheduled_for=datetime.now(),
            metadata=metadata,
            action_text="Review Recommendation"
        )
    
    @classmethod
    def create_emergency_alert(cls, user_id: int, patient_id: int, 
                             emergency_details: str):
        """Create emergency alert notification"""
        return cls(
            user_id=user_id,
            patient_id=patient_id,
            title="EMERGENCY ALERT",
            message=emergency_details,
            notification_type=NotificationType.EMERGENCY_ALERT,
            priority=NotificationPriority.CRITICAL,
            scheduled_for=datetime.now(),
            channel=NotificationChannel.PHONE_CALL,
            action_text="Respond Now"
        )
    
    def get_display_time(self):
        """Get human-readable time for display"""
        now = datetime.now()
        
        if self.sent_at:
            time_ref = self.sent_at
        elif self.created_at:
            time_ref = self.created_at
        else:
            return "Unknown"
        
        delta = now - time_ref
        
        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    def to_dict(self):
        """Convert notification to dictionary for API responses"""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.notification_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "channel": self.channel.value,
            "is_read": self.is_read,
            "is_starred": self.is_starred,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "action_url": self.action_url,
            "action_text": self.action_text,
            "metadata": self.metadata,
            "display_time": self.get_display_time()
        }