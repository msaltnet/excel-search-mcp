"""
사용 예제 테스트

실제 사용 시나리오를 시뮬레이션하는 예제 테스트
"""

import pytest
from pathlib import Path

from src.file_scanner import FileScanner, list_excel_files
from src.excel_processor import ExcelProcessor, get_excel_summary, search_in_excel


class TestUsageExamples:
    """실제 사용 예제 테스트"""

    def setup_method(self):
        """테스트 설정"""
        self.scanner = FileScanner()
        self.processor = ExcelProcessor()
        self.sample_dir = Path("sample")

        if not self.sample_dir.exists():
            pytest.skip("sample 디렉토리가 존재하지 않습니다.")

    def test_example_1_find_and_analyze_excel_files(self):
        """예제 1: Excel 파일들을 찾고 분석하기"""
        print("\n=== 예제 1: Excel 파일들을 찾고 분석하기 ===")

        # 1. sample 디렉토리에서 모든 Excel 파일 찾기
        result = list_excel_files(str(self.sample_dir))

        if result["success"]:
            print(f"발견된 Excel 파일 수: {result['total_files']}")

            # 2. 각 파일의 기본 정보 출력
            for i, file_info in enumerate(result["files"][:3]):  # 처음 3개만
                file_path = file_info["file_path"]
                print(f"\n파일 {i+1}: {Path(file_path).name}")
                print(f"  크기: {file_info['file_size']:,} bytes")

                # 3. 파일 상세 정보 가져오기
                summary = get_excel_summary(file_path)
                if summary["success"]:
                    print(f"  시트 수: {summary['total_worksheets']}")
                    print(f"  형식: {summary['file_format']}")

                    # 4. 시트 목록 출력
                    for sheet in summary["worksheets"][:3]:  # 처음 3개 시트만
                        print(
                            f"    - {sheet['name']}: {sheet['row_count']}행 x {sheet['column_count']}열"
                        )
        else:
            print(f"파일 스캔 실패: {result['error']}")

    def test_example_2_search_files_by_pattern(self):
        """예제 2: 패턴으로 파일 검색하기"""
        print("\n=== 예제 2: 패턴으로 파일 검색하기 ===")

        # 1. "2020"이 포함된 파일들 검색
        pattern_result = self.scanner.find_excel_files_by_name(
            str(self.sample_dir), "*2020*", recursive=True
        )

        if pattern_result["success"]:
            print(f"'2020'이 포함된 파일 수: {pattern_result['total_files']}")

            for file_info in pattern_result["files"][:2]:  # 처음 2개만
                file_path = file_info["file_path"]
                print(f"  - {Path(file_path).name}")
        else:
            print(f"패턴 검색 실패: {pattern_result['error']}")

    def test_example_3_search_content_in_excel(self):
        """예제 3: Excel 파일 내용 검색하기"""
        print("\n=== 예제 3: Excel 파일 내용 검색하기 ===")

        # 1. 파일 하나 선택
        result = list_excel_files(str(self.sample_dir))

        if result["success"] and len(result["files"]) > 0:
            file_path = result["files"][0]["file_path"]
            print(f"검색 대상 파일: {Path(file_path).name}")

            # 2. "data"라는 단어 검색
            search_result = search_in_excel(file_path, "data", case_sensitive=False)

            if search_result["success"]:
                print(f"검색 결과: {search_result['total_matches']}개 매치")

                # 3. 매치된 결과 출력 (처음 3개만)
                for match in search_result["matches"][:3]:
                    print(
                        f"  - 시트: {match['worksheet_name']}, "
                        f"셀: {match['cell_address']}, "
                        f"값: {match['cell_value'][:50]}..."
                    )
            else:
                print(f"검색 실패: {search_result['error']}")

    def test_example_4_complete_workflow(self):
        """예제 4: 완전한 워크플로우"""
        print("\n=== 예제 4: 완전한 워크플로우 ===")

        # 1. 파일 스캔
        scan_result = list_excel_files(str(self.sample_dir))

        if not scan_result["success"]:
            print(f"스캔 실패: {scan_result['error']}")
            return

        print(f"1. 스캔 완료: {scan_result['total_files']}개 파일 발견")

        # 2. 가장 큰 파일 선택
        if scan_result["files"]:
            largest_file = max(
                scan_result["files"], key=lambda x: x.get("file_size", 0)
            )
            file_path = largest_file["file_path"]
            print(
                f"2. 분석 대상: {Path(file_path).name} ({largest_file['file_size']:,} bytes)"
            )

            # 3. 파일 상세 분석
            summary = get_excel_summary(file_path)

            if summary["success"]:
                print(f"3. 파일 분석 완료:")
                print(f"   - 시트 수: {summary['total_worksheets']}")
                print(f"   - 파일 형식: {summary['file_format']}")

                # 4. 첫 번째 시트의 데이터 샘플 확인
                if summary["worksheets"]:
                    first_sheet = summary["worksheets"][0]
                    print(f"4. 첫 번째 시트 '{first_sheet['name']}' 분석:")
                    print(
                        f"   - 크기: {first_sheet['row_count']}행 x {first_sheet['column_count']}열"
                    )
                    print(
                        f"   - 데이터 존재: {'예' if first_sheet['has_data'] else '아니오'}"
                    )

                    # 5. 시트 데이터 읽기 (처음 3행만)
                    sheet_data = self.processor.read_worksheet_data(
                        Path(file_path), first_sheet["name"], max_rows=3
                    )

                    if sheet_data["success"] and sheet_data["rows"]:
                        print(f"5. 데이터 샘플 (처음 3행):")
                        for i, row in enumerate(sheet_data["rows"]):
                            print(f"   행 {i+1}: {row[:3]}...")  # 처음 3개 컬럼만
            else:
                print(f"3. 파일 분석 실패: {summary['error']}")

    def test_example_5_error_handling(self):
        """예제 5: 에러 처리"""
        print("\n=== 예제 5: 에러 처리 ===")

        # 1. 존재하지 않는 디렉토리
        result = list_excel_files("/nonexistent/directory")
        print(f"존재하지 않는 디렉토리: {'실패' if not result['success'] else '성공'}")

        # 2. 존재하지 않는 파일
        summary = get_excel_summary("/nonexistent/file.xlsx")
        print(f"존재하지 않는 파일: {'실패' if not summary['success'] else '성공'}")

        # 3. 잘못된 파일 형식
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(b"not an excel file")

        try:
            invalid_summary = get_excel_summary(tmp_path)
            print(
                f"잘못된 파일 형식: {'실패' if not invalid_summary['success'] else '성공'}"
            )
        finally:
            import os

            os.unlink(tmp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s 옵션으로 print 출력 보기
