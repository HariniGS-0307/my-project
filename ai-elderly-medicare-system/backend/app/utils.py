import os
import jwt
import secrets
import string
from functools import wraps
from datetime import datetime, timedelta
from flask import jsonify, request, current_app
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def generate_token(user_email, expires_in=3600):
    """Generate a JWT token for email verification or password reset."""
    try:
        payload = {
            'email': user_email,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        return None

def verify_token(token):
    """Verify a JWT token and return the email if valid."""
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload['email']
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        return None

def role_required(*roles):
    """Decorator to restrict access to specific roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({
                    'status': 'error',
                    'message': 'Authentication required'
                }), 401
            
            if current_user.role not in roles:
                return jsonify({
                    'status': 'error',
                    'message': 'Insufficient permissions'
                }), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def generate_password(length=12):
    """Generate a random password with the specified length."""
    chars = string.ascii_letters + string.digits + '!@#$%^&*()_+=-'
    while True:
        password = ''.join(secrets.choice(chars) for _ in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in '!@#$%^&*()_+=-' for c in password)):
            return password

def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long'
    if not any(c.isupper() for c in password):
        return False, 'Password must contain at least one uppercase letter'
    if not any(c.islower() for c in password):
        return False, 'Password must contain at least one lowercase letter'
    if not any(c.isdigit() for c in password):
        return False, 'Password must contain at least one number'
    if not any(c in '!@#$%^&*()_+=-' for c in password):
        return False, 'Password must contain at least one special character'
    return True, 'Password is valid'

def send_email(subject, recipients, template, **kwargs):
    """Send an email using the specified template."""
    try:
        from flask_mail import Message
        from . import mail
        
        msg = Message(
            subject=subject,
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=recipients
        )
        
        # Render email template
        msg.html = render_template(f'email/{template}.html', **kwargs)
        
        # Send email
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

def log_activity(user_id, action, details=None):
    """Log user activity to the database."""
    try:
        from .models import ActivityLog
        
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            details=details or {},
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        db.session.add(activity)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error logging activity: {str(e)}")
        return False

def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object to a string."""
    if value is None:
        return ''
    return value.strftime(format)

def parse_datetime(datetime_str, format='%Y-%m-%d %H:%M:%S'):
    """Parse a string to a datetime object."""
    try:
        return datetime.strptime(datetime_str, format)
    except (ValueError, TypeError):
        return None

def json_response(data=None, status='success', message='', status_code=200):
    """Create a standardized JSON response."""
    response = {
        'status': status,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
        
    return jsonify(response), status_code

def paginate_query(query, page=1, per_page=10):
    """Paginate a SQLAlchemy query."""
    return query.paginate(page=page, per_page=per_page, error_out=False)

def allowed_file(filename, allowed_extensions=None):
    """Check if the file extension is allowed."""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, upload_folder, allowed_extensions=None):
    """Save an uploaded file to the specified folder."""
    try:
        if not file or file.filename == '':
            return None, 'No file selected'
            
        if not allowed_file(file.filename, allowed_extensions):
            return None, 'File type not allowed'
            
        # Generate a secure filename
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        
        # Create upload folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save the file
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        return filepath, None
    except Exception as e:
        logger.error(f"Error saving uploaded file: {str(e)}")
        return None, str(e)
