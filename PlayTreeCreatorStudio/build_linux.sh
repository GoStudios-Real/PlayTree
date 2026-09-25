#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 -m pip install --upgrade pygame pyinstaller
python3 -m PyInstaller --onefile --noconfirm --name PlayTreeCreatorStudio --add-data "runtime.py:." creator_studio.py
echo "Built: dist/PlayTreeCreatorStudio"
