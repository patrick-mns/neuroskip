"""
Voice Activity Detection Service - Voice activity and silence detection

This service provides functionality for detecting voice activity and
silence intervals in audio files using Silero VAD.
"""

import torch
from typing import List
from core.logging import get_logger


class VoiceActivityService:
    """Service for voice activity detection using Silero VAD"""

    def __init__(self):
        self.logger = get_logger(f'services.{self.__class__.__name__}')
        
        # Initialize Silero VAD model
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False
        )
        self.get_speech_ts, _, self.read_audio, _, _ = utils

    def detect_silence(self, audio_file: str) -> List[float]:
        """
        Detect silence intervals in an audio file using Silero VAD.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            List of silence end timestamps
        """
        try:
            wav = self.read_audio(audio_file, sampling_rate=16000)
            speech_timestamps = self.get_speech_ts(wav, self.model)

            # Invert: we want intervals without speech
            silence_ends = []
            last_end = 0.0
            
            for segment in speech_timestamps:
                start, end = segment['start'] / 16000.0, segment['end'] / 16000.0
                if start > last_end:
                    silence_ends.append(start)
                last_end = end

            if not silence_ends:
                duration = wav.shape[-1] / 16000.0
                self.logger.info("No silence detected, using full duration")
                silence_ends.append(duration)

            return silence_ends

        except Exception as e:
            self.logger.error(f"Silero VAD error: {str(e)}")
            raise ValueError("Silence detection failed")

    def detect_speech_segments(self, audio_file: str) -> List[dict]:
        """
        Detect speech segments in an audio file.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            List of speech segments with start and end timestamps
        """
        try:
            wav = self.read_audio(audio_file, sampling_rate=16000)
            speech_timestamps = self.get_speech_ts(wav, self.model)
            
            # Convert timestamps to seconds
            segments = []
            for segment in speech_timestamps:
                segments.append({
                    'start': segment['start'] / 16000.0,
                    'end': segment['end'] / 16000.0
                })
            
            return segments

        except Exception as e:
            self.logger.error(f"Speech detection error: {str(e)}")
            raise ValueError("Speech detection failed")
