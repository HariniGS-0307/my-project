"""
Delivery model for medication and medical supply deliveries
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.database import Base

class DeliveryStatus(enum.Enum):
    """Delivery status options"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETURNED = "returned"

class DeliveryType(enum.Enum):
    """Types of deliveries"""
    MEDICATION = "medication"
    MEDICAL_SUPPLIES = "medical_supplies"
    EQUIPMENT = "equipment"
    DOCUMENTS = "documents"
    EMERGENCY = "emergency"
    ROUTINE = "routine"

class DeliveryPriority(enum.Enum):
    """Delivery priority levels"""
    STANDARD = "standard"
    EXPEDITED = "expedited"
    URGENT = "urgent"
    EMERGENCY = "emergency"

class Delivery(Base):
    """Delivery model for tracking medication and supply deliveries"""
    
    __tablename__ = "deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    medication_id = Column(Integer, ForeignKey("medications.id"))
    
    # Delivery Information
    delivery_id = Column(String(50), unique=True, index=True, nullable=False)
    delivery_type = Column(Enum(DeliveryType), nullable=False)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    priority = Column(Enum(DeliveryPriority), default=DeliveryPriority.STANDARD)
    
    # Items and Quantities
    items = Column(JSON)  # List of items being delivered
    total_items = Column(Integer, default=1)
    total_weight = Column(Float)  # in kg
    
    # Delivery Details
    description = Column(Text)
    special_instructions = Column(Text)
    requires_signature = Column(Boolean, default=True)
    requires_refrigeration = Column(Boolean, default=False)
    is_controlled_substance = Column(Boolean, default=False)
    
    # Addresses
    pickup_address = Column(Text)
    delivery_address = Column(Text, nullable=False)
    
    # Scheduling
    requested_delivery_date = Column(DateTime(timezone=True))
    estimated_delivery_date = Column(DateTime(timezone=True))
    actual_delivery_date = Column(DateTime(timezone=True))
    delivery_window_start = Column(DateTime(timezone=True))
    delivery_window_end = Column(DateTime(timezone=True))
    
    # Carrier Information
    carrier_name = Column(String(100))
    tracking_number = Column(String(100), index=True)
    carrier_service = Column(String(50))  # e.g., "Next Day", "Ground"
    
    # Cost Information
    delivery_cost = Column(Float)
    insurance_covered = Column(Boolean, default=False)
    copay_amount = Column(Float)
    
    # Delivery Personnel
    driver_name = Column(String(100))
    driver_phone = Column(String(20))
    delivery_notes = Column(Text)
    
    # Recipient Information
    recipient_name = Column(String(100))
    recipient_phone = Column(String(20))
    signature_required = Column(Boolean, default=True)
    signature_obtained = Column(Boolean, default=False)
    signature_data = Column(Text)  # Base64 encoded signature
    
    # Location Tracking
    current_location = Column(String(200))
    gps_coordinates = Column(String(50))  # "lat,lng"
    location_updates = Column(JSON)  # Array of location updates
    
    # Delivery Attempt Tracking
    delivery_attempts = Column(Integer, default=0)
    max_delivery_attempts = Column(Integer, default=3)
    last_attempt_date = Column(DateTime(timezone=True))
    next_attempt_date = Column(DateTime(timezone=True))
    
    # Failure and Return Information
    failure_reason = Column(Text)
    return_reason = Column(Text)
    return_date = Column(DateTime(timezone=True))
    
    # Notifications
    notifications_sent = Column(JSON)  # Track which notifications were sent
    customer_notified = Column(Boolean, default=False)
    
    # Quality and Condition
    package_condition = Column(String(50))  # good, damaged, tampered
    temperature_maintained = Column(Boolean, default=True)
    quality_check_passed = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    shipped_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    
    # Relationships
    patient = relationship("Patient")
    medication = relationship("Medication", back_populates="deliveries")
    
    def __repr__(self):
        return f"<Delivery(id={self.id}, delivery_id='{self.delivery_id}', status='{self.status.value}', patient_id={self.patient_id})>"
    
    @property
    def is_active(self):
        """Check if delivery is currently active"""
        active_statuses = [
            DeliveryStatus.PENDING,
            DeliveryStatus.CONFIRMED,
            DeliveryStatus.PREPARING,
            DeliveryStatus.SHIPPED,
            DeliveryStatus.OUT_FOR_DELIVERY
        ]
        return self.status in active_statuses
    
    @property
    def is_completed(self):
        """Check if delivery is completed"""
        return self.status == DeliveryStatus.DELIVERED
    
    @property
    def is_failed(self):
        """Check if delivery failed"""
        return self.status in [DeliveryStatus.FAILED, DeliveryStatus.CANCELLED, DeliveryStatus.RETURNED]
    
    @property
    def is_overdue(self):
        """Check if delivery is overdue"""
        if self.estimated_delivery_date and not self.is_completed:
            return datetime.now() > self.estimated_delivery_date
        return False
    
    @property
    def days_since_shipped(self):
        """Get days since shipment"""
        if self.shipped_at:
            return (datetime.now() - self.shipped_at).days
        return 0
    
    @property
    def estimated_arrival_time(self):
        """Get estimated arrival time"""
        if self.estimated_delivery_date:
            return self.estimated_delivery_date
        elif self.shipped_at:
            # Default to 2-3 business days for standard delivery
            days_to_add = 2 if self.priority == DeliveryPriority.EXPEDITED else 3
            return self.shipped_at + timedelta(days=days_to_add)
        return None
    
    @property
    def can_attempt_delivery(self):
        """Check if delivery can be attempted"""
        return (self.delivery_attempts < self.max_delivery_attempts and 
                self.status in [DeliveryStatus.OUT_FOR_DELIVERY, DeliveryStatus.FAILED])
    
    def update_status(self, new_status: DeliveryStatus, notes: str = None):
        """Update delivery status with timestamp"""
        old_status = self.status
        self.status = new_status
        
        # Set appropriate timestamps
        if new_status == DeliveryStatus.SHIPPED:
            self.shipped_at = datetime.now()
        elif new_status == DeliveryStatus.DELIVERED:
            self.delivered_at = datetime.now()
            self.actual_delivery_date = datetime.now()
        
        # Add notes if provided
        if notes:
            current_notes = self.delivery_notes or ""
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.delivery_notes = f"{current_notes}\n[{timestamp}] Status changed from {old_status.value} to {new_status.value}: {notes}".strip()
    
    def add_location_update(self, location: str, coordinates: str = None, timestamp: datetime = None):
        """Add location update to tracking"""
        if not timestamp:
            timestamp = datetime.now()
        
        self.current_location = location
        if coordinates:
            self.gps_coordinates = coordinates
        
        # Add to location updates history
        if not self.location_updates:
            self.location_updates = []
        
        update = {
            "location": location,
            "coordinates": coordinates,
            "timestamp": timestamp.isoformat()
        }
        
        self.location_updates.append(update)
    
    def attempt_delivery(self, success: bool = False, notes: str = None):
        """Record delivery attempt"""
        self.delivery_attempts += 1
        self.last_attempt_date = datetime.now()
        
        if success:
            self.update_status(DeliveryStatus.DELIVERED, "Delivery successful")
            self.signature_obtained = True
        else:
            if self.delivery_attempts >= self.max_delivery_attempts:
                self.update_status(DeliveryStatus.FAILED, "Maximum delivery attempts exceeded")
            else:
                # Schedule next attempt (next business day)
                self.next_attempt_date = datetime.now() + timedelta(days=1)
                if notes:
                    self.failure_reason = notes
    
    def mark_as_delivered(self, recipient_name: str = None, signature: str = None):
        """Mark delivery as completed"""
        self.update_status(DeliveryStatus.DELIVERED)
        self.signature_obtained = True
        
        if recipient_name:
            self.recipient_name = recipient_name
        if signature:
            self.signature_data = signature
    
    def cancel_delivery(self, reason: str = None):
        """Cancel delivery"""
        self.update_status(DeliveryStatus.CANCELLED, reason)
        if reason:
            self.failure_reason = reason
    
    def return_delivery(self, reason: str = None):
        """Mark delivery as returned"""
        self.update_status(DeliveryStatus.RETURNED, reason)
        self.return_date = datetime.now()
        if reason:
            self.return_reason = reason
    
    def calculate_delivery_cost(self):
        """Calculate delivery cost based on priority and weight"""
        base_cost = 5.00  # Base delivery cost
        
        # Priority multipliers
        priority_multipliers = {
            DeliveryPriority.STANDARD: 1.0,
            DeliveryPriority.EXPEDITED: 1.5,
            DeliveryPriority.URGENT: 2.0,
            DeliveryPriority.EMERGENCY: 3.0
        }
        
        # Weight-based cost
        weight_cost = (self.total_weight or 1) * 0.50
        
        # Calculate total cost
        total_cost = (base_cost + weight_cost) * priority_multipliers.get(self.priority, 1.0)
        
        # Special handling fees
        if self.requires_refrigeration:
            total_cost += 10.00
        if self.is_controlled_substance:
            total_cost += 15.00
        if self.requires_signature:
            total_cost += 2.00
        
        self.delivery_cost = round(total_cost, 2)
        return self.delivery_cost
    
    def get_tracking_info(self):
        """Get comprehensive tracking information"""
        return {
            "delivery_id": self.delivery_id,
            "tracking_number": self.tracking_number,
            "status": self.status.value,
            "current_location": self.current_location,
            "estimated_delivery": self.estimated_delivery_date.isoformat() if self.estimated_delivery_date else None,
            "last_update": self.updated_at.isoformat() if self.updated_at else None,
            "delivery_attempts": self.delivery_attempts,
            "location_history": self.location_updates or [],
            "carrier": self.carrier_name,
            "service": self.carrier_service
        }
    
    def send_notification(self, notification_type: str):
        """Track sent notifications"""
        if not self.notifications_sent:
            self.notifications_sent = []
        
        notification = {
            "type": notification_type,
            "sent_at": datetime.now().isoformat()
        }
        
        self.notifications_sent.append(notification)
        self.customer_notified = True
    
    @classmethod
    def create_medication_delivery(cls, patient_id: int, medication_id: int, 
                                 delivery_address: str, priority: DeliveryPriority = DeliveryPriority.STANDARD):
        """Create a medication delivery"""
        import uuid
        
        delivery_id = f"DEL-{uuid.uuid4().hex[:8].upper()}"
        
        return cls(
            patient_id=patient_id,
            medication_id=medication_id,
            delivery_id=delivery_id,
            delivery_type=DeliveryType.MEDICATION,
            priority=priority,
            delivery_address=delivery_address,
            requires_signature=True,
            estimated_delivery_date=datetime.now() + timedelta(days=2)
        )