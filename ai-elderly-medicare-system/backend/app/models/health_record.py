ies"""
Health record model for tracking patient vital signs and health data
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

class HealthRecord(Base):
    """Health record model for storing patient health data"""
    
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    recorded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Vital Signs
    systolic_bp = Column(Integer)  # Systolic blood pressure
    diastolic_bp = Column(Integer)  # Diastolic blood pressure
    heart_rate = Column(Integer)  # Beats per minute
    temperature = Column(Float)  # In Fahrenheit
    respiratory_rate = Column(Integer)  # Breaths per minute
    oxygen_saturation = Column(Float)  # SpO2 percentage
    blood_sugar = Column(Float)  # mg/dL
    
    # Physical Measurements
    weight = Column(Float)  # in kg
    height = Column(Float)  # in cm
    bmi = Column(Float)  # Body Mass Index
    
    # Health Indicators
    pain_level = Column(Integer)  # 1-10 scale
    mood_score = Column(Integer)  # 1-10 scale
    sleep_hours = Column(Float)  # Hours of sleep
    activity_level = Column(String(20))  # low, moderate, high
    
    # Symptoms and Notes
    symptoms = Column(Text)
    notes = Column(Text)
    diagnosis = Column(Text)
    treatment_plan = Column(Text)
    
    # AI Analysis Results
    ai_risk_score = Column(Float)  # 0-1 risk score from AI model
    ai_recommendations = Column(JSON)  # AI-generated recommendations
    anomaly_detected = Column(Boolean, default=False)
    
    # Metadata
    record_type = Column(String(50), default="routine")  # routine, emergency, follow_up
    location = Column(String(100))  # where the record was taken
    device_used = Column(String(100))  # monitoring device used
    
    # Timestamps
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="health_records")
    recorded_by = relationship("User", foreign_keys=[recorded_by_id])
    
    def __repr__(self):
        return f"<HealthRecord(id={self.id}, patient_id={self.patient_id}, recorded_at='{self.recorded_at}')>"
    
    @property
    def blood_pressure(self):
        """Get formatted blood pressure reading"""
        if self.systolic_bp and self.diastolic_bp:
            return f"{self.systolic_bp}/{self.diastolic_bp}"
        return None
    
    @property
    def is_critical(self):
        """Check if any vital signs are in critical range"""
        critical_conditions = [
            self.systolic_bp and (self.systolic_bp > 180 or self.systolic_bp < 90),
            self.diastolic_bp and (self.diastolic_bp > 120 or self.diastolic_bp < 60),
            self.heart_rate and (self.heart_rate > 120 or self.heart_rate < 50),
            self.temperature and (self.temperature > 103 or self.temperature < 95),
            self.oxygen_saturation and self.oxygen_saturation < 90,
            self.blood_sugar and (self.blood_sugar > 400 or self.blood_sugar < 70)
        ]
        return any(critical_conditions)
    
    @property
    def vital_signs_summary(self):
        """Get a summary of vital signs"""
        summary = {}
        if self.blood_pressure:
            summary["blood_pressure"] = self.blood_pressure
        if self.heart_rate:
            summary["heart_rate"] = f"{self.heart_rate} bpm"
        if self.temperature:
            summary["temperature"] = f"{self.temperature}°F"
        if self.oxygen_saturation:
            summary["oxygen_saturation"] = f"{self.oxygen_saturation}%"
        if self.blood_sugar:
            summary["blood_sugar"] = f"{self.blood_sugar} mg/dL"
        return summary
    
    def calculate_health_score(self):
        """Calculate overall health score based on vital signs"""
        score = 100
        
        # Blood pressure scoring
        if self.systolic_bp:
            if self.systolic_bp > 140 or self.systolic_bp < 90:
                score -= 15
            elif self.systolic_bp > 130 or self.systolic_bp < 100:
                score -= 10
        
        # Heart rate scoring
        if self.heart_rate:
            if self.heart_rate > 100 or self.heart_rate < 60:
                score -= 10
            elif self.heart_rate > 90 or self.heart_rate < 65:
                score -= 5
        
        # Temperature scoring
        if self.temperature:
            if self.temperature > 100.4 or self.temperature < 97:
                score -= 10
        
        # Oxygen saturation scoring
        if self.oxygen_saturation:
            if self.oxygen_saturation < 95:
                score -= 15
            elif self.oxygen_saturation < 98:
                score -= 5
        
        # Blood sugar scoring
        if self.blood_sugar:
            if self.blood_sugar > 200 or self.blood_sugar < 80:
                score -= 15
            elif self.blood_sugar > 140 or self.blood_sugar < 90:
                score -= 10
        
        return max(0, score)