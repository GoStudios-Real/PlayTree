#!/bin/sh
# Build the PlayTree executable on macOS (PyInstaller).
# Requires: Python 3.10+, pip
set -e
cd "$(dirname "$0")"
python3 -m pip install --upgrade pip
python3 -m pip install pygame numpy psutil pyinstaller
python3 -m PyInstaller --clean --noconfirm PLAYTREE.spec
echo "Built: dist/PLAYTREE"
echo "Codesign (optional): codesign --deep --force -s - dist/PLAYTREE"
