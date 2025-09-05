"""
Audio Workflow Orchestrator - Coordinates audio processing pipeline

This service orchestrates the complete audio processing workflow,
coordinating between transcription, audio processing, VAD, and file management services.
"""

from pathlib import Path
from typing import List, Optional, Generator, Tuple
from core.logging import get_logger
from .transcription_service import TranscriptionService, TranscriptionConfig
from .audio_processing_service import AudioProcessingService
from .voice_activity_service import VoiceActivityService
from .temp_file_service import TempFileService


class AudioWorkflowOrchestrator:
    """Orchestrates the complete audio processing and transcription workflow"""

    def __init__(self, transcription_config: Optional[TranscriptionConfig] = None):
        self.logger = get_logger(f'services.{self.__class__.__name__}')
        
        # Initialize services
        self.transcription_service = TranscriptionService(transcription_config)
        self.audio_service = AudioProcessingService()
        self.vad_service = VoiceActivityService()
        self.temp_service = TempFileService(
            transcription_config.temp_dir if transcription_config else Path("/tmp")
        )

    def process_audio_complete_workflow(
        self, 
        audio_file: Path, 
        video_id: str, 
        language: Optional[str] = None
    ) -> Generator[Tuple[List[dict], Optional[str]], None, None]:
        """
        Complete workflow for processing and transcribing audio.
        
        Args:
            audio_file: Path to the input audio file
            video_id: Unique identifier for the video
            language: Language code for transcription (auto-detected if None)
            
        Yields:
            Tuples of (segments, language_info) for each part
        """
        try:
            self.logger.info(f"Starting audio workflow for video: {video_id}")
            
            # Step 1: Verify audio file
            if not self.audio_service.verify_audio(audio_file):
                raise ValueError(f"Invalid audio file: {audio_file}")
            
            # Step 2: Detect silence using VAD service
            self.logger.info("Detecting silence intervals...")
            silence_times = self.vad_service.detect_silence(str(audio_file))
            
            # Step 3: Create temporary directory
            temp_dir = self.temp_service.create_temp_dir(video_id)
            
            # Step 4: Split audio using audio processing service
            self.logger.info("Splitting audio into segments...")
            audio_parts, silence_times = self.audio_service.split_audio(
                audio_file, silence_times, temp_dir, video_id
            )
            
            # Step 5: Transcribe all parts
            self.logger.info(f"Transcribing {len(audio_parts)} audio segments...")
            yield from self.transcription_service.transcribe_audio(
                audio_parts, video_id, silence_times, language
            )
            
            self.logger.info(f"Audio workflow completed for video: {video_id}")
            
        except Exception as e:
            self.logger.error(f"Error in audio workflow for {video_id}: {e}")
            raise ValueError(f"Audio processing workflow failed: {e}")
        finally:
            # Clean up temporary files
            self.temp_service.cleanup_temp_files(video_id)

    def transcribe_single_file(
        self, 
        audio_file: Path, 
        language: Optional[str] = None
    ) -> List[dict]:
        """
        Transcribe a single audio file without splitting.
        
        Args:
            audio_file: Path to the audio file
            language: Language code for transcription
            
        Returns:
            List of transcription segments
        """
        try:
            self.logger.info(f"Transcribing single file: {audio_file}")
            
            # Verify audio file
            if not self.audio_service.verify_audio(audio_file):
                raise ValueError(f"Invalid audio file: {audio_file}")
            
            # Auto-detect language if not provided
            if language is None:
                language = self.transcription_service.detect_language(str(audio_file))
                self.logger.info(f"Detected language: {language}")
            
            # Transcribe directly
            segments, _ = self.transcription_service.transcribe_part(audio_file, 0, language)
            
            self.logger.info(f"Transcription completed with {len(segments)} segments")
            return segments
            
        except Exception as e:
            self.logger.error(f"Error transcribing single file {audio_file}: {e}")
            raise ValueError(f"Single file transcription failed: {e}")

    def get_audio_speech_segments(self, audio_file: Path) -> List[dict]:
        """
        Get speech segments from an audio file using VAD.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            List of speech segments with timestamps
        """
        try:
            return self.vad_service.detect_speech_segments(str(audio_file))
        except Exception as e:
            self.logger.error(f"Error detecting speech segments: {e}")
            raise ValueError(f"Speech segment detection failed: {e}")

    def cleanup_workflow_files(self, video_id: str) -> None:
        """
        Clean up all temporary files for a workflow.
        
        Args:
            video_id: Unique identifier for the workflow
        """
        self.temp_service.cleanup_temp_files(video_id)
