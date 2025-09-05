"""
Celery configuration and worker setup for Neuroskip
"""

from .config import celery_app
from .worker import start_worker

__all__ = ['celery_app', 'start_worker']
