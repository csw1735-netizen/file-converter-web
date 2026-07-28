@echo off
chcp 65001 >nul
cd /d "%~dp0"

python -c "import streamlit, pandas, openpyxl, xlrd" >nul 2>&1
if errorlevel 1 (
    echo 필요한 구성 요소를 처음 한 번 설치합니다...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo 설치에 실패했습니다. 인터넷 연결과 Python 설치 상태를 확인해 주세요.
        pause
        exit /b 1
    )
)

echo 파일 변환 도구를 시작합니다. 브라우저가 잠시 후 열립니다.
python -m streamlit run app.py
pause
