import json
from services.youtube import download_audio
from services.audio_workflow_orchestrator import AudioWorkflowOrchestrator
from services.transcription_service import TranscriptionConfig
from core.filesystem import generate_sha256_from_file
import redis
import os
from core.config import settings
from core.logging import get_logger
from celery_app.config import celery_app

# Initialize logger for YouTube processing tasks
logger = get_logger('tasks.youtube_processing')
from database import db
from models.Segment import Segment
from services.lock_service import is_task_locked, lock_task, unlock_task
from tasks.content_classification import classify_advertisement_content

@celery_app.task
def process_youtube_video(id, session_key, upload=False):
    """
    Process YouTube video for transcription and content analysis.
    
    Args:
        id: YouTube video ID
        session_key: Session key for user identification
        upload: Whether this is an upload operation
    
    Returns:
        str: Processing ID on success
    """
    logger.info(f"Starting YouTube video processing for id: {id}, session_key: {session_key}")

    audio_file = None
    audio_parts = []
    porcentage = 0
    
    try:
        config = TranscriptionConfig(
            model_name=os.environ.get("WHISPER_MODEL", "base"),
            cpu_threads=int(os.environ.get("CPU_THREADS", 4))
        )
        orchestrator = AudioWorkflowOrchestrator(config)
        
        logger.info(f"Attempting to download audio for video ID: {id}")
        audio_file = download_audio(id)
        logger.info(f"Audio downloaded successfully: {audio_file}")
        
        hash_id = generate_sha256_from_file(audio_file)
        
        count = 0
        total_segments = 0
        lang = None
        
        # First pass to count total segments for percentage calculation
        segments_list = list(orchestrator.process_audio_complete_workflow(audio_file, id, lang))
        total = len(segments_list)
        
        for segments, info in segments_list:
            count += 1
            porcentage = ((count) * 100) / total  
            if len(segments) > 0:
                _save_youtube_segments_to_database(hash_id, id, segments, porcentage, session_key)
        
        return id
    except Exception as e:
        logger.error(f"Error processing video {id}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Full error details: {repr(e)}")
        raise e
    finally:
        unlock_task(id)


def _save_youtube_segments_to_database(hash_id, external_id, segments, porcentage, session_key):
    """
    Save YouTube video transcription segments to database and trigger content classification.
    
    Args:
        hash_id: SHA256 hash of the audio file
        external_id: YouTube video ID
        segments: List of transcription segments
        porcentage: Processing completion percentage
        session_key: Session key for user identification
    """
    segments_id = []
    try:
        for segment in segments:
            existing_segment = Segment.get_or_none(
            Segment.external_id == external_id,
            Segment.start == segment["start"],
            Segment.end == segment["end"]
            )

            if existing_segment:
                logger.info(f"Segment already exists for external_id {external_id} at start={segment['start']}, end={segment['end']}. Skipping.")
                continue  

            seg = Segment.create(
            hash_id=hash_id,
            external_id=external_id,
            start=str(segment["start"])[:6],
            end=str(segment["end"])[:6],
            text=segment["text"],
            provider="youtube",
            type=None,
            porcentage=porcentage
            )
            segments_id.append(seg.id)
    except Exception as e:
        logger.error(f"Error saving transcription for video {external_id}: {str(e)}")
        raise ValueError(f"Internal Server Error")
    finally:
        # Trigger advertisement classification for the segments
        classify_advertisement_content.delay(segments_id)
