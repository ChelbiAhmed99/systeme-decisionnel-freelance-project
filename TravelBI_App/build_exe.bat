@echo off
REM Executable Windows autonome dans dist\TravelBI\
cd /d "%~dp0"
call .venv\Scripts\activate
pip install pyinstaller
pyinstaller --noconfirm --windowed --name TravelBI --collect-all lightgbm --collect-all xgboost --collect-all catboost app.py
xcopy /E /I /Y models dist\TravelBI\models
xcopy /E /I /Y data dist\TravelBI\data
xcopy /E /I /Y assets dist\TravelBI\assets
copy /Y config.json dist\TravelBI\config.json
echo.
echo Executable : dist\TravelBI\TravelBI.exe
pause
