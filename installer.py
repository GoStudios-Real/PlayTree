import sys
import os
import shutil
import subprocess
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox

APP_NAME = "PLAYTREE"
EXE_NAME = "PLAYTREE.exe"


def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    # normalize separators
    return os.path.join(base, *rel.replace("\\", "/").split("/"))


def bundle_file(rel):
    rel = rel.replace("\\", "/")
    cand = [
        resource_path(rel),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), *rel.split("/")),
    ]
    for c in cand:
        if os.path.exists(c):
            return c
    return cand[0]


def get_desktop_path():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as k:
            v, _ = winreg.QueryValueEx(k, "Desktop")
            if os.path.isdir(v):
                return v
    except Exception:
        pass
    p = os.path.join(os.path.expanduser("~"), "Desktop")
    if os.path.isdir(p):
        return p
    return os.path.join(os.path.expanduser("~"), "Desktop")


def get_startmenu_path():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as k:
            v, _ = winreg.QueryValueEx(k, "Programs")
            if os.path.isdir(v):
                return v
    except Exception:
        pass
    p = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs")
    return p


def kill_process_for_file(filepath):
    exe = os.path.basename(filepath)
    try:
        subprocess.run(["taskkill", "/F", "/IM", exe], capture_output=True, check=False)
    except Exception:
        pass


def safe_copy(src, dst):
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    if os.path.exists(dst):
        kill_process_for_file(dst)
        try:
            os.chmod(dst, 0o666)
        except Exception:
            pass
        subprocess.run(["attrib", "-r", "-h", "-s", dst], check=False)
        try:
            os.remove(dst)
        except PermissionError:
            import time
            time.sleep(0.5)
            try:
                os.remove(dst)
            except Exception as e:
                raise PermissionError(f"Cannot overwrite {dst} — close {os.path.basename(dst)} and try again: {e}")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy(src, dst)


def create_shortcut(target, shortcut_path, icon_path, description=""):
    # Remove old shortcut that may be read-only
    if os.path.exists(shortcut_path):
        try:
            os.chmod(shortcut_path, 0o666)
        except Exception:
            pass
        subprocess.run(["attrib", "-r", "-h", "-s", shortcut_path], check=False)
        try:
            os.remove(shortcut_path)
        except Exception:
            pass
    os.makedirs(os.path.dirname(shortcut_path), exist_ok=True)

    # PowerShell single-quote escaping: ' -> ''
    def ps_esc(s):
        return s.replace("'", "''")

    # Use persistent icon if temp, otherwise copy already handled
    icon_to_use = icon_path

    ps_content = f"""$ErrorActionPreference='Stop'
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut('{ps_esc(shortcut_path)}')
$sc.TargetPath = '{ps_esc(target)}'
$sc.WorkingDirectory = '{ps_esc(os.path.dirname(target))}'
$sc.Description = '{ps_esc(description)}'
if (Test-Path '{ps_esc(icon_to_use)}') {{ $sc.IconLocation = '{ps_esc(icon_to_use)}' }}
$sc.Save()
"""
    ps1 = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ps1", delete=False, encoding="utf-8") as f:
            f.write(ps_content)
            ps1 = f.name
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            # fallback without icon (icon path may be bad)
            ps_noicon = f"""$ErrorActionPreference='Stop'
$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut('{ps_esc(shortcut_path)}')
$sc.TargetPath = '{ps_esc(target)}'
$sc.WorkingDirectory = '{ps_esc(os.path.dirname(target))}'
$sc.Description = '{ps_esc(description)}'
$sc.Save()
"""
            with open(ps1, "w", encoding="utf-8") as f:
                f.write(ps_noicon)
            result2 = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1],
                capture_output=True, text=True, timeout=15
            )
            if result2.returncode != 0:
                raise RuntimeError(result2.stderr.strip() or result.stderr.strip() or "powershell shortcut failed")
        return True
    except Exception as e:
        print(f"shortcut failed {shortcut_path}: {e}")
        return False
    finally:
        if ps1 and os.path.exists(ps1):
            try:
                os.remove(ps1)
            except Exception:
                pass


def set_folder_icon(folder, icon_path):
    os.makedirs(folder, exist_ok=True)
    ini = os.path.join(folder, "desktop.ini")
    if os.path.exists(ini):
        subprocess.run(["attrib", "-s", "-h", "-r", ini], check=False)
        try:
            os.chmod(ini, 0o666)
        except Exception:
            pass
        try:
            os.remove(ini)
        except Exception:
            pass
    subprocess.run(["attrib", "-r", folder], check=False)
    try:
        with open(ini, "w", encoding="utf-8") as f:
            f.write("[.ShellClassInfo]\r\n")
            f.write(f"IconResource={icon_path},0\r\n")
            f.write("ConfirmFileOp=0\r\n")
        subprocess.run(["attrib", "+h", "+s", ini], check=False)
    except PermissionError:
        try:
            if os.path.exists(ini):
                os.chmod(ini, 0o666)
            with open(ini, "w", encoding="utf-8") as f:
                f.write("[.ShellClassInfo]\r\n")
                f.write(f"IconResource={icon_path},0\r\n")
            subprocess.run(["attrib", "+h", "+s", ini], check=False)
        except Exception:
            pass
    subprocess.run(["attrib", "+r", folder], check=False)


class Installer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} Setup")
        try:
            self.iconbitmap(resource_path("assets/installer.ico"))
        except Exception:
            pass
        self.geometry("500x360")
        self.install_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", APP_NAME)

        tk.Label(self, text=f"{APP_NAME} Setup", font=("Segoe UI", 16, "bold")).pack(pady=12)
        tk.Label(self, text="Install PLAYTREE and extra files to:").pack()

        self.path_var = tk.StringVar(value=self.install_dir)
        row = tk.Frame(self)
        row.pack(pady=6, padx=20, fill="x")
        tk.Entry(row, textvariable=self.path_var).pack(side="left", fill="x", expand=True)
        tk.Button(row, text="Browse...", command=self.browse).pack(side="left", padx=6)

        self.status = tk.Label(self, text="", fg="green", wraplength=460, justify="center")
        self.status.pack(pady=4)

        tk.Button(self, text="Install", bg="#3c78dc", fg="white", padx=20, command=self.install).pack(pady=10)
        tk.Button(self, text="Exit", command=self.destroy).pack()

    def browse(self):
        d = filedialog.askdirectory(initialdir=self.path_var.get())
        if d:
            self.path_var.set(d)

    def install(self):
        dest = self.path_var.get().strip().strip('"').strip("'")
        if not dest:
            messagebox.showerror("Error", "Please choose an install folder.")
            return
        try:
            os.makedirs(dest, exist_ok=True)
            # check writable
            test_file = os.path.join(dest, "_write_test.tmp")
            try:
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
            except PermissionError:
                raise PermissionError(f"No write permission for {dest}. Try a different folder or run as Administrator.")

            # Copy icons to dest first so shortcuts point to persistent files (fixes temp _MEI bug) — installer.py:84
            for ico in ("app.ico", "doc.ico"):
                src = bundle_file(os.path.join("assets", ico))
                if os.path.exists(src):
                    try:
                        safe_copy(src, os.path.join(dest, ico))
                    except Exception:
                        shutil.copy(src, os.path.join(dest, ico))
            app_ico = os.path.join(dest, "app.ico") if os.path.exists(os.path.join(dest, "app.ico")) else bundle_file(os.path.join("assets", "app.ico"))
            doc_ico = os.path.join(dest, "doc.ico") if os.path.exists(os.path.join(dest, "doc.ico")) else bundle_file(os.path.join("assets", "doc.ico"))

            # Main application — handle locked exe
            exe_src = bundle_file(EXE_NAME)
            exe_dst = os.path.join(dest, EXE_NAME)
            if os.path.exists(exe_src):
                safe_copy(exe_src, exe_dst)
            else:
                raise FileNotFoundError(f"Bundled {EXE_NAME} not found.")
            # GoConsoleOS + Launcher + Cloud + FootBall editions
            for extra_exe in ["PlayTree GoConsoleOS.exe", "PlayTree Launcher.exe", "PlayTree Cloud Gaming.exe", "PlayTree FootBall.exe", "PLAYTREE.xvc"]:
                src2 = bundle_file(extra_exe)
                if os.path.exists(src2):
                    try:
                        safe_copy(src2, os.path.join(dest, extra_exe))
                    except:
                        try: shutil.copy(src2, os.path.join(dest, extra_exe))
                        except: pass

            # Extra bundled files
            extras_dir = os.path.join(dest, f"{APP_NAME} Extras")
            os.makedirs(extras_dir, exist_ok=True)
            for fname in ("README.txt", "LICENSE.txt", "NOTES.txt"):
                src = bundle_file(os.path.join("extra", fname))
                if os.path.exists(src):
                    try:
                        safe_copy(src, os.path.join(extras_dir, fname))
                    except Exception:
                        shutil.copy(src, os.path.join(extras_dir, fname))

            # Custom folder icon for the extras folder
            set_folder_icon(extras_dir, doc_ico)

            # Desktop shortcut to the app
            desktop = get_desktop_path()
            start = get_startmenu_path()
            os.makedirs(start, exist_ok=True)

            ok1 = create_shortcut(exe_dst, os.path.join(desktop, f"{APP_NAME}.lnk"), app_ico, APP_NAME)
            ok2 = create_shortcut(exe_dst, os.path.join(start, f"{APP_NAME}.lnk"), app_ico, APP_NAME)
            # Shortcuts for GoConsoleOS + Launcher
            gce = os.path.join(dest, "PlayTree GoConsoleOS.exe")
            if os.path.exists(gce):
                create_shortcut(gce, os.path.join(desktop, "PlayTree GoConsoleOS.lnk"), app_ico, "PlayTree GoConsoleOS")
                create_shortcut(gce, os.path.join(start, "PlayTree GoConsoleOS.lnk"), app_ico, "PlayTree GoConsoleOS")
            launch = os.path.join(dest, "PlayTree Launcher.exe")
            if os.path.exists(launch):
                create_shortcut(launch, os.path.join(desktop, "PlayTree Launcher.lnk"), app_ico, "PlayTree Launcher")
                create_shortcut(launch, os.path.join(start, "PlayTree Launcher.lnk"), app_ico, "PlayTree Launcher")
            cloud = os.path.join(dest, "PlayTree Cloud Gaming.exe")
            if os.path.exists(cloud):
                create_shortcut(cloud, os.path.join(desktop, "PlayTree Cloud Gaming.lnk"), app_ico, "PlayTree Cloud Gaming")
                create_shortcut(cloud, os.path.join(start, "PlayTree Cloud Gaming.lnk"), app_ico, "PlayTree Cloud Gaming")
            fb = os.path.join(dest, "PlayTree FootBall.exe")
            if os.path.exists(fb):
                create_shortcut(fb, os.path.join(desktop, "PlayTree FootBall.lnk"), app_ico, "PlayTree FootBall")
                create_shortcut(fb, os.path.join(start, "PlayTree FootBall.lnk"), app_ico, "PlayTree FootBall")

            # Extra-file shortcuts with the doc icon
            for fname in ("README.txt", "LICENSE.txt", "NOTES.txt"):
                fpath = os.path.join(extras_dir, fname)
                if os.path.exists(fpath):
                    create_shortcut(fpath, os.path.join(desktop, f"{APP_NAME} {fname}.lnk"), doc_ico, f"{APP_NAME} {fname}")

            if not ok1 and not ok2:
                raise RuntimeError("Shortcuts could not be created. Check antivirus or Desktop permissions.")

            self.status.config(text=f"Installed to {dest}", fg="green")
            messagebox.showinfo("Done", f"{APP_NAME} installed to:\n{dest}\n\nYou can launch from Desktop or Start Menu.")
        except Exception as e:
            # Show short message, not raw powershell dump
            msg = str(e).strip()
            if len(msg) > 600:
                msg = msg[:600] + "..."
            # hide scary powershell internals from user
            if "powershell" in msg.lower() and "CreateShortcut" in msg:
                msg = "Failed to create shortcuts. Try running as Administrator or check antivirus blocks PowerShell."
            self.status.config(text=f"Error: {msg}", fg="red")
            messagebox.showerror("Error", msg)


if __name__ == "__main__":
    Installer().mainloop()
