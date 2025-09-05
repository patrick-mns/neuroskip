"""
Main entry point for Celery worker.
This allows running the worker directly from the celery_app module.
"""

from .worker import start_worker

if __name__ == '__main__':
    start_worker()
