"""
Temporary File Management Service - Temporary file and directory management

This service provides functionality for managing temporary files and
directories during audio processing workflows.
"""

import shutil
from pathlib import Path
from typing import Optional
from core.logging import get_logger


class TempFileService:
    """Service for temporary file management"""

    def __init__(self, base_temp_dir: Optional[Path] = None):
        self.base_temp_dir = base_temp_dir or Path("/tmp")
        self.base_temp_dir.mkdir(exist_ok=True)
        self.logger = get_logger(f'services.{self.__class__.__name__}')

    def create_temp_dir(self, identifier: str) -> Path:
        """
        Create a temporary directory for a specific identifier.
        
        Args:
            identifier: Unique identifier for the temporary directory
            
        Returns:
            Path to the created temporary directory
        """
        temp_dir = self.base_temp_dir / identifier
        temp_dir.mkdir(exist_ok=True)
        self.logger.info(f"Created temporary directory: {temp_dir}")
        return temp_dir

    def cleanup_temp_files(self, identifier: str) -> None:
        """
        Clean up temporary files for a specific identifier.
        
        Args:
            identifier: Unique identifier for the temporary files
        """
        try:
            temp_dir = self.base_temp_dir / identifier
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                self.logger.info(f"Cleaned up temporary files for: {identifier}")
        except Exception as e:
            self.logger.warning(f"Could not clean up temp files for {identifier}: {e}")

    def cleanup_file(self, file_path: Path) -> None:
        """
        Clean up a specific temporary file.
        
        Args:
            file_path: Path to the file to clean up
        """
        try:
            if file_path.exists():
                file_path.unlink()
                self.logger.debug(f"Cleaned up file: {file_path}")
        except Exception as e:
            self.logger.warning(f"Could not clean up file {file_path}: {e}")

    def get_temp_dir(self, identifier: str) -> Path:
        """
        Get the temporary directory path for a specific identifier.
        
        Args:
            identifier: Unique identifier for the temporary directory
            
        Returns:
            Path to the temporary directory
        """
        return self.base_temp_dir / identifier
