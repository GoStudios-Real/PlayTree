"""Register PlayTree Discord to auto-start with Windows"""
import winreg
import os
import sys

BATCH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_all.bat")
PYTHON = r"C:\Users\RhysC\AppData\Local\Programs\Python\Python312\python.exe"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def add_autostart():
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE,
    )
    winreg.SetValueEx(
        key,
        "PlayTreeDiscord",
        0,
        winreg.REG_SZ,
        f'"{BATCH}"',
    )
    winreg.CloseKey(key)
    print(f"Auto-start registered: {BATCH}")


def remove_autostart():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.DeleteValue(key, "PlayTreeDiscord")
        winreg.CloseKey(key)
        print("Auto-start removed")
    except FileNotFoundError:
        print("Auto-start was not registered")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "remove":
        remove_autostart()
    else:
        add_autostart()
