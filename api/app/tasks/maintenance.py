import shutil
from celery_app.config import celery_app
from core.logging import get_logger
from pathlib import Path
from core.config import settings
import time
from services.lock_service import is_task_locked

# Initialize logger for maintenance tasks
logger = get_logger('tasks.maintenance')


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Configure periodic maintenance tasks for the application."""
    logger.info('Setting up periodic maintenance tasks...')
    sender.add_periodic_task(
        300, 
        cleanup_temporary_files.s(), 
        name='cleanup temporary files every 5 minutes'
    )
    
    
@celery_app.task
def cleanup_temporary_files():
    """
    Clean up temporary files and directories that are no longer needed.
    
    This task removes temporary directories older than 5 minutes that are not
    currently locked by active tasks.
    """
    logger.info('Starting temporary files cleanup...')
    tmp_dir = settings.tmp_dir
    now = time.time()
    cleaned_count = 0
    
    for folder in Path(tmp_dir).iterdir():
        if folder.is_dir() and not folder.name.startswith("audio_"):
            hash_id = folder.name
            
            # Skip if task is currently locked
            if not is_task_locked(hash_id):
                # Check if the directory is older than 5 minutes
                mtime = folder.stat().st_mtime
                if now - mtime > 300:
                    try:
                        shutil.rmtree(folder)
                        cleaned_count += 1
                        logger.info(f"Cleaned up temporary folder: {hash_id}")
                    except Exception as e:
                        logger.error(f"Error cleaning up temporary folder {folder}: {e}")
    
    logger.info(f'Temporary files cleanup completed. Removed {cleaned_count} folders.')
