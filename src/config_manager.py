"""
Configuration Manager Module

MCP 서버의 설정을 관리하는 모듈
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ConfigManager:
    """설정 관리 클래스"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """설정 파일을 로드합니다."""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                logger.info(f"설정 파일 로드됨: {self.config_path}")
                return config
            else:
                logger.warning(f"설정 파일이 없습니다: {self.config_path}")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """기본 설정을 반환합니다."""
        return {
            "server": {
                "name": "excel-search-mcp",
                "version": "0.1.0",
                "description": "Excel 파일 검색 및 처리를 위한 MCP 서버",
            },
            "security": {
                "allowed_directories": [
                    str(Path.home() / "Documents"),
                    str(Path.home() / "Desktop"),
                    str(Path.home() / "Downloads"),
                ],
                "allow_subdirectories": True,
                "max_search_depth": 10,
            },
            "excel": {
                "supported_extensions": [".xlsx", ".xls", ".xlsm", ".xlsb"],
                "max_file_size_mb": 100,
                "max_files_per_search": 1000,
            },
        }

    def get_work_directory(self) -> str:
        """작업 디렉토리를 반환합니다."""
        return self.config.get("work_directory", str(Path.home() / "Documents"))

    def get_supported_extensions(self) -> List[str]:
        """지원하는 Excel 확장자를 반환합니다."""
        return self.config.get("excel", {}).get(
            "supported_extensions", [".xlsx", ".xls", ".xlsm", ".xlsb"]
        )

    def get_max_file_size_mb(self) -> int:
        """최대 파일 크기(MB)를 반환합니다."""
        return self.config.get("excel", {}).get("max_file_size_mb", 100)

    def get_max_files_per_search(self) -> int:
        """검색당 최대 파일 수를 반환합니다."""
        return self.config.get("excel", {}).get("max_files_per_search", 1000)

    def get_recursive_search(self) -> bool:
        """재귀 검색 여부를 반환합니다."""
        return self.config.get("excel", {}).get("recursive_search", True)

    def is_path_within_work_directory(self, path: str) -> bool:
        """경로가 작업 디렉토리 내에 있는지 확인합니다."""
        try:
            target_path = Path(path).resolve()
            work_dir = Path(self.get_work_directory()).resolve()

            # 정확히 일치하는 경우
            if target_path == work_dir:
                return True

            # 하위 디렉토리인 경우
            try:
                target_path.relative_to(work_dir)
                return True
            except ValueError:
                # 상위 디렉토리임
                return False

        except Exception as e:
            logger.error(f"경로 검증 중 오류 발생: {path} - {e}")
            return False

    def _save_config(self) -> bool:
        """설정을 파일에 저장합니다."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"설정 파일 저장됨: {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"설정 파일 저장 실패: {e}")
            return False


# 전역 설정 관리자 인스턴스
config_manager = ConfigManager()
