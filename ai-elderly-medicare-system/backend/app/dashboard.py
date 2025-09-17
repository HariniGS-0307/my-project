from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from ..models import db, Appointment, Medication, Delivery, Notification
from ..utils import role_required
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def create_dashboard_blueprint():
    dashboard_bp = Blueprint('dashboard', __name__)

    @dashboard_bp.route('/')
    @login_required
    def index():
        try:
            # Get counts for dashboard cards
            stats = {
                'total_patients': 0,
                'upcoming_appointments': 0,
                'active_medications': 0,
                'pending_deliveries': 0,
                'recent_activities': [],
                'upcoming_schedule': []
            }

            # Get counts based on user role
            if current_user.role == 'admin':
                # Admin sees counts for all users
                stats['total_patients'] = User.query.filter_by(role='patient').count()
                stats['upcoming_appointments'] = Appointment.query.filter(
                    Appointment.start_time >= datetime.utcnow()
                ).count()
                stats['active_medications'] = Medication.query.filter_by(status='active').count()
                stats['pending_deliveries'] = Delivery.query.filter_by(status='pending').count()
                
                # Get recent activities (last 10)
                stats['recent_activities'] = ActivityLog.query.order_by(
                    ActivityLog.timestamp.desc()
                ).limit(10).all()
                
                # Get upcoming schedule (next 7 days)
                stats['upcoming_schedule'] = Appointment.query.filter(
                    Appointment.start_time.between(
                        datetime.utcnow(),
                        datetime.utcnow() + timedelta(days=7)
                    )
                ).order_by(Appointment.start_time.asc()).limit(10).all()
                
                return render_template('dashboard/admin_dashboard.html', **stats)
                
            elif current_user.role == 'caregiver':
                # Caregiver sees their assigned patients and related data
                stats['total_patients'] = current_user.assigned_patients.count()
                stats['upcoming_appointments'] = Appointment.query.filter(
                    Appointment.caregiver_id == current_user.id,
                    Appointment.start_time >= datetime.utcnow()
                ).count()
                
                # Get medications for assigned patients
                patient_ids = [p.id for p in current_user.assigned_patients]
                stats['active_medications'] = Medication.query.filter(
                    Medication.patient_id.in_(patient_ids),
                    Medication.status == 'active'
                ).count()
                
                stats['pending_deliveries'] = Delivery.query.filter(
                    Delivery.patient_id.in_(patient_ids),
                    Delivery.status == 'pending'
                ).count()
                
                # Get recent activities for assigned patients
                stats['recent_activities'] = ActivityLog.query.filter(
                    ActivityLog.user_id.in_(patient_ids)
                ).order_by(ActivityLog.timestamp.desc()).limit(10).all()
                
                # Get upcoming schedule for caregiver
                stats['upcoming_schedule'] = Appointment.query.filter(
                    Appointment.caregiver_id == current_user.id,
                    Appointment.start_time.between(
                        datetime.utcnow(),
                        datetime.utcnow() + timedelta(days=7)
                    )
                ).order_by(Appointment.start_time.asc()).limit(10).all()
                
                return render_template('dashboard/caregiver_dashboard.html', **stats)
                
            else:  # Patient
                # Patient sees their own data
                stats['upcoming_appointments'] = Appointment.query.filter(
                    Appointment.patient_id == current_user.id,
                    Appointment.start_time >= datetime.utcnow()
                ).count()
                
                stats['active_medications'] = Medication.query.filter(
                    Medication.patient_id == current_user.id,
                    Medication.status == 'active'
                ).count()
                
                stats['pending_deliveries'] = Delivery.query.filter(
                    Delivery.patient_id == current_user.id,
                    Delivery.status == 'pending'
                ).count()
                
                # Get recent activities for the patient
                stats['recent_activities'] = ActivityLog.query.filter_by(
                    user_id=current_user.id
                ).order_by(ActivityLog.timestamp.desc()).limit(10).all()
                
                # Get upcoming schedule for the patient
                stats['upcoming_schedule'] = Appointment.query.filter(
                    Appointment.patient_id == current_user.id,
                    Appointment.start_time.between(
                        datetime.utcnow(),
                        datetime.utcnow() + timedelta(days=7)
                    )
                ).order_by(Appointment.start_time.asc()).limit(10).all()
                
                return render_template('dashboard/patient_dashboard.html', **stats)
                
        except Exception as e:
            logger.error(f"Error loading dashboard: {str(e)}")
            return render_template('errors/500.html'), 500

    # API endpoint for dashboard data (used for AJAX updates)
    @dashboard_bp.route('/api/dashboard-data')
    @login_required
    def get_dashboard_data():
        try:
            data = {
                'status': 'success',
                'data': {}
            }
            
            # Get unread notifications count
            unread_count = Notification.query.filter_by(
                user_id=current_user.id,
                is_read=False
            ).count()
            
            data['data']['unread_notifications'] = unread_count
            
            # Get upcoming appointments count
            upcoming_appointments = Appointment.query.filter(
                Appointment.patient_id == current_user.id,
                Appointment.start_time >= datetime.utcnow()
            ).count()
            
            data['data']['upcoming_appointments'] = upcoming_appointments
            
            # Get pending deliveries count
            pending_deliveries = Delivery.query.filter(
                Delivery.patient_id == current_user.id,
                Delivery.status == 'pending'
            ).count()
            
            data['data']['pending_deliveries'] = pending_deliveries
            
            return jsonify(data)
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to load dashboard data'
            }), 500

    return dashboard_bp
