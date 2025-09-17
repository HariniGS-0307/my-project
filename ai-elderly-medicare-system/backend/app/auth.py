from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User, db
from ..forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from ..utils import send_email, generate_token, verify_token
from datetime import datetime, timedelta
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def create_auth_blueprint():
    auth = Blueprint('auth', __name__)

    @auth.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
            
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password, form.password.data):
                if not user.is_active:
                    flash('Your account is inactive. Please contact support.', 'warning')
                    return redirect(url_for('auth.login'))
                
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                flash('You have been logged in successfully!', 'success')
                
                # Redirect based on user role
                if user.role == 'admin':
                    return redirect(next_page or url_for('admin.dashboard'))
                else:
                    return redirect(next_page or url_for('dashboard.index'))
            else:
                flash('Invalid email or password', 'danger')
        
        return render_template('auth/login.html', form=form)

    @auth.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
            
        form = RegistrationForm()
        if form.validate_on_submit():
            try:
                hashed_password = generate_password_hash(form.password.data)
                user = User(
                    email=form.email.data,
                    password=hashed_password,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    phone=form.phone.data,
                    role='patient',  # Default role
                    is_active=True  # Set to False if email verification is required
                )
                
                db.session.add(user)
                db.session.commit()
                
                # Send welcome/verification email
                try:
                    token = generate_token(user.email)
                    verify_url = url_for('auth.verify_email', token=token, _external=True)
                    send_email(
                        subject='Welcome to AI Elderly Medicare',
                        recipients=[user.email],
                        template='email/welcome.html',
                        user=user,
                        verify_url=verify_url
                    )
                except Exception as e:
                    logger.error(f"Error sending welcome email: {str(e)}")
                
                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error during registration: {str(e)}")
                flash('An error occurred during registration. Please try again.', 'danger')
        
        return render_template('auth/register.html', form=form)

    @auth.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('auth.login'))

    @auth.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
            
        form = ForgotPasswordForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                try:
                    # Generate password reset token (expires in 1 hour)
                    token = generate_token(user.email, expires_in=3600)
                    reset_url = url_for('auth.reset_password', token=token, _external=True)
                    
                    # Send password reset email
                    send_email(
                        subject='Password Reset Request',
                        recipients=[user.email],
                        template='email/reset_password.html',
                        user=user,
                        reset_url=reset_url
                    )
                    
                    flash('Password reset instructions have been sent to your email.', 'info')
                    return redirect(url_for('auth.login'))
                except Exception as e:
                    logger.error(f"Error sending password reset email: {str(e)}")
                    flash('An error occurred while sending the reset email. Please try again.', 'danger')
            else:
                flash('If an account exists with this email, you will receive a password reset link.', 'info')
                return redirect(url_for('auth.login'))
                
        return render_template('auth/forgot_password.html', form=form)

    @auth.route('/reset-password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
            
        # Verify token
        email = verify_token(token)
        if not email:
            flash('The password reset link is invalid or has expired.', 'danger')
            return redirect(url_for('auth.forgot_password'))
            
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('auth.forgot_password'))
            
        form = ResetPasswordForm()
        if form.validate_on_submit():
            try:
                user.password = generate_password_hash(form.password.data)
                db.session.commit()
                flash('Your password has been updated successfully!', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error resetting password: {str(e)}")
                flash('An error occurred while resetting your password. Please try again.', 'danger')
                
        return render_template('auth/reset_password.html', form=form, token=token)

    @auth.route('/verify-email/<token>')
    def verify_email(token):
        if current_user.is_authenticated and current_user.email_verified:
            return redirect(url_for('dashboard.index'))
            
        email = verify_token(token)
        if not email:
            flash('The verification link is invalid or has expired.', 'danger')
            return redirect(url_for('auth.login'))
            
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('auth.register'))
            
        if user.email_verified:
            flash('Email already verified. Please log in.', 'info')
        else:
            user.email_verified = True
            user.email_verified_at = datetime.utcnow()
            db.session.commit()
            flash('Your email has been verified successfully!', 'success')
            
        return redirect(url_for('auth.login'))

    @auth.route('/two-factor')
    @login_required
    def two_factor():
        if current_user.two_factor_enabled:
            return redirect(url_for('dashboard.index'))
            
        return render_template('auth/two_factor.html')

    return auth
