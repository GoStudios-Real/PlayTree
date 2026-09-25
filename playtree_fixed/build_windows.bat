@echo off
REM Build the PlayTree executable on Windows (PyInstaller).
cd /d "%~dp0"
python -m pip install --upgrade pip
python -m pip install pygame numpy psutil pyinstaller
python -m PyInstaller --clean --noconfirm PLAYTREE.spec
echo Built: dist\PLAYTREE.exe
