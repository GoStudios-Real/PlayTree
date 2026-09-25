@echo off
cd /d "%~dp0"
python -m pip install --upgrade pygame pyinstaller
python -m PyInstaller --onefile --noconfirm --name PlayTreeCreatorStudio --add-data "runtime.py;." creator_studio.py
echo Built: dist\PlayTreeCreatorStudio.exe
