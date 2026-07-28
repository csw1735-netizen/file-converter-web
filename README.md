# 파일 변환 도구

Excel, CSV, TXT 파일을 브라우저에 드래그해 표준 CSV로 변환하는 로컬 웹앱입니다.

## 지원 기능

- Excel (`.xlsx`, `.xlsm`, `.xls`) → CSV
- 여러 Excel 시트 → 시트별 CSV가 담긴 ZIP
- TXT/TSV/CSV → UTF-8 BOM CSV
- 쉼표, 탭, 세미콜론, 파이프 구분자 자동 감지
- UTF-8, CP949, EUC-KR 등 문자 인코딩 지원

## 실행

가장 쉬운 방법은 `run_app.bat`을 더블클릭하는 것입니다. 필요한 구성 요소가 없으면 처음 한 번 자동으로 설치하고 앱을 실행합니다.

직접 명령어로 실행하려면 Python 3.10 이상을 설치한 뒤 PowerShell에서 이 폴더로 이동해 실행합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

브라우저가 열리면 파일을 끌어 놓아 사용할 수 있습니다.

## 웹에서 사용

이 프로젝트는 Streamlit Community Cloud에 바로 배포할 수 있습니다. GitHub 저장소를 연결하고 실행 파일로 `app.py`를 선택하면 됩니다.

업로드된 파일은 변환 요청을 처리하는 동안 서버 메모리에서 읽으며, 앱 코드에서 별도 파일이나 데이터베이스로 저장하지 않습니다. 민감한 자료는 조직의 보안 정책을 먼저 확인한 뒤 업로드하세요.

## 참고

- CSV 출력은 한글이 Excel에서 깨지지 않도록 UTF-8 BOM 형식입니다.
- Excel의 수식과 셀 서식은 CSV 변환 시 보존되지 않고 현재 셀 값만 저장됩니다.
- 대용량 파일은 브라우저 메모리의 영향을 받을 수 있습니다.
