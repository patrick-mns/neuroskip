"""
Audio Processing Service - Audio validation, manipulation and splitting

This service provides functionality for audio file processing,
validation and splitting operations.
"""

import subprocess
from pathlib import Path
from typing import List, Tuple
from pydub import AudioSegment
from core.logging import get_logger


class AudioProcessingService:
    """Service for audio processing and validation"""

    def __init__(self):
        self.logger = get_logger(f'services.{self.__class__.__name__}')

    def verify_audio(self, audio_file: Path) -> bool:
        """
        Verify if an audio file is valid and playable.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            True if audio is valid, False otherwise
        """
        try:
            subprocess.run(
                ["ffmpeg", "-v", "error", "-i", str(audio_file), "-f", "null", "-"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
        except subprocess.CalledProcessError:
            self.logger.error(f"Invalid audio file: {audio_file}")
            return False

    def get_longest_audio(self, audio_parts: List[Path]) -> Path | None:
        """
        Find the audio part with the longest duration.
        
        Args:
            audio_parts: List of audio file paths
            
        Returns:
            Path to the longest audio file or None
        """
        longest = None
        max_duration = 0

        for path in audio_parts:
            try:
                audio = AudioSegment.from_file(path)
                duration = len(audio)

                if duration > max_duration:
                    max_duration = duration
                    longest = path
            except Exception as e:
                self.logger.warning(f"Could not process audio file {path}: {e}")
                continue

        return longest

    def split_audio(self, audio_file: Path, silence_times: List[float], output_dir: Path, video_id: str) -> Tuple[List[Path], List[float]]:
        """
        Split audio file into segments based on silence detection.
        
        Args:
            audio_file: Path to the input audio file
            silence_times: List of silence timestamps
            output_dir: Directory to save split audio parts
            video_id: Unique identifier for the video
            
        Returns:
            Tuple of (audio parts list, silence times)
        """
        try:
            output_dir.mkdir(exist_ok=True)
            
            output_pattern = str(output_dir / f"audio_part_{video_id}_%03d.mp3")
            segment_times = ",".join(map(str, silence_times))
            
            self.logger.info(f"Splitting audio file: {audio_file}")
            self.logger.info(f"Segment times: {segment_times}")
            
            subprocess.run([
                "ffmpeg", "-i", str(audio_file),
                "-f", "segment", "-segment_times", segment_times,
                "-c:a", "mp3", "-b:a", "192k",
                "-avoid_negative_ts", "make_zero",
                output_pattern, "-y"
            ], check=True, capture_output=True)

            parts = sorted(output_dir.glob(f"audio_part_{video_id}_*.mp3"))
            if not parts:
                raise ValueError("No audio parts were created")
            
            self.logger.info(f"Created {len(parts)} audio parts")
            
            return parts, silence_times
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error splitting audio: {e}")
            raise ValueError("Audio splitting failed")
