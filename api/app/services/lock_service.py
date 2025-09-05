"""
Lock Service - Distributed task locking using Redis

This service provides functionality for managing distributed locks
to prevent concurrent execution of tasks.
"""

from core.filesystem import delete_dir_tmp
import redis
from core.config import settings

LOCK_PREFIX = "task_lock:"
redis_client = redis.from_url(settings.redis_string, decode_responses=True)


def is_task_locked(task_id: str) -> bool:
    """
    Check if a task is currently locked.
    
    Args:
        task_id (str): The ID of the task to check
        
    Returns:
        bool: True if the task is locked, False otherwise
    """
    lock_key = f"{LOCK_PREFIX}{task_id}"
    return redis_client.exists(lock_key) == 1


def lock_task(task_id: str) -> None:
    """
    Lock a task to prevent concurrent execution.
    
    Args:
        task_id (str): The ID of the task to lock
        
    Raises:
        ValueError: If the task is already locked
    """
    lock_key = f"{LOCK_PREFIX}{task_id}"
    if not redis_client.set(lock_key, "locked", ex=3600, nx=True):
        raise ValueError(f"Task {task_id} is already locked.")


def unlock_task(task_id: str) -> bool:
    """
    Unlock a task and clean up associated temporary files.
    
    Args:
        task_id (str): The ID of the task to unlock
        
    Returns:
        bool: True if the task was successfully unlocked, False otherwise
    """
    delete_dir_tmp(task_id) 
    lock_key = f"{LOCK_PREFIX}{task_id}"
    return redis_client.delete(lock_key) == 1
