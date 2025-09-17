"""
Email service for sending notifications and communications
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import os

from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Service class for email operations"""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.EMAIL_USERNAME
        self.password = settings.EMAIL_PASSWORD
        self.from_email = settings.EMAIL_USERNAME
        self.from_name = "AI Medicare System"
    
    def _create_smtp_connection(self):
        """Create SMTP connection"""
        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls(context=context)
            server.login(self.username, self.password)
            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {e}")
            raise
    
    def send_email(self, to_email: str, subject: str, body: str, 
                   html_body: Optional[str] = None, attachments: Optional[List[str]] = None) -> bool:
        """Send email with optional HTML body and attachments"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add text part
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        message.attach(part)
            
            # Send email
            with self._create_smtp_connection() as server:
                server.send_message(message)
            
            logger.info(f"Email sent successfully to: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_verification_email(self, email: str, first_name: str, verification_token: str) -> bool:
        """Send email verification email"""
        try:
            subject = "Verify Your Email - AI Medicare System"
            
            # Create verification URL
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
            
            # Text body
            text_body = f"""
Hello {first_name},

Welcome to AI Medicare System! Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
AI Medicare System Team
            """.strip()
            
            # HTML body
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Email Verification</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #2c5aa0; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Medicare System</h1>
        </div>
        <div class="content">
            <h2>Hello {first_name},</h2>
            <p>Welcome to AI Medicare System! Please verify your email address by clicking the button below:</p>
            <p style="text-align: center;">
                <a href="{verification_url}" class="button">Verify Email Address</a>
            </p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create an account, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2024 AI Medicare System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            return False
    
    def send_password_reset_email(self, email: str, first_name: str, reset_token: str) -> bool:
        """Send password reset email"""
        try:
            subject = "Password Reset - AI Medicare System"
            
            # Create reset URL
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            
            # Text body
            text_body = f"""
Hello {first_name},

You requested a password reset for your AI Medicare System account.

Click the link below to reset your password:

{reset_url}

This link will expire in 1 hour.

If you didn't request a password reset, please ignore this email.

Best regards,
AI Medicare System Team
            """.strip()
            
            # HTML body
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Password Reset</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #2c5aa0; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Medicare System</h1>
        </div>
        <div class="content">
            <h2>Hello {first_name},</h2>
            <p>You requested a password reset for your AI Medicare System account.</p>
            <p style="text-align: center;">
                <a href="{reset_url}" class="button">Reset Password</a>
            </p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request a password reset, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2024 AI Medicare System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return False
    
    def send_appointment_reminder(self, email: str, patient_name: str, 
                                appointment_details: Dict[str, Any]) -> bool:
        """Send appointment reminder email"""
        try:
            subject = "Appointment Reminder - AI Medicare System"
            
            appointment_date = appointment_details.get('date', 'Not specified')
            appointment_time = appointment_details.get('time', 'Not specified')
            provider_name = appointment_details.get('provider', 'Healthcare Provider')
            location = appointment_details.get('location', 'Not specified')
            
            # Text body
            text_body = f"""
Hello {patient_name},

This is a reminder about your upcoming appointment:

Date: {appointment_date}
Time: {appointment_time}
Provider: {provider_name}
Location: {location}

Please arrive 15 minutes early for check-in.

If you need to reschedule or cancel, please contact us as soon as possible.

Best regards,
AI Medicare System Team
            """.strip()
            
            # HTML body
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Appointment Reminder</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #2c5aa0; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .appointment-details {{ background: white; padding: 15px; border-left: 4px solid #28a745; margin: 15px 0; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Appointment Reminder</h1>
        </div>
        <div class="content">
            <h2>Hello {patient_name},</h2>
            <p>This is a reminder about your upcoming appointment:</p>
            <div class="appointment-details">
                <p><strong>Date:</strong> {appointment_date}</p>
                <p><strong>Time:</strong> {appointment_time}</p>
                <p><strong>Provider:</strong> {provider_name}</p>
                <p><strong>Location:</strong> {location}</p>
            </div>
            <p>Please arrive 15 minutes early for check-in.</p>
            <p>If you need to reschedule or cancel, please contact us as soon as possible.</p>
        </div>
        <div class="footer">
            <p>© 2024 AI Medicare System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send appointment reminder: {e}")
            return False
    
    def send_medication_reminder(self, email: str, patient_name: str, 
                               medication_name: str, dosage: str, time: str) -> bool:
        """Send medication reminder email"""
        try:
            subject = "Medication Reminder - AI Medicare System"
            
            # Text body
            text_body = f"""
Hello {patient_name},

This is a reminder to take your medication:

Medication: {medication_name}
Dosage: {dosage}
Time: {time}

Please take your medication as prescribed by your healthcare provider.

If you have any questions about your medication, please contact your doctor.

Best regards,
AI Medicare System Team
            """.strip()
            
            # HTML body
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Medication Reminder</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #2c5aa0; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .medication-details {{ background: white; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Medication Reminder</h1>
        </div>
        <div class="content">
            <h2>Hello {patient_name},</h2>
            <p>This is a reminder to take your medication:</p>
            <div class="medication-details">
                <p><strong>Medication:</strong> {medication_name}</p>
                <p><strong>Dosage:</strong> {dosage}</p>
                <p><strong>Time:</strong> {time}</p>
            </div>
            <p>Please take your medication as prescribed by your healthcare provider.</p>
            <p>If you have any questions about your medication, please contact your doctor.</p>
        </div>
        <div class="footer">
            <p>© 2024 AI Medicare System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send medication reminder: {e}")
            return False
    
    def send_health_alert(self, email: str, patient_name: str, alert_message: str, 
                         severity: str = "medium") -> bool:
        """Send health alert email"""
        try:
            subject = f"Health Alert - AI Medicare System"
            
            severity_colors = {
                "low": "#28a745",
                "medium": "#ffc107", 
                "high": "#fd7e14",
                "critical": "#dc3545"
            }
            
            color = severity_colors.get(severity, "#ffc107")
            
            # Text body
            text_body = f"""
Hello {patient_name},

HEALTH ALERT - {severity.upper()} PRIORITY

{alert_message}

Please contact your healthcare provider if you have any concerns.

Best regards,
AI Medicare System Team
            """.strip()
            
            # HTML body
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Health Alert</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: {color}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .alert-box {{ background: white; padding: 15px; border-left: 4px solid {color}; margin: 15px 0; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Health Alert</h1>
            <p>{severity.upper()} PRIORITY</p>
        </div>
        <div class="content">
            <h2>Hello {patient_name},</h2>
            <div class="alert-box">
                <p>{alert_message}</p>
            </div>
            <p>Please contact your healthcare provider if you have any concerns.</p>
        </div>
        <div class="footer">
            <p>© 2024 AI Medicare System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send health alert: {e}")
            return False
    
    def send_bulk_email(self, recipients: List[str], subject: str, body: str, 
                       html_body: Optional[str] = None) -> Dict[str, bool]:
        """Send bulk email to multiple recipients"""
        results = {}
        
        for email in recipients:
            try:
                success = self.send_email(email, subject, body, html_body)
                results[email] = success
            except Exception as e:
                logger.error(f"Failed to send bulk email to {email}: {e}")
                results[email] = False
        
        return results
    
    def send_welcome_email(self, email: str, first_name: str, role: str) -> bool:
        """Send welcome email to new users"""
        try:
            subject = "Welcome to AI Medicare System"
            
            # Text body
            text_body = f"""
Hello {first_name},

Welcome to AI Medicare System! Your account has been created successfully.

Role: {role}

You can now log in to access your personalized healthcare dashboard.

If you have any questions, please don't hesitate to contact our support team.

Best regards,
AI Medicare System Team
            """.strip()
            
            # HTML body
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome to AI Medicare System</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #2c5aa0; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background: #f9f9f9; }}
        .welcome-box {{ background: white; padding: 15px; border-left: 4px solid #28a745; margin: 15px 0; }}
        .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to AI Medicare System</h1>
        </div>
        <div class="content">
            <h2>Hello {first_name},</h2>
            <div class="welcome-box">
                <p>Welcome to AI Medicare System! Your account has been created successfully.</p>
                <p><strong>Role:</strong> {role}</p>
            </div>
            <p>You can now log in to access your personalized healthcare dashboard.</p>
            <p>If you have any questions, please don't hesitate to contact our support team.</p>
        </div>
        <div class="footer">
            <p>© 2024 AI Medicare System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
            
            return self.send_email(email, subject, text_body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            return False