"""
Integration Tests

통합 테스트: file_scanner와 excel_processor의 연동 테스트
실제 Excel 파일을 사용하여 전체 워크플로우를 테스트합니다.
"""

import pytest
from pathlib import Path
import tempfile
import os
import shutil

from src.file_scanner import FileScanner, list_excel_files
from src.excel_processor import ExcelProcessor, get_excel_summary


class TestFileScannerExcelProcessorIntegration:
    """FileScanner와 ExcelProcessor 통합 테스트"""

    def setup_method(self):
        """테스트 설정"""
        self.scanner = FileScanner()
        self.processor = ExcelProcessor()
        self.sample_dir = Path("sample")

        # sample 디렉토리가 존재하는지 확인
        if not self.sample_dir.exists():
            pytest.skip("sample 디렉토리가 존재하지 않습니다.")

    def test_scan_and_process_real_excel_files(self):
        """실제 Excel 파일들을 스캔하고 처리하는 통합 테스트"""
        # 1. sample 디렉토리에서 Excel 파일들 스캔
        scan_result = list_excel_files(str(self.sample_dir))

        # 스캔 결과 검증
        assert scan_result["success"] is True
        assert "files" in scan_result
        assert len(scan_result["files"]) > 0

        # 2. 스캔된 파일들 중 일부를 선택하여 처리
        excel_files = scan_result["files"]
        test_files = excel_files[:3]  # 처음 3개 파일만 테스트

        for file_info in test_files:
            file_path = file_info["file_path"]

            # 3. 파일이 실제로 존재하는지 확인
            assert Path(file_path).exists()

            # 4. ExcelProcessor로 파일 정보 추출
            summary_result = get_excel_summary(file_path)

            # 5. 결과 검증
            assert summary_result["success"] is True
            assert "worksheets" in summary_result
            assert "file_name" in summary_result
            assert "file_size" in summary_result

            assert summary_result["file_name"] == Path(file_path).name
            assert summary_result["file_size"] > 0
            assert summary_result["file_format"] in [".xlsx", ".xls", ".xlsm", ".xlsb"]

    def test_scan_with_pattern_and_process(self):
        """패턴으로 파일을 검색하고 처리하는 통합 테스트"""
        # 1. 특정 패턴으로 파일 검색 (예: "2020"이 포함된 파일들)
        pattern_result = self.scanner.find_excel_files_by_name(
            str(self.sample_dir), "*2020*", recursive=True
        )

        if pattern_result["success"] and pattern_result["total_files"] > 0:
            # 2. 검색된 파일들 처리
            for file_info in pattern_result["files"]:
                file_path = file_info["file_path"]

                # 3. 파일 처리
                summary_result = get_excel_summary(file_path)

                # 4. 결과 검증
                assert summary_result["success"] is True
                assert "2020" in Path(file_path).name

    def test_scan_and_search_content(self):
        """파일을 스캔하고 내용을 검색하는 통합 테스트"""
        # 1. sample 디렉토리에서 Excel 파일들 스캔
        scan_result = list_excel_files(str(self.sample_dir))

        if scan_result["success"] and len(scan_result["files"]) > 0:
            # 2. 첫 번째 파일 선택
            first_file = scan_result["files"][0]
            file_path = first_file["file_path"]

            # 3. 파일 내용 검색 (일반적인 키워드들)
            search_terms = ["data", "table", "value", "total", "sum"]

            for term in search_terms:
                search_result = self.processor.search_in_worksheet(
                    Path(file_path), term, case_sensitive=False
                )

                # 검색 결과가 있든 없든 정상적으로 처리되어야 함
                assert "success" in search_result
                assert "search_term" in search_result
                assert search_result["search_term"] == term

    def test_error_handling_integration(self):
        """에러 처리 통합 테스트"""
        # 1. 존재하지 않는 디렉토리 스캔
        invalid_scan = list_excel_files("/nonexistent/directory")
        assert invalid_scan["success"] is False

        # 2. 존재하지 않는 파일 처리
        invalid_file = get_excel_summary("/nonexistent/file.xlsx")
        assert invalid_file["success"] is False

        # 3. 잘못된 파일 형식 처리
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(b"not an excel file")

        try:
            invalid_format = get_excel_summary(tmp_path)
            # Excel이 아닌 파일은 처리 실패해야 함
            assert invalid_format["success"] is False
        finally:
            os.unlink(tmp_path)

    def test_workflow_complete_integration(self):
        """완전한 워크플로우 통합 테스트"""
        # 1. 디렉토리 스캔
        scan_result = list_excel_files(str(self.sample_dir))

        if not scan_result["success"] or len(scan_result["files"]) == 0:
            pytest.skip("처리할 Excel 파일이 없습니다.")

        # 2. 파일 선택 및 메타데이터 수집
        selected_file = scan_result["files"][0]
        file_path = selected_file["file_path"]

        # 3. 파일 요약 정보 추출
        summary = get_excel_summary(file_path)
        assert summary["success"] is True

        # 4. 시트 정보 확인
        worksheets = summary["worksheets"]
        if worksheets:
            first_sheet = worksheets[0]
            sheet_name = first_sheet["name"]

            # 5. 특정 시트의 데이터 읽기
            sheet_data = self.processor.read_worksheet_data(Path(file_path), sheet_name)
            assert sheet_data["success"] is True

            # 6. 데이터가 있으면 샘플 데이터 확인
            if sheet_data["rows"] and len(sheet_data["rows"]) > 0:
                sample_data = sheet_data["rows"][:5]  # 처음 5행만
                assert len(sample_data) > 0

    def test_large_file_handling(self):
        """큰 파일 처리 테스트"""
        # sample 디렉토리에서 가장 큰 파일 찾기
        scan_result = list_excel_files(str(self.sample_dir))

        if not scan_result["success"] or len(scan_result["files"]) == 0:
            pytest.skip("처리할 Excel 파일이 없습니다.")

        # 파일 크기순으로 정렬
        files_by_size = sorted(
            scan_result["files"], key=lambda x: x.get("file_size", 0), reverse=True
        )

        # 가장 큰 파일 처리
        largest_file = files_by_size[0]
        file_path = largest_file["file_path"]

        # 파일 처리 (타임아웃 없이)
        summary = get_excel_summary(file_path)
        assert summary["success"] is True

        # 파일 크기 확인
        assert summary["file_size"] > 0


class TestDataConsistencyIntegration:
    """데이터 일관성 통합 테스트"""

    def setup_method(self):
        """테스트 설정"""
        self.scanner = FileScanner()
        self.processor = ExcelProcessor()
        self.sample_dir = Path("sample")

    def test_file_metadata_consistency(self):
        """파일 메타데이터 일관성 테스트"""
        scan_result = list_excel_files(str(self.sample_dir))

        if not scan_result["success"]:
            pytest.skip("파일 스캔에 실패했습니다.")

        for file_info in scan_result["files"][:5]:  # 처음 5개 파일만 테스트
            file_path = file_info["file_path"]

            # FileScanner에서 얻은 정보
            scanner_size = file_info.get("file_size", 0)
            scanner_name = file_info.get("file_name", "")

            # ExcelProcessor에서 얻은 정보
            summary = get_excel_summary(file_path)

            if summary["success"]:
                processor_size = summary["file_size"]
                processor_name = summary["file_name"]

                # 크기와 이름이 일치해야 함
                assert scanner_size == processor_size, f"파일 크기 불일치: {file_path}"
                assert scanner_name == processor_name, f"파일 이름 불일치: {file_path}"

    def test_sheet_count_consistency(self):
        """시트 개수 일관성 테스트"""
        scan_result = list_excel_files(str(self.sample_dir))

        if not scan_result["success"]:
            pytest.skip("파일 스캔에 실패했습니다.")

        for file_info in scan_result["files"][:3]:  # 처음 3개 파일만 테스트
            file_path = file_info["file_path"]

            # ExcelProcessor로 시트 정보 가져오기
            summary = get_excel_summary(file_path)

            if summary["success"]:
                worksheets = summary["worksheets"]
                sheet_count = len(worksheets)

                # 시트 개수가 0보다 커야 함 (빈 Excel 파일이 아닌 경우)
                if summary["file_size"] > 1000:  # 1KB 이상인 파일만
                    assert sheet_count > 0, f"시트가 없는 파일: {file_path}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
