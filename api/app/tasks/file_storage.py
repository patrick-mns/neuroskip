from pathlib import Path
from celery_app.config import celery_app


@celery_app.task
def store_audio_file(file_str: str, hash_id: str):
    """
    Store audio file content to the temporary directory.
    
    Args:
        file_str: Audio file content as Latin-1 encoded string
        hash_id: Unique hash identifier for the file
    
    Returns:
        str: Path to the stored file
    """
    file_content = file_str.encode("latin1")  

    folder = Path(f"/tmp/{hash_id}")
    folder.mkdir(parents=True, exist_ok=True)

    file_path = folder / f"audio_{hash_id}.mp3"
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return str(file_path)
