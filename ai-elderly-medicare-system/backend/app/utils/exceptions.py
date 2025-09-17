"""
Custom exceptions for the AI Elderly Medicare System
"""

class BaseCustomException(Exception):
    """Base exception class for custom exceptions"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(BaseCustomException):
    """Raised when data validation fails"""
    
    def __init__(self, message: str, field: str = None, value=None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value

class AuthenticationError(BaseCustomException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")

class AuthorizationError(BaseCustomException):
    """Raised when user lacks required permissions"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "AUTHORIZATION_ERROR")

class PermissionError(BaseCustomException):
    """Raised when user doesn't have permission for an action"""
    
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, "PERMISSION_ERROR")

class ResourceNotFoundError(BaseCustomException):
    """Raised when a requested resource is not found"""
    
    def __init__(self, resource_type: str, resource_id=None):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(message, "RESOURCE_NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id

class DuplicateResourceError(BaseCustomException):
    """Raised when trying to create a resource that already exists"""
    
    def __init__(self, resource_type: str, identifier: str):
        message = f"{resource_type} already exists: {identifier}"
        super().__init__(message, "DUPLICATE_RESOURCE")
        self.resource_type = resource_type
        self.identifier = identifier

class BusinessLogicError(BaseCustomException):
    """Raised when business logic rules are violated"""
    
    def __init__(self, message: str, rule: str = None):
        super().__init__(message, "BUSINESS_LOGIC_ERROR")
        self.rule = rule

class DatabaseError(BaseCustomException):
    """Raised when database operations fail"""
    
    def __init__(self, message: str = "Database operation failed", operation: str = None):
        super().__init__(message, "DATABASE_ERROR")
        self.operation = operation

class ExternalServiceError(BaseCustomException):
    """Raised when external service calls fail"""
    
    def __init__(self, service_name: str, message: str = "External service error"):
        super().__init__(f"{service_name}: {message}", "EXTERNAL_SERVICE_ERROR")
        self.service_name = service_name

class ConfigurationError(BaseCustomException):
    """Raised when configuration is invalid or missing"""
    
    def __init__(self, message: str = "Configuration error", config_key: str = None):
        super().__init__(message, "CONFIGURATION_ERROR")
        self.config_key = config_key

class RateLimitError(BaseCustomException):
    """Raised when rate limits are exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", limit: int = None, window: str = None):
        super().__init__(message, "RATE_LIMIT_ERROR")
        self.limit = limit
        self.window = window

class FileProcessingError(BaseCustomException):
    """Raised when file processing fails"""
    
    def __init__(self, message: str, filename: str = None, file_type: str = None):
        super().__init__(message, "FILE_PROCESSING_ERROR")
        self.filename = filename
        self.file_type = file_type

class MedicationError(BaseCustomException):
    """Raised for medication-related errors"""
    
    def __init__(self, message: str, medication_name: str = None, error_type: str = None):
        super().__init__(message, "MEDICATION_ERROR")
        self.medication_name = medication_name
        self.error_type = error_type

class DrugInteractionError(MedicationError):
    """Raised when drug interactions are detected"""
    
    def __init__(self, medication1: str, medication2: str, severity: str = "unknown"):
        message = f"Drug interaction detected between {medication1} and {medication2}"
        super().__init__(message, error_type="DRUG_INTERACTION")
        self.medication1 = medication1
        self.medication2 = medication2
        self.severity = severity

class AppointmentError(BaseCustomException):
    """Raised for appointment-related errors"""
    
    def __init__(self, message: str, appointment_id: int = None, error_type: str = None):
        super().__init__(message, "APPOINTMENT_ERROR")
        self.appointment_id = appointment_id
        self.error_type = error_type

class SchedulingConflictError(AppointmentError):
    """Raised when appointment scheduling conflicts occur"""
    
    def __init__(self, message: str = "Scheduling conflict detected"):
        super().__init__(message, error_type="SCHEDULING_CONFLICT")

class HealthDataError(BaseCustomException):
    """Raised for health data related errors"""
    
    def __init__(self, message: str, data_type: str = None, patient_id: int = None):
        super().__init__(message, "HEALTH_DATA_ERROR")
        self.data_type = data_type
        self.patient_id = patient_id

class VitalSignsError(HealthDataError):
    """Raised when vital signs are out of normal range"""
    
    def __init__(self, message: str, vital_sign: str, value, normal_range: str = None):
        super().__init__(message, data_type="VITAL_SIGNS")
        self.vital_sign = vital_sign
        self.value = value
        self.normal_range = normal_range

class NotificationError(BaseCustomException):
    """Raised for notification-related errors"""
    
    def __init__(self, message: str, notification_type: str = None, recipient: str = None):
        super().__init__(message, "NOTIFICATION_ERROR")
        self.notification_type = notification_type
        self.recipient = recipient

class DeliveryError(BaseCustomException):
    """Raised for delivery-related errors"""
    
    def __init__(self, message: str, delivery_id: str = None, error_type: str = None):
        super().__init__(message, "DELIVERY_ERROR")
        self.delivery_id = delivery_id
        self.error_type = error_type

class PaymentError(BaseCustomException):
    """Raised for payment processing errors"""
    
    def __init__(self, message: str, transaction_id: str = None, amount: float = None):
        super().__init__(message, "PAYMENT_ERROR")
        self.transaction_id = transaction_id
        self.amount = amount

class AIServiceError(BaseCustomException):
    """Raised when AI/ML services fail"""
    
    def __init__(self, message: str, model_name: str = None, error_type: str = None):
        super().__init__(message, "AI_SERVICE_ERROR")
        self.model_name = model_name
        self.error_type = error_type

class DataIntegrityError(BaseCustomException):
    """Raised when data integrity checks fail"""
    
    def __init__(self, message: str, table: str = None, constraint: str = None):
        super().__init__(message, "DATA_INTEGRITY_ERROR")
        self.table = table
        self.constraint = constraint

class ConcurrencyError(BaseCustomException):
    """Raised when concurrent operations conflict"""
    
    def __init__(self, message: str = "Concurrent modification detected", resource_id=None):
        super().__init__(message, "CONCURRENCY_ERROR")
        self.resource_id = resource_id

class SecurityError(BaseCustomException):
    """Raised for security-related issues"""
    
    def __init__(self, message: str, security_type: str = None):
        super().__init__(message, "SECURITY_ERROR")
        self.security_type = security_type

class ComplianceError(BaseCustomException):
    """Raised when compliance rules are violated"""
    
    def __init__(self, message: str, regulation: str = None, violation_type: str = None):
        super().__init__(message, "COMPLIANCE_ERROR")
        self.regulation = regulation
        self.violation_type = violation_type

class HIPAAViolationError(ComplianceError):
    """Raised when HIPAA compliance is violated"""
    
    def __init__(self, message: str, violation_type: str = None):
        super().__init__(message, regulation="HIPAA", violation_type=violation_type)

# Exception mapping for HTTP status codes
EXCEPTION_STATUS_MAP = {
    ValidationError: 400,
    AuthenticationError: 401,
    AuthorizationError: 403,
    PermissionError: 403,
    ResourceNotFoundError: 404,
    DuplicateResourceError: 409,
    BusinessLogicError: 422,
    RateLimitError: 429,
    DatabaseError: 500,
    ExternalServiceError: 502,
    ConfigurationError: 500,
    FileProcessingError: 422,
    MedicationError: 422,
    DrugInteractionError: 422,
    AppointmentError: 422,
    SchedulingConflictError: 409,
    HealthDataError: 422,
    VitalSignsError: 422,
    NotificationError: 500,
    DeliveryError: 422,
    PaymentError: 422,
    AIServiceError: 503,
    DataIntegrityError: 422,
    ConcurrencyError: 409,
    SecurityError: 403,
    ComplianceError: 422,
    HIPAAViolationError: 403
}

def get_http_status_for_exception(exception: BaseCustomException) -> int:
    """Get appropriate HTTP status code for custom exception"""
    return EXCEPTION_STATUS_MAP.get(type(exception), 500)