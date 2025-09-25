# 샘플 Excel 파일

이 디렉토리는 테스트용 샘플 Excel 파일들을 저장하는 곳입니다.

## 파일 구조

```
sample_excel_files/
├── README.md
├── sample1.xlsx          # 기본 샘플 파일
├── sample2.xlsx          # 다중 워크시트 샘플
├── large_file.xlsx       # 대용량 테스트 파일
└── old_format.xls        # 구형 Excel 형식
```

## 샘플 파일 설명

- **sample1.xlsx**: 기본적인 데이터가 포함된 간단한 Excel 파일
- **sample2.xlsx**: 여러 워크시트가 있는 복잡한 Excel 파일
- **large_file.xlsx**: 성능 테스트를 위한 대용량 파일
- **old_format.xls**: 구형 Excel 형식(.xls) 파일

## 사용 방법

테스트 시 이 디렉토리를 `directory_path`로 지정하여 Excel 파일 검색 기능을 테스트할 수 있습니다.

```python
arguments = {
    "directory_path": "./examples/sample_excel_files",
    "recursive": False
}
```
