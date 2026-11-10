@echo off
cd /d "%~dp0"
title WMT Brief Video Pictures
echo Dang khoi dong WMT Brief Video Pictures...
streamlit run app.py --server.port 8507 --server.headless false
pause
