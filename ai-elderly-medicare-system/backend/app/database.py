"""
Database configuration and connection management for AI Elderly Medicare System
"""

from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging
import os
from typing import Generator

from app.config import settings

logger = logging.getLogger(__name__)

# Create database engine based on database URL
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DATABASE_ECHO
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        
else:
    # PostgreSQL/MySQL configuration
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
        echo=settings.DATABASE_ECHO
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Create base class for models
Base = declarative_base()

# Metadata for database operations
metadata = MetaData()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session for FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Context manager for database session
    Use this for operations outside of FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database transaction error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """
    Initialize database tables
    Creates all tables defined in models
    """
    try:
        # Import all models to ensure they are registered
        from app.models import (
            user, patient, medication, appointment, 
            notification, delivery, caregiver, 
            health_record, prescription, emergency_contact
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create initial data if needed
        create_initial_data()
        
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def drop_db():
    """
    Drop all database tables
    WARNING: This will delete all data!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise

def create_initial_data():
    """
    Create initial data for the system
    """
    try:
        with get_db_context() as db:
            from app.models.user import User, UserRole, UserStatus
            from app.security import get_password_hash
            
            # Check if admin user exists
            admin_user = db.query(User).filter(User.username == "admin").first()
            
            if not admin_user:
                # Create default admin user
                admin_user = User(
                    username="admin",
                    email="admin@medicare-system.com",
                    hashed_password=get_password_hash("admin123"),
                    first_name="System",
                    last_name="Administrator",
                    role=UserRole.ADMIN,
                    status=UserStatus.ACTIVE,
                    is_active=True,
                    is_verified=True
                )
                db.add(admin_user)
                logger.info("Default admin user created")
            
            # Create demo doctor
            doctor_user = db.query(User).filter(User.username == "doctor").first()
            if not doctor_user:
                doctor_user = User(
                    username="doctor",
                    email="doctor@medicare-system.com",
                    hashed_password=get_password_hash("doctor123"),
                    first_name="Dr. John",
                    last_name="Smith",
                    role=UserRole.DOCTOR,
                    status=UserStatus.ACTIVE,
                    is_active=True,
                    is_verified=True,
                    license_number="MD123456",
                    specialization="Geriatrics"
                )
                db.add(doctor_user)
                logger.info("Demo doctor user created")
            
            # Create demo patient
            patient_user = db.query(User).filter(User.username == "patient").first()
            if not patient_user:
                patient_user = User(
                    username="patient",
                    email="patient@medicare-system.com",
                    hashed_password=get_password_hash("patient123"),
                    first_name="Mary",
                    last_name="Johnson",
                    role=UserRole.PATIENT,
                    status=UserStatus.ACTIVE,
                    is_active=True,
                    is_verified=True
                )
                db.add(patient_user)
                logger.info("Demo patient user created")
                
    except Exception as e:
        logger.error(f"Error creating initial data: {e}")

def check_db_connection():
    """
    Check if database connection is working
    """
    try:
        with get_db_context() as db:
            db.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def get_db_info():
    """
    Get database information
    """
    try:
        with get_db_context() as db:
            if settings.DATABASE_URL.startswith("sqlite"):
                result = db.execute("SELECT sqlite_version()").fetchone()
                return {"type": "SQLite", "version": result[0] if result else "Unknown"}
            else:
                result = db.execute("SELECT version()").fetchone()
                return {"type": "PostgreSQL", "version": result[0] if result else "Unknown"}
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {"type": "Unknown", "version": "Unknown"}

class DatabaseManager:
    """
    Database management utility class
    """
    
    @staticmethod
    def backup_database(backup_path: str = None):
        """
        Create database backup (SQLite only)
        """
        if not settings.DATABASE_URL.startswith("sqlite"):
            raise NotImplementedError("Backup only supported for SQLite databases")
        
        import shutil
        from datetime import datetime
        
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_elderly_medicare_{timestamp}.db"
        
        try:
            db_path = settings.DATABASE_URL.replace("sqlite:///", "")
            shutil.copy2(db_path, backup_path)
            logger.info(f"Database backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            raise
    
    @staticmethod
    def restore_database(backup_path: str):
        """
        Restore database from backup (SQLite only)
        """
        if not settings.DATABASE_URL.startswith("sqlite"):
            raise NotImplementedError("Restore only supported for SQLite databases")
        
        import shutil
        
        try:
            db_path = settings.DATABASE_URL.replace("sqlite:///", "")
            shutil.copy2(backup_path, db_path)
            logger.info(f"Database restored from: {backup_path}")
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            raise
    
    @staticmethod
    def get_table_stats():
        """
        Get statistics about database tables
        """
        try:
            with get_db_context() as db:
                from app.models.user import User
                from app.models.patient import Patient
                from app.models.appointment import Appointment
                from app.models.health_record import HealthRecord
                
                stats = {
                    "users": db.query(User).count(),
                    "patients": db.query(Patient).count(),
                    "appointments": db.query(Appointment).count(),
                    "health_records": db.query(HealthRecord).count(),
                }
                
                return stats
        except Exception as e:
            logger.error(f"Error getting table stats: {e}")
            return {}

# Export commonly used items
__all__ = [
    "Base",
    "engine", 
    "SessionLocal",
    "get_db",
    "get_db_context",
    "init_db",
    "drop_db",
    "check_db_connection",
    "DatabaseManager"
]