"""
Transcription Service - Audio transcription using Whisper

This service provides functionality for audio transcription using Whisper model.
Focuses only on transcription logic, delegating other responsibilities to specialized services.
"""

from dataclasses import dataclass
from typing import List, Optional, Generator, Tuple
from pathlib import Path
from faster_whisper import WhisperModel
from core.logging import get_logger
from .audio_processing_service import AudioProcessingService
from .voice_activity_service import VoiceActivityService
from .temp_file_service import TempFileService


@dataclass
class TranscriptionConfig:
    """Configuration for transcription service"""
    model_name: str = "base"
    cpu_threads: int = 1
    temp_dir: Path = Path("/tmp")


class TranscriptionService:
    """Service for audio transcription using Whisper"""

    def __init__(self, config: Optional[TranscriptionConfig] = None):
        self.config = config or TranscriptionConfig()
        self.logger = get_logger(f'services.{self.__class__.__name__}')
        
        # Initialize Whisper model
        self.whisper_model = WhisperModel(
            self.config.model_name,
            device="cpu", 
            cpu_threads=self.config.cpu_threads,
            compute_type="int8",
        )
        
        # Initialize supporting services
        self.audio_service = AudioProcessingService()
        self.vad_service = VoiceActivityService()
        self.temp_service = TempFileService(self.config.temp_dir)

    def detect_language(self, audio_path: str) -> str:
        """
        Detect the language of an audio file using Whisper.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Detected language code
        """
        try:
            segments, info = self.whisper_model.transcribe(
                audio_path, 
                language=None, 
                beam_size=1
            )
            return info.language
        except Exception as e:
            self.logger.error(f"Language detection failed: {e}")
            raise ValueError("Failed to detect audio language")
    
    def transcribe_part(self, part: Path, offset: float, language: Optional[str] = None) -> Tuple[List[dict], Optional[str]]:
        """
        Transcribe a single audio part.
        
        Args:
            part: Path to the audio part
            offset: Time offset to apply to segments
            language: Language code for transcription
            
        Returns:
            Tuple of (segments list, detected language)
        """
        self.logger.info(f"Transcribing audio part: {part}")
        
        if not part.exists() or part.stat().st_size == 0 or not self.audio_service.verify_audio(part):
            self.logger.error(f"Invalid audio part: {part}")
            return [], None
            
        try:
            segments, info = self.whisper_model.transcribe(
                str(part), 
                beam_size=3, 
                language=language
            )
            
            # Clean up the audio part after transcription
            self.temp_service.cleanup_file(part)
            
            offset = offset or 0
            result = [
                {
                    "start": segment.start + offset, 
                    "end": segment.end + offset, 
                    "text": segment.text
                } 
                for segment in segments
            ]
            
            return result, info.language if info else None
            
        except Exception as e:
            self.logger.error(f"Error transcribing part {part}: {e}")
            return [], None

    def transcribe_audio(self, audio_parts: List[Path], video_id: str, silence_times: List[float], language: Optional[str] = None) -> Generator[Tuple[List[dict], Optional[str]], None, None]:
        """
        Transcribe multiple audio parts.
        
        Args:
            audio_parts: List of audio file paths
            video_id: Unique identifier for the video
            silence_times: List of silence timestamps for offset calculation
            language: Language code for transcription (auto-detected if None)
            
        Yields:
            Tuples of (segments, language_info) for each part
        """
        try:
            # Auto-detect language if not provided
            if language is None:
                longest = self.audio_service.get_longest_audio(audio_parts)
                if longest is not None:
                    language = self.detect_language(str(longest))
                    self.logger.info(f"Detected language: {language}")
                
            for p, part in enumerate(audio_parts):
                offset = silence_times[p-1] if len(silence_times) > 0 and p-1 >= 0 and silence_times[p-1] is not None else 0
                result, detected_lang = self.transcribe_part(part, offset, language)
                
                if language is None and detected_lang is not None:
                    language = detected_lang
                    
                yield result, detected_lang
            
        except Exception as e:
            self.logger.error(f"Error during transcription: {e}")
            raise ValueError("Transcription failed")

    def process_audio_workflow(self, audio_file: Path, video_id: str, language: Optional[str] = None) -> Generator[Tuple[List[dict], Optional[str]], None, None]:
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
            # Detect silence using VAD service
            silence_times = self.vad_service.detect_silence(str(audio_file))
            
            # Create temporary directory
            temp_dir = self.temp_service.create_temp_dir(video_id)
            
            # Split audio using audio processing service
            audio_parts, silence_times = self.audio_service.split_audio(
                audio_file, silence_times, temp_dir, video_id
            )
            
            # Transcribe all parts
            yield from self.transcribe_audio(audio_parts, video_id, silence_times, language)
            
        except Exception as e:
            self.logger.error(f"Error in audio workflow: {e}")
            raise ValueError("Audio processing workflow failed")
        finally:
            # Clean up temporary files
            self.temp_service.cleanup_temp_files(video_id)
