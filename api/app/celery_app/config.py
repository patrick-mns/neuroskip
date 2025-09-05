"""
Celery configuration for Neuroskip application.
"""
from core.config import settings
from celery import Celery

# Initialize Celery app
celery_app = Celery(
    'neuroskip',
    broker=settings.redis_string, 
    backend=settings.redis_string,
    task_serializer='json',
    result_serializer='json'
)

# Basic configuration
celery_app.conf.task_track_started = True

# Configure autodiscovery of tasks
celery_app.autodiscover_tasks(['tasks'])

# Configure task routes and queues
celery_app.conf.task_routes = {
    'tasks.youtube_processing.process_youtube_video': {'queue': 'urgent'},
    'tasks.content_classification.classify_advertisement_content': {'queue': 'default'},
    'tasks.maintenance.cleanup_temporary_files': {'queue': 'default'},
    'tasks.file_storage.store_audio_file': {'queue': 'default'},
}

# Define queues
celery_app.conf.task_default_queue = 'default'
celery_app.conf.task_queues = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'urgent': {
        'exchange': 'urgent',
        'routing_key': 'urgent',
    },
}
