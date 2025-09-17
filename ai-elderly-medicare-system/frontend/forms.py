"""
WTForms for AI Elderly Medicare System
"""

from wtforms import Form, StringField, PasswordField, SelectField, validators
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import re

class BaseForm(Form):
    """Base form class with common functionality"""
    pass

class RegistrationForm(BaseForm):
    """Form for user registration"""
    first_name = StringField('First Name', [
        validators.DataRequired(),
        validators.Length(min=2, max=50)
    ])
    
    last_name = StringField('Last Name', [
        validators.DataRequired(),
        validators.Length(min=2, max=50)
    ])
    
    email = StringField('Email', [
        validators.DataRequired(),
        validators.Email(),
        validators.Length(min=6, max=100)
    ])
    
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=8, max=100),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    
    confirm_password = PasswordField('Confirm Password')
    
    role = SelectField('Role', choices=[
        ('patient', 'Patient'),
        ('caregiver', 'Caregiver'),
        ('doctor', 'Doctor'),
        ('admin', 'Administrator')
    ], default='patient')
    
    def validate_password(self, field):
        password = field.data
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one number')

class PatientForm(BaseForm):
    """Form for patient information"""
    def __init__(self):
        super().__init__()
        self.fields = [
            'first_name',
            'last_name',
            'date_of_birth',
            'address',
            'phone',
            'email',
            'emergency_contact'
        ]

class MedicationForm(BaseForm):
    """Form for medication information"""
    def __init__(self):
        super().__init__()
        self.fields = [
            'name',
            'dosage',
            'frequency',
            'start_date',
            'end_date',
            'prescribing_doctor'
        ]

class AppointmentForm(BaseForm):
    """Form for appointment scheduling"""
    def __init__(self):
        super().__init__()
        self.fields = [
            'patient_id',
            'doctor_id',
            'date',
            'time',
            'reason',
            'notes'
        ]

class LoginForm(BaseForm):
    """Form for user login"""
    def __init__(self):
        super().__init__()
        self.fields = [
            'username',
            'password'
        ]

# Additional form classes would be defined here for:
# - PrescriptionForm
# - DeliveryForm
# - NotificationForm
# - ReportForm
# - SettingsForm

if __name__ == "__main__":
    print("WTForms for AI Elderly Medicare System")
    print("=====================================")
    print("This module defines form classes for the application.")
    print("In a full implementation, these would be WTForms classes with validation.")