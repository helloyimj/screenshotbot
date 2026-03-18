@echo off
chcp 65001 >nul
title 스크린샷 커맨드 센터 가동기

echo ===================================================
echo   [스크린샷 커맨드 센터] 구동을 시작합니다...
echo ===================================================
echo.

echo [1/3] 필수 부품(라이브러리)을 확인하고 설치합니다...
pip install -r requirements.txt -q

echo.
echo [2/3] 전용 브라우저 엔진을 준비합니다...
playwright install chromium

echo.
echo [3/3] 시스템을 가동합니다! (인터넷 창이 열릴 때까지 기다려주세요)
echo.
streamlit run main.py

pause