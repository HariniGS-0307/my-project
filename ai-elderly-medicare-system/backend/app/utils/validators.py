"""
Validation utilities for data validation and sanitization
"""

import re
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import phonenumbers
from phonenumbers import NumberParseException

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None

def validate_password(password: str) -> bool:
    """Validate password strength
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if not password or not isinstance(password, str):
        return False
    
    if len(password) < 8:
        return False
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    
    # Check for digit
    if not re.search(r'\d', password):
        return False
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

def validate_phone_number(phone: str, country_code: str = "US") -> bool:
    """Validate phone number format"""
    if not phone or not isinstance(phone, str):
        return False
    
    try:
        parsed_number = phonenumbers.parse(phone, country_code)
        return phonenumbers.is_valid_number(parsed_number)
    except NumberParseException:
        return False

def format_phone_number(phone: str, country_code: str = "US") -> Optional[str]:
    """Format phone number to standard format"""
    if not validate_phone_number(phone, country_code):
        return None
    
    try:
        parsed_number = phonenumbers.parse(phone, country_code)
        return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
    except NumberParseException:
        return None

def validate_date_of_birth(dob: date) -> bool:
    """Validate date of birth"""
    if not isinstance(dob, date):
        return False
    
    today = date.today()
    
    # Check if date is not in the future
    if dob > today:
        return False
    
    # Check if age is reasonable (0-150 years)
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if age < 0 or age > 150:
        return False
    
    return True

def validate_medical_record_number(mrn: str) -> bool:
    """Validate medical record number format"""
    if not mrn or not isinstance(mrn, str):
        return False
    
    # Remove spaces and hyphens
    cleaned_mrn = re.sub(r'[\s-]', '', mrn)
    
    # Check if it's alphanumeric and reasonable length
    if not re.match(r'^[A-Za-z0-9]{6,20}$', cleaned_mrn):
        return False
    
    return True

def validate_insurance_number(insurance_num: str) -> bool:
    """Validate insurance number format"""
    if not insurance_num or not isinstance(insurance_num, str):
        return False
    
    # Remove spaces and hyphens
    cleaned_num = re.sub(r'[\s-]', '', insurance_num)
    
    # Check if it's alphanumeric and reasonable length
    if not re.match(r'^[A-Za-z0-9]{8,25}$', cleaned_num):
        return False
    
    return True

def validate_medicare_number(medicare_num: str) -> bool:
    """Validate Medicare number format (new format: 1EG4-TE5-MK73)"""
    if not medicare_num or not isinstance(medicare_num, str):
        return False
    
    # New Medicare format: 1 digit, 2 letters, 1 digit, hyphen, 2 letters, 1 digit, hyphen, 2 letters, 2 digits
    pattern = r'^\d[A-Za-z]{2}\d-[A-Za-z]{2}\d-[A-Za-z]{2}\d{2}$'
    
    if re.match(pattern, medicare_num):
        return True
    
    # Also accept old format (SSN-based) for legacy support
    old_pattern = r'^\d{3}-\d{2}-\d{4}[A-Za-z]?$'
    return re.match(old_pattern, medicare_num) is not None

def validate_zip_code(zip_code: str, country: str = "US") -> bool:
    """Validate ZIP/postal code format"""
    if not zip_code or not isinstance(zip_code, str):
        return False
    
    if country.upper() == "US":
        # US ZIP code: 12345 or 12345-6789
        pattern = r'^\d{5}(-\d{4})?$'
        return re.match(pattern, zip_code) is not None
    elif country.upper() == "CA":
        # Canadian postal code: A1A 1A1
        pattern = r'^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$'
        return re.match(pattern, zip_code) is not None
    
    # Generic validation for other countries
    return len(zip_code.strip()) >= 3

def validate_height(height: float, unit: str = "cm") -> bool:
    """Validate height measurement"""
    if not isinstance(height, (int, float)) or height <= 0:
        return False
    
    if unit.lower() == "cm":
        # Height in centimeters (50-250 cm)
        return 50 <= height <= 250
    elif unit.lower() in ["ft", "feet"]:
        # Height in feet (1.5-8.5 feet)
        return 1.5 <= height <= 8.5
    elif unit.lower() in ["in", "inches"]:
        # Height in inches (20-100 inches)
        return 20 <= height <= 100
    
    return False

def validate_weight(weight: float, unit: str = "kg") -> bool:
    """Validate weight measurement"""
    if not isinstance(weight, (int, float)) or weight <= 0:
        return False
    
    if unit.lower() == "kg":
        # Weight in kilograms (1-500 kg)
        return 1 <= weight <= 500
    elif unit.lower() in ["lb", "lbs", "pounds"]:
        # Weight in pounds (2-1100 lbs)
        return 2 <= weight <= 1100
    
    return False

def validate_blood_pressure(systolic: int, diastolic: int) -> bool:
    """Validate blood pressure readings"""
    if not isinstance(systolic, int) or not isinstance(diastolic, int):
        return False
    
    # Reasonable ranges for blood pressure
    if not (50 <= systolic <= 300):
        return False
    
    if not (30 <= diastolic <= 200):
        return False
    
    # Systolic should be higher than diastolic
    if systolic <= diastolic:
        return False
    
    return True

def validate_heart_rate(heart_rate: int) -> bool:
    """Validate heart rate"""
    if not isinstance(heart_rate, int):
        return False
    
    # Reasonable range for heart rate (30-250 bpm)
    return 30 <= heart_rate <= 250

def validate_temperature(temperature: float, unit: str = "F") -> bool:
    """Validate body temperature"""
    if not isinstance(temperature, (int, float)):
        return False
    
    if unit.upper() == "F":
        # Fahrenheit (90-110°F)
        return 90 <= temperature <= 110
    elif unit.upper() == "C":
        # Celsius (32-43°C)
        return 32 <= temperature <= 43
    
    return False

def validate_medication_name(name: str) -> bool:
    """Validate medication name"""
    if not name or not isinstance(name, str):
        return False
    
    # Remove extra spaces
    name = name.strip()
    
    # Check length
    if len(name) < 2 or len(name) > 200:
        return False
    
    # Check for valid characters (letters, numbers, spaces, hyphens, parentheses)
    if not re.match(r'^[A-Za-z0-9\s\-\(\)\.]+$', name):
        return False
    
    return True

def validate_dosage(dosage: str) -> bool:
    """Validate medication dosage format"""
    if not dosage or not isinstance(dosage, str):
        return False
    
    # Common dosage patterns: 10mg, 5ml, 2.5mg, 1/2 tablet, etc.
    patterns = [
        r'^\d+(\.\d+)?\s*(mg|g|ml|l|mcg|units?|tablets?|capsules?|drops?)$',
        r'^\d+/\d+\s*(mg|g|ml|l|mcg|units?|tablets?|capsules?|drops?)$',
        r'^\d+(\.\d+)?\s*(mg|g|ml|l|mcg|units?|tablets?|capsules?|drops?)\s*/\s*\d+(\.\d+)?\s*(mg|g|ml|l|mcg|units?|tablets?|capsules?|drops?)$'
    ]
    
    dosage_lower = dosage.lower().strip()
    
    for pattern in patterns:
        if re.match(pattern, dosage_lower):
            return True
    
    return False

def sanitize_string(input_string: str, max_length: Optional[int] = None) -> str:
    """Sanitize string input"""
    if not isinstance(input_string, str):
        return ""
    
    # Remove leading/trailing whitespace
    sanitized = input_string.strip()
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '&', '"', "'", '/', '\\', ';', '|']
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Limit length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

def validate_appointment_duration(duration_minutes: int) -> bool:
    """Validate appointment duration"""
    if not isinstance(duration_minutes, int):
        return False
    
    # Reasonable range: 5 minutes to 8 hours
    return 5 <= duration_minutes <= 480

def validate_age_range(age: int, min_age: int = 0, max_age: int = 150) -> bool:
    """Validate age within specified range"""
    if not isinstance(age, int):
        return False
    
    return min_age <= age <= max_age

def validate_emergency_contact_relationship(relationship: str) -> bool:
    """Validate emergency contact relationship"""
    if not relationship or not isinstance(relationship, str):
        return False
    
    valid_relationships = [
        'spouse', 'child', 'parent', 'sibling', 'grandchild', 'grandparent',
        'aunt', 'uncle', 'cousin', 'friend', 'neighbor', 'caregiver',
        'legal_guardian', 'power_of_attorney', 'healthcare_proxy', 'other'
    ]
    
    return relationship.lower().strip() in valid_relationships

def validate_prescription_number(rx_number: str) -> bool:
    """Validate prescription number format"""
    if not rx_number or not isinstance(rx_number, str):
        return False
    
    # Remove spaces and hyphens
    cleaned_rx = re.sub(r'[\s-]', '', rx_number)
    
    # Check if it's alphanumeric and reasonable length
    if not re.match(r'^[A-Za-z0-9]{6,20}$', cleaned_rx):
        return False
    
    return True

def validate_ndc_number(ndc: str) -> bool:
    """Validate National Drug Code (NDC) number"""
    if not ndc or not isinstance(ndc, str):
        return False
    
    # NDC format: 5-4-2 or 4-4-2 (with or without hyphens)
    # Remove hyphens for validation
    cleaned_ndc = ndc.replace('-', '')
    
    # Check if it's 10 or 11 digits
    if not re.match(r'^\d{10,11}$', cleaned_ndc):
        return False
    
    return True

def validate_data_completeness(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, List[str]]:
    """Validate data completeness and return validation results"""
    results = {
        'missing_fields': [],
        'invalid_fields': [],
        'warnings': []
    }
    
    # Check for missing required fields
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            results['missing_fields'].append(field)
    
    return results