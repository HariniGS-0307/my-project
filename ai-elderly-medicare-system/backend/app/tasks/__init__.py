"""
Background Tasks Package for AI Elderly Medicare System
Celery-based asynchronous task processing
"""

from .celery_app import celery_app

__all__ = ["celery_app"]