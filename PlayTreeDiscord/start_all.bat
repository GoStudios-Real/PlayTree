@echo off
title PlayTree Discord Suite
color 0A
echo ============================================
echo    PlayTree Discord Suite - GoStudios
echo ============================================
echo.
echo Starting Rich Presence...
start "PlayTree Rich Presence" cmd /c "cd /d "%~dp0" && "C:\Users\RhysC\AppData\Local\Programs\Python\Python312\python.exe" rich_presence.py"
timeout /t 3 /nobreak >nul
echo Starting Discord Bot...
start "PlayTree Discord Bot" cmd /c "cd /d "%~dp0" && "C:\Users\RhysC\AppData\Local\Programs\Python\Python312\python.exe" bot.py"
echo.
echo ============================================
echo  Both started!
echo  - Rich Presence: Shows on your profile
echo  - Bot: Slash commands in server
echo ============================================
echo.
echo Press any key to close this window...
pause >nul
