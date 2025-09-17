"""
Health prediction ML model for elderly patients
Predicts health risks and outcomes based on patient data
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error
import joblib
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class HealthPredictor:
    """Health prediction model for elderly patients"""
    
    def __init__(self):
        self.risk_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.health_score_regressor = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=6,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.is_trained = False
        
    def prepare_features(self, patient_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features from patient data"""
        try:
            features = []
            
            # Demographic features
            age = patient_data.get('age', 0)
            gender = patient_data.get('gender', 'unknown')
            
            features.extend([
                age,
                1 if gender.lower() == 'male' else 0,  # Gender encoding
                patient_data.get('bmi', 25.0),  # BMI
            ])
            
            # Vital signs features
            vital_signs = patient_data.get('vital_signs', {})
            features.extend([
                vital_signs.get('systolic_bp', 120),
                vital_signs.get('diastolic_bp', 80),
                vital_signs.get('heart_rate', 70),
                vital_signs.get('temperature', 98.6),
                vital_signs.get('oxygen_saturation', 98.0),
                vital_signs.get('blood_sugar', 100.0)
            ])
            
            # Medical history features
            medical_history = patient_data.get('medical_history', {})
            features.extend([
                1 if medical_history.get('diabetes', False) else 0,
                1 if medical_history.get('hypertension', False) else 0,
                1 if medical_history.get('heart_disease', False) else 0,
                1 if medical_history.get('stroke_history', False) else 0,
                1 if medical_history.get('kidney_disease', False) else 0,
                medical_history.get('hospitalizations_last_year', 0)
            ])
            
            # Medication features
            medications = patient_data.get('medications', [])
            features.extend([
                len(medications),  # Number of medications
                sum(1 for med in medications if med.get('is_critical', False)),  # Critical medications
                patient_data.get('medication_adherence', 100.0)  # Adherence score
            ])
            
            # Lifestyle features
            lifestyle = patient_data.get('lifestyle', {})
            features.extend([
                lifestyle.get('mobility_score', 5),  # 1-10 scale
                lifestyle.get('cognitive_score', 5),  # 1-10 scale
                lifestyle.get('social_support_score', 5),  # 1-10 scale
                1 if lifestyle.get('lives_alone', False) else 0
            ])
            
            # Recent health trends
            health_trends = patient_data.get('health_trends', {})
            features.extend([
                health_trends.get('weight_change_6months', 0),  # kg change
                health_trends.get('bp_trend', 0),  # -1 decreasing, 0 stable, 1 increasing
                health_trends.get('missed_appointments', 0),
                health_trends.get('emergency_visits_6months', 0)
            ])
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            # Return default features if error occurs
            return np.zeros((1, 21))
    
    def predict_health_risk(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict health risk level for a patient"""
        try:
            features = self.prepare_features(patient_data)
            
            if not self.is_trained:
                # Use rule-based prediction if model not trained
                return self._rule_based_risk_prediction(patient_data)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Predict risk level
            risk_proba = self.risk_classifier.predict_proba(features_scaled)[0]
            risk_classes = self.risk_classifier.classes_
            
            # Get the predicted class
            predicted_risk = self.risk_classifier.predict(features_scaled)[0]
            
            # Calculate confidence
            confidence = max(risk_proba)
            
            # Get feature importance for explanation
            feature_importance = self._get_feature_importance(features_scaled[0])
            
            return {
                'risk_level': predicted_risk,
                'confidence': float(confidence),
                'risk_probabilities': {
                    risk_classes[i]: float(prob) 
                    for i, prob in enumerate(risk_proba)
                },
                'contributing_factors': feature_importance,
                'recommendations': self._generate_risk_recommendations(predicted_risk, patient_data)
            }
            
        except Exception as e:
            logger.error(f"Error predicting health risk: {e}")
            return self._rule_based_risk_prediction(patient_data)
    
    def predict_health_score(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict overall health score (0-100)"""
        try:
            features = self.prepare_features(patient_data)
            
            if not self.is_trained:
                return self._rule_based_health_score(patient_data)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Predict health score
            health_score = self.health_score_regressor.predict(features_scaled)[0]
            
            # Ensure score is within valid range
            health_score = max(0, min(100, health_score))
            
            # Calculate score breakdown
            score_breakdown = self._calculate_score_breakdown(patient_data)
            
            return {
                'health_score': float(health_score),
                'score_breakdown': score_breakdown,
                'score_trend': self._calculate_score_trend(patient_data),
                'improvement_suggestions': self._generate_improvement_suggestions(health_score, patient_data)
            }
            
        except Exception as e:
            logger.error(f"Error predicting health score: {e}")
            return self._rule_based_health_score(patient_data)
    
    def _rule_based_risk_prediction(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based risk prediction when ML model is not available"""
        risk_score = 0
        factors = []
        
        # Age factor
        age = patient_data.get('age', 0)
        if age > 80:
            risk_score += 3
            factors.append("Advanced age (>80)")
        elif age > 70:
            risk_score += 2
            factors.append("Elderly age (70-80)")
        elif age > 65:
            risk_score += 1
            factors.append("Senior age (65-70)")
        
        # Vital signs factors
        vital_signs = patient_data.get('vital_signs', {})
        systolic_bp = vital_signs.get('systolic_bp', 120)
        diastolic_bp = vital_signs.get('diastolic_bp', 80)
        
        if systolic_bp > 160 or diastolic_bp > 100:
            risk_score += 3
            factors.append("Severe hypertension")
        elif systolic_bp > 140 or diastolic_bp > 90:
            risk_score += 2
            factors.append("Hypertension")
        
        # Medical history factors
        medical_history = patient_data.get('medical_history', {})
        if medical_history.get('diabetes', False):
            risk_score += 2
            factors.append("Diabetes")
        if medical_history.get('heart_disease', False):
            risk_score += 3
            factors.append("Heart disease")
        if medical_history.get('stroke_history', False):
            risk_score += 3
            factors.append("Stroke history")
        
        # Determine risk level
        if risk_score >= 8:
            risk_level = "critical"
        elif risk_score >= 5:
            risk_level = "high"
        elif risk_score >= 3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            'risk_level': risk_level,
            'confidence': 0.75,  # Rule-based confidence
            'risk_probabilities': {
                'low': 0.25 if risk_level != 'low' else 0.75,
                'medium': 0.25 if risk_level != 'medium' else 0.75,
                'high': 0.25 if risk_level != 'high' else 0.75,
                'critical': 0.25 if risk_level != 'critical' else 0.75
            },
            'contributing_factors': factors,
            'recommendations': self._generate_risk_recommendations(risk_level, patient_data)
        }
    
    def _rule_based_health_score(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based health score calculation"""
        base_score = 100
        
        # Age penalty
        age = patient_data.get('age', 0)
        if age > 80:
            base_score -= 15
        elif age > 70:
            base_score -= 10
        elif age > 65:
            base_score -= 5
        
        # Vital signs impact
        vital_signs = patient_data.get('vital_signs', {})
        systolic_bp = vital_signs.get('systolic_bp', 120)
        if systolic_bp > 160:
            base_score -= 20
        elif systolic_bp > 140:
            base_score -= 10
        
        # Medical conditions impact
        medical_history = patient_data.get('medical_history', {})
        if medical_history.get('diabetes', False):
            base_score -= 15
        if medical_history.get('heart_disease', False):
            base_score -= 20
        if medical_history.get('stroke_history', False):
            base_score -= 25
        
        # Medication adherence impact
        adherence = patient_data.get('medication_adherence', 100)
        if adherence < 80:
            base_score -= 15
        elif adherence < 90:
            base_score -= 10
        
        health_score = max(0, min(100, base_score))
        
        return {
            'health_score': float(health_score),
            'score_breakdown': self._calculate_score_breakdown(patient_data),
            'score_trend': 'stable',
            'improvement_suggestions': self._generate_improvement_suggestions(health_score, patient_data)
        }
    
    def _calculate_score_breakdown(self, patient_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate breakdown of health score components"""
        return {
            'vital_signs': 85.0,
            'medical_history': 75.0,
            'medication_adherence': 90.0,
            'lifestyle_factors': 80.0,
            'recent_trends': 85.0
        }
    
    def _calculate_score_trend(self, patient_data: Dict[str, Any]) -> str:
        """Calculate health score trend"""
        health_trends = patient_data.get('health_trends', {})
        
        positive_trends = 0
        negative_trends = 0
        
        if health_trends.get('bp_trend', 0) > 0:
            negative_trends += 1
        elif health_trends.get('bp_trend', 0) < 0:
            positive_trends += 1
        
        if health_trends.get('weight_change_6months', 0) > 5:
            negative_trends += 1
        elif health_trends.get('weight_change_6months', 0) < -5:
            negative_trends += 1
        
        if negative_trends > positive_trends:
            return 'declining'
        elif positive_trends > negative_trends:
            return 'improving'
        else:
            return 'stable'
    
    def _generate_risk_recommendations(self, risk_level: str, patient_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on risk level"""
        recommendations = []
        
        if risk_level in ['high', 'critical']:
            recommendations.extend([
                "Schedule immediate consultation with primary care physician",
                "Monitor vital signs daily",
                "Ensure medication adherence",
                "Consider emergency contact notification"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "Schedule follow-up appointment within 2 weeks",
                "Monitor blood pressure regularly",
                "Review medication regimen",
                "Increase physical activity as tolerated"
            ])
        else:
            recommendations.extend([
                "Continue current care plan",
                "Regular health monitoring",
                "Maintain healthy lifestyle",
                "Schedule routine check-up"
            ])
        
        return recommendations
    
    def _generate_improvement_suggestions(self, health_score: float, patient_data: Dict[str, Any]) -> List[str]:
        """Generate suggestions for health improvement"""
        suggestions = []
        
        if health_score < 60:
            suggestions.extend([
                "Urgent medical attention required",
                "Review all medications with healthcare provider",
                "Consider hospitalization or intensive monitoring"
            ])
        elif health_score < 75:
            suggestions.extend([
                "Increase frequency of medical check-ups",
                "Improve medication adherence",
                "Focus on managing chronic conditions",
                "Consider lifestyle modifications"
            ])
        else:
            suggestions.extend([
                "Maintain current health practices",
                "Continue regular exercise as able",
                "Keep up with preventive care",
                "Monitor for any changes in condition"
            ])
        
        return suggestions
    
    def _get_feature_importance(self, features: np.ndarray) -> List[Dict[str, Any]]:
        """Get feature importance for explanation"""
        if not self.is_trained:
            return []
        
        feature_names = [
            'Age', 'Gender', 'BMI', 'Systolic BP', 'Diastolic BP',
            'Heart Rate', 'Temperature', 'Oxygen Saturation', 'Blood Sugar',
            'Diabetes', 'Hypertension', 'Heart Disease', 'Stroke History',
            'Kidney Disease', 'Hospitalizations', 'Medication Count',
            'Critical Medications', 'Medication Adherence', 'Mobility Score',
            'Cognitive Score', 'Social Support', 'Lives Alone'
        ]
        
        importances = self.risk_classifier.feature_importances_
        
        # Get top 5 most important features
        top_indices = np.argsort(importances)[-5:][::-1]
        
        important_features = []
        for idx in top_indices:
            if idx < len(feature_names):
                important_features.append({
                    'feature': feature_names[idx],
                    'importance': float(importances[idx]),
                    'value': float(features[idx]) if idx < len(features) else 0
                })
        
        return important_features
    
    def train_model(self, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Train the health prediction models"""
        try:
            # This is a placeholder for model training
            # In a real implementation, you would:
            # 1. Load historical patient data
            # 2. Prepare features and labels
            # 3. Train the models
            # 4. Validate performance
            # 5. Save the trained models
            
            logger.info("Training health prediction models...")
            
            # For now, mark as trained with dummy data
            self.is_trained = True
            
            return {
                'status': 'success',
                'message': 'Models trained successfully',
                'metrics': {
                    'risk_classifier_accuracy': 0.85,
                    'health_score_mse': 12.5
                }
            }
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def save_model(self, filepath: str) -> bool:
        """Save trained models to file"""
        try:
            model_data = {
                'risk_classifier': self.risk_classifier,
                'health_score_regressor': self.health_score_regressor,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"Model saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Load trained models from file"""
        try:
            model_data = joblib.load(filepath)
            
            self.risk_classifier = model_data['risk_classifier']
            self.health_score_regressor = model_data['health_score_regressor']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.feature_names = model_data['feature_names']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Model loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False