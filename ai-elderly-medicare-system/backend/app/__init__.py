"""
AI Elderly Medicare System Backend Application
"""

__version__ = "1.0.0"
__author__ = "AI Medicare Team"
__description__ = "Advanced healthcare management system for elderly patients with AI integration"

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
bcrypt = Bcrypt()
csrf = CSRFProtect()

def create_app(config_class=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, 
               template_folder='../../frontend/templates',
               static_folder='../../frontend/static')
    
    # Load configuration
    if config_class is None:
        # Default to DevelopmentConfig if no config is provided
        from config import DevelopmentConfig
        config_class = DevelopmentConfig
    
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    
    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": app.config.get('ALLOWED_ORIGINS', [])}})
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/ai_elderly_medicare.log',
                                         maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('AI Elderly Medicare startup')
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register context processors
    register_context_processors(app)
    
    # Register shell context
    register_shell_context(app)
    
    # Register commands
    register_commands(app)
    
    return app

def register_blueprints(app):
    """Register Flask blueprints."""
    from . import routes, auth, dashboard
    
    # Main routes
    app.register_blueprint(routes.create_blueprint())
    
    # Auth routes
    app.register_blueprint(auth.create_auth_blueprint())
    
    # Dashboard routes
    app.register_blueprint(dashboard.create_dashboard_blueprint())
    
    # API routes (versioned)
    from .api.v1 import api as api_v1_blueprint
    app.register_blueprint(api_v1_blueprint, url_prefix='/api/v1')

def register_error_handlers(app):
    """Register error handlers."""
    from flask import render_template
    
    @app.errorhandler(403)
    def forbidden_error(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'message': 'You do not have permission to access this resource.'
            }), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'message': 'The requested resource was not found.'
            }), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'message': 'An internal server error occurred.'
            }), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        if request.path.startswith('/api/'):
            return jsonify({
                'status': 'error',
                'message': 'The file is too large.'
            }), 413
        flash('File is too large. Maximum file size is 16MB.', 'danger')
        return redirect(request.referrer or url_for('main.index'))

def register_context_processors(app):
    """Register context processors."""
    from .models import Notification
    
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)
    
    @app.context_processor
    def inject_notifications():
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(
                user_id=current_user.id,
                is_read=False
            ).count()
            return {'unread_notifications': unread_count}
        return {'unread_notifications': 0}

def register_shell_context(app):
    """Register shell context objects."""
    from .models import User, Role, Permission, Notification, ActivityLog
    
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Role': Role,
            'Permission': Permission,
            'Notification': Notification,
            'ActivityLog': ActivityLog
        }

def register_commands(app):
    """Register Click commands."""
    import click
    from .models import User, Role
    
    @app.cli.command()
    @click.argument('test_names', nargs=-1)
    def test(test_names):
        """Run the unit tests."""
        import unittest
        if test_names:
            tests = unittest.TestLoader().loadTestsFromNames(test_names)
        else:
            tests = unittest.TestLoader().discover('tests')
        unittest.TextTestRunner(verbosity=2).run(tests)
    
    @app.cli.command()
    @click.option('--username', prompt=True, help='The username')
    @click.option('--email', prompt=True, help='The email address')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password')
    def create_admin(username, email, password):
        """Create an admin user."""
        from werkzeug.security import generate_password_hash
        
        # Check if user already exists
        if User.query.filter_by(email=email).first() is not None:
            click.echo('Error: Email already registered.')
            return
        
        # Create admin user
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            is_admin=True,
            is_active=True,
            email_verified=True
        )
        
        # Add admin role
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            user.roles.append(admin_role)
        
        db.session.add(user)
        db.session.commit()
        
        click.echo('Admin user created successfully.')
    
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        click.echo('Database initialized.')
    
    @app.cli.command()
    def seed_roles():
        """Seed the database with default roles and permissions."""
        from .models import Role, Permission
        
        # Create default roles
        roles_permissions = {
            'admin': ['admin', 'manage_users', 'manage_content', 'view_reports'],
            'caregiver': ['view_patients', 'manage_appointments', 'view_reports'],
            'patient': ['view_profile', 'manage_appointments', 'view_medications']
        }
        
        for role_name, permissions in roles_permissions.items():
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
            
            # Clear existing permissions
            role.permissions = []
            
            # Add permissions
            for perm_name in permissions:
                permission = Permission.query.filter_by(name=perm_name).first()
                if permission is None:
                    permission = Permission(name=perm_name, description=f'Can {perm_name.replace("_", " ")}')
                    db.session.add(permission)
                role.permissions.append(permission)
        
        db.session.commit()
        click.echo('Database seeded with default roles and permissions.')

# Import models to ensure they are registered with SQLAlchemy
from . import models