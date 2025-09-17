from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def create_blueprint():
    # Create main blueprint
    bp = Blueprint('main', __name__)

    # Authentication decorator for role-based access
    def role_required(*roles):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    return current_app.login_manager.unauthorized()
                if current_user.role not in roles:
                    flash('You do not have permission to access this page.', 'danger')
                    return redirect(url_for('main.dashboard'))
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    # Error handlers
    @bp.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @bp.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    # Main routes
    @bp.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return render_template('landing.html')

    # Dashboard routes
    @bp.route('/dashboard')
    @login_required
    def dashboard():
        try:
            # Get dashboard data based on user role
            if current_user.role == 'admin':
                return render_template('dashboard/admin_dashboard.html')
            elif current_user.role == 'caregiver':
                return render_template('dashboard/caregiver_dashboard.html')
            else:  # patient
                return render_template('dashboard/patient_dashboard.html')
        except Exception as e:
            logger.error(f"Error loading dashboard: {str(e)}")
            flash('An error occurred while loading the dashboard.', 'danger')
            return redirect(url_for('main.index'))

    # Authentication routes
    from .auth import auth as auth_blueprint
    bp.register_blueprint(auth_blueprint, url_prefix='/auth')

    # Appointments routes
    from .appointments import appointments as appointments_blueprint
    bp.register_blueprint(appointments_blueprint, url_prefix='/appointments')

    # Medications routes
    from .medications import medications as medications_blueprint
    bp.register_blueprint(medications_blueprint, url_prefix='/medications')

    # Delivery routes
    from .delivery import delivery as delivery_blueprint
    bp.register_blueprint(delivery_blueprint, url_prefix='/delivery')

    # Health records routes
    from .health import health as health_blueprint
    bp.register_blueprint(health_blueprint, url_prefix='/health')

    # Messages routes
    from .messages import messages as messages_blueprint
    bp.register_blueprint(messages_blueprint, url_prefix='/messages')

    # Notifications routes
    from .notifications import notifications as notifications_blueprint
    bp.register_blueprint(notifications_blueprint, url_prefix='/notifications')

    # Reports routes
    from .reports import reports as reports_blueprint
    bp.register_blueprint(reports_blueprint, url_prefix='/reports')

    # Settings routes
    from .settings import settings as settings_blueprint
    bp.register_blueprint(settings_blueprint, url_prefix='/settings')

    # Admin routes
    from .admin import admin as admin_blueprint
    bp.register_blueprint(admin_blueprint, url_prefix='/admin')

    # Profile routes
    from .profile import profile as profile_blueprint
    bp.register_blueprint(profile_blueprint, url_prefix='/profile')

    return bp
