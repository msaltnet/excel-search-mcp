"""
File Scanner Module

Module responsible for Excel file search and metadata collection
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .config_manager import config_manager

logger = logging.getLogger(__name__)

# Supported Excel file extensions (will be loaded from config)
EXCEL_EXTENSIONS = config_manager.get_supported_extensions()


class FileScanner:
    """Excel file search and metadata collection class"""

    def __init__(self):
        self.supported_extensions = set(config_manager.get_supported_extensions())
        self.config_manager = config_manager

    def is_excel_file(self, file_path: Path) -> bool:
        """Check if the file is an Excel file"""
        return file_path.suffix.lower() in self.supported_extensions

    def is_path_within_work_directory(self, path: str) -> bool:
        """Check if the path is within work directory"""
        return self.config_manager.is_path_within_work_directory(path)

    def validate_directory_path(self, directory_path: str) -> Dict[str, Any]:
        """Validate directory path and return validation result"""
        try:
            directory = Path(directory_path)

            # Check if path exists
            if not directory.exists():
                return {
                    "valid": False,
                    "error": f"Directory does not exist: {directory_path}",
                    "error_code": "DIRECTORY_NOT_FOUND",
                }

            # Check if it's a directory
            if not directory.is_dir():
                return {
                    "valid": False,
                    "error": f"Path is not a directory: {directory_path}",
                    "error_code": "NOT_A_DIRECTORY",
                }

            # Check if path is within work directory
            if not self.is_path_within_work_directory(directory_path):
                work_dir = self.config_manager.get_work_directory()
                return {
                    "valid": False,
                    "error": f"Directory access denied: {directory_path}. Work directory: {work_dir}",
                    "error_code": "ACCESS_DENIED",
                    "work_directory": work_dir,
                }

            return {
                "valid": True,
                "directory": str(directory.resolve()),
                "allowed": True,
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Path validation error: {str(e)}",
                "error_code": "VALIDATION_ERROR",
            }

    def get_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Collect file metadata"""
        try:
            stat = file_path.stat()
            return {
                "file_path": str(file_path.absolute()),
                "file_name": file_path.name,
                "file_size": stat.st_size,
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat()
                + "Z",
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat() + "Z",
                "extension": file_path.suffix.lower(),
            }
        except (OSError, PermissionError) as e:
            logger.warning(f"Failed to collect file metadata: {file_path} - {e}")
            return {
                "file_path": str(file_path.absolute()),
                "file_name": file_path.name,
                "file_size": 0,
                "modified_time": None,
                "created_time": None,
                "extension": file_path.suffix.lower(),
                "error": str(e),
            }

    def scan_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        max_files: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Search for Excel files in directory

        Args:
            directory_path: Directory path to search for Excel files
            recursive: Whether to search recursively in subdirectories
            max_files: Maximum number of files to return (None for unlimited)

        Returns:
            Search result dictionary
        """
        try:
            # Validate directory path first
            validation = self.validate_directory_path(directory_path)
            if not validation["valid"]:
                logger.warning(
                    f"Directory access denied: {directory_path} - {validation['error']}"
                )

                return {
                    "success": False,
                    "error": validation["error"],
                    "error_code": validation["error_code"],
                    "directory": directory_path,
                    "recursive": recursive,
                    "total_files": 0,
                    "files": [],
                    "work_directory": validation.get("work_directory", ""),
                }

            directory = Path(validation["directory"])

            logger.info(
                f"Excel file search started: {directory_path} (recursive: {recursive})"
            )

            excel_files = []
            scanned_count = 0

            # Set file search pattern
            if recursive:
                pattern = "**/*"
            else:
                pattern = "*"

            # Execute file search
            for file_path in directory.glob(pattern):
                scanned_count += 1

                # Check file count limit
                if max_files and len(excel_files) >= max_files:
                    logger.info(f"Maximum file count reached: {max_files}")
                    break

                # Check if it's an Excel file
                if file_path.is_file() and self.is_excel_file(file_path):
                    metadata = self.get_file_metadata(file_path)
                    excel_files.append(metadata)

            logger.info(
                f"Search completed: {len(excel_files)} Excel files found (total {scanned_count} files scanned)"
            )

            return {
                "success": True,
                "directory": directory_path,
                "total_files": len(excel_files),
                "scanned_files": scanned_count,
                "files": excel_files,
                "supported_extensions": list(self.supported_extensions),
            }

        except PermissionError as e:
            logger.error(f"Directory access permission error: {directory_path} - {e}")
            return {
                "success": False,
                "error": f"No permission to access directory: {directory_path}",
                "directory": directory_path,
                "total_files": 0,
                "files": [],
            }
        except Exception as e:
            logger.error(
                f"Error occurred during directory search: {directory_path} - {e}"
            )
            return {
                "success": False,
                "error": f"Error occurred during directory search: {str(e)}",
                "directory": directory_path,
                "total_files": 0,
                "files": [],
            }

    def find_excel_files_by_name(
        self, directory_path: str, filename_pattern: str, recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Search Excel files by filename pattern

        Args:
            directory_path: Directory path to search for Excel files
            filename_pattern: Filename pattern (supports wildcards)
            recursive: Whether to search recursively in subdirectories

        Returns:
            Search result dictionary
        """
        try:
            directory = Path(directory_path)

            if not directory.exists() or not directory.is_dir():
                return {
                    "success": False,
                    "error": f"Invalid directory: {directory_path}",
                    "directory": directory_path,
                    "pattern": filename_pattern,
                    "total_files": 0,
                    "files": [],
                }

            logger.info(
                f"Filename pattern search: {filename_pattern} in {directory_path}"
            )

            excel_files = []

            # Execute pattern search
            if recursive:
                search_pattern = f"**/{filename_pattern}"
            else:
                search_pattern = filename_pattern

            for file_path in directory.glob(search_pattern):
                if file_path.is_file() and self.is_excel_file(file_path):
                    metadata = self.get_file_metadata(file_path)
                    excel_files.append(metadata)

            logger.info(f"Pattern search completed: {len(excel_files)} files found")

            return {
                "success": True,
                "directory": directory_path,
                "pattern": filename_pattern,
                "total_files": len(excel_files),
                "files": excel_files,
            }

        except Exception as e:
            logger.error(f"Error occurred during pattern search: {e}")
            return {
                "success": False,
                "error": f"Error occurred during pattern search: {str(e)}",
                "directory": directory_path,
                "pattern": filename_pattern,
                "total_files": 0,
                "files": [],
            }


# Convenience functions
def list_excel_files(
    directory_path: str, recursive: bool = True, max_files: Optional[int] = None
) -> Dict[str, Any]:
    """Convenience function that returns Excel file list"""
    scanner = FileScanner()
    return scanner.scan_directory(directory_path, recursive, max_files)


def find_excel_files_by_name(
    directory_path: str, filename_pattern: str, recursive: bool = True
) -> Dict[str, Any]:
    """Convenience function to search Excel files by filename pattern"""
    scanner = FileScanner()
    return scanner.find_excel_files_by_name(directory_path, filename_pattern, recursive)
