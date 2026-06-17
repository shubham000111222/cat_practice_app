@echo off
echo Installing PyInstaller if not present...
pip install pyinstaller

echo.
echo Building CAT Practice Platform EXE...
echo This will take several minutes. Do not close this window!

:: We use --onedir instead of --onefile because Streamlit is massive (200MB+).
:: --onefile would take 15-30 seconds to silently extract to a temp folder EVERY TIME the user double-clicks it.
:: --onedir creates a folder with the lightning-fast EXE inside.
python -m PyInstaller --noconfirm ^
  --onedir ^
  --name "CAT_Practice_Platform" ^
  --add-data "app.py;." ^
  --add-data "pages;pages/" ^
  --add-data "utils;utils/" ^
  --add-data "database;database/" ^
  --add-data "images;images/" ^
  --collect-all streamlit ^
  run_app.py

echo.
echo Build complete! Your EXE is located in the 'dist/CAT_Practice_Platform' folder.
