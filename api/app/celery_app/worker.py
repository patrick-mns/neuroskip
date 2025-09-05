"""
Celery worker initialization and startup
"""
import debugpy
from core.config import settings
from core.logging import setup_logging, get_logger

# Setup logging first
setup_logging(settings.log_level)
logger = get_logger('celery.worker')

from .config import celery_app

# Import all task modules to ensure they are registered with Celery
import tasks.maintenance
import tasks.youtube_processing
import tasks.file_storage
import tasks.content_classification

logger.info("Celery worker initialized with all task modules")


def start_worker():
    """Start the Celery worker with debug support if enabled."""
    if settings.debug_worker:
        debugpy.listen(("0.0.0.0", 5680))
        logger.info("Debug mode enabled. Waiting for debugger to attach on port 5680...")
        debugpy.wait_for_client()
        logger.info("Debugger attached, starting worker...")
    
    logger.info("Starting Celery worker...")
    # Start worker with beat scheduler
    celery_app.worker_main([
        'worker',
        '--beat',
        '--loglevel=info',
        '--queues=default,urgent'
    ])


if __name__ == '__main__':
    start_worker()
