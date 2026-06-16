@echo off
echo Starting CAT Practice Platform...
echo Please wait for your browser to open.

:: Navigate to the directory where this batch file is located
cd /d "%~dp0"

:: Run the Streamlit application
python -m streamlit run app.py

pause
