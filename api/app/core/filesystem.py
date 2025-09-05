import os
import shutil
import hashlib
import re
from core.config import settings


def delete_dir_tmp(dirname: str):
    """
    Delete a directory from the temporary directory.
    
    Args:
        dirname: Name of the directory to delete
    """
    dirpath = os.path.join(settings.tmp_dir, dirname)
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)


def generate_sha256_from_file(path: str) -> str:
    """
    Generate SHA256 hash from a file.
    
    Args:
        path: Path to the file
        
    Returns:
        SHA256 hash as hexadecimal string
    """
    hash_sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):  # Lê em blocos de 8KB
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def is_sha256(id: str) -> bool:
    """
    Check if a string is a valid SHA256 hash.
    
    Args:
        id: String to validate
        
    Returns:
        True if string is a valid SHA256 hash, False otherwise
    """
    return bool(re.match(r'^[a-f0-9]{64}$', id))
