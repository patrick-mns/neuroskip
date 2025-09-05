import os
import re
from core.config import settings
from pathlib import Path
from pytubefix import YouTube
from pytubefix.exceptions import VideoUnavailable


def download_audio(video_id: str) -> Path:
    """
    Download audio from a YouTube video.
    
    Args:
        video_id: YouTube video ID (11 characters)
        
    Returns:
        Path to the downloaded audio file
        
    Raises:
        ValueError: If video ID format is invalid or no audio stream found
        RuntimeError: If download fails
    """
    try:
        # Validate YouTube video ID format
        if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
            raise ValueError(f"Invalid YouTube video ID format: {video_id}")
        
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Ensure directory exists
        video_dir = os.path.join(settings.tmp_dir, video_id)
        os.makedirs(video_dir, exist_ok=True)
        
        output = os.path.join(video_dir, f"audio_{video_id}.mp3")
        if os.path.exists(output):
            # Verify the file is valid
            if os.path.getsize(output) > 0:
                print(f"Using cached audio file: {output}")
                return output
            else:
                # Remove invalid file
                print(f"Removing invalid cached file: {output}")
                os.remove(output)
    
        print(f"Downloading audio from YouTube: {video_url}")
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        if not audio_stream:
            raise ValueError(f"No audio stream found for video ID: {video_id}")
        
        print(f"Audio stream found: {audio_stream.mime_type}, itag: {audio_stream.itag}")
        
        # Download with original filename first
        temp_filename = audio_stream.default_filename
        print(f"Downloading to temporary file: {temp_filename}")
        downloaded_file = audio_stream.download(output_path=video_dir)
        print(f"Downloaded file: {downloaded_file}")
        
        # If the downloaded file is not MP3, convert it using ffmpeg
        if not downloaded_file.endswith('.mp3'):
            print(f"Converting {downloaded_file} to MP3 format")
            import subprocess
            try:
                result = subprocess.run([
                    'ffmpeg', '-i', downloaded_file, 
                    '-acodec', 'mp3', '-ab', '128k', 
                    output, '-y'
                ], check=True, capture_output=True, text=True)
                print(f"FFmpeg conversion successful")
                # Remove the original file
                os.remove(downloaded_file)
                print(f"Removed original file: {downloaded_file}")
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg error: {e.stderr}")
                raise ValueError(f"Failed to convert audio to MP3: {e}")
        else:
            # If it's already MP3, just rename it
            print(f"File is already MP3, renaming to: {output}")
            if downloaded_file != output:
                os.rename(downloaded_file, output)
        
        # Verify the final file exists and has content
        if not os.path.exists(output):
            raise ValueError(f"Final audio file does not exist: {output}")
        
        file_size = os.path.getsize(output)
        if file_size == 0:
            raise ValueError(f"Downloaded audio file is empty")
        
        print(f"Audio download completed successfully: {output} ({file_size} bytes)")
        return str(output)
    except Exception as e:
        raise RuntimeError(f"Error downloading audio {str(e)}")
