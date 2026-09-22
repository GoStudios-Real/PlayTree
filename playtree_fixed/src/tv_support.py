import pygame
import os
import sys

IS_MOBILE = sys.platform in ("android", "ios") or hasattr(sys, "getandroidapilevel")

TV_KEYWORDS = [
    "eko home tv", "eko tv", "google tv", "android tv", "apple tv",
    "fire tv", "roku", "samsung tv", "lg tv", "sony tv", "hisense",
    "tcl tv", "vizio", "sharp tv", "panasonic tv", "tv box",
    "set-top box", "smart tv", "chromecast",
]


def detect_tv_mode():
    if IS_MOBILE:
        if sys.platform == "android" or hasattr(sys, "getandroidapilevel"):
            return True
        return False

    if sys.platform != "win32":
        return False

    try:
        import subprocess
        result = subprocess.run(
            ["wmic", "desktopmonitor", "get", "name"],
            capture_output=True, timeout=5, creationflags=0x08000000
        )
        monitor_name = result.stdout.decode(errors="ignore").lower()
        for kw in TV_KEYWORDS:
            if kw in monitor_name:
                return True
    except Exception:
        pass

    try:
        import subprocess
        result = subprocess.run(
            ["powershell", "-Command",
             "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"],
            capture_output=True, timeout=5, creationflags=0x08000000
        )
        gpu_name = result.stdout.decode(errors="ignore").lower()
        for kw in TV_KEYWORDS:
            if kw in gpu_name:
                return True
    except Exception:
        pass

    try:
        hostname = os.environ.get("COMPUTERNAME", "").lower()
        for kw in ["eko", "tv", "smart", "android"]:
            if kw in hostname:
                return True
    except Exception:
        pass

    if os.environ.get("PLAYTREE_TV_MODE", "").strip():
        return True

    return False


def get_tv_info():
    info = {
        "is_tv": False,
        "tv_type": "Unknown",
        "resolution": "1920x1080",
        "overscan补偿": 0.05,
        "controller_only": False,
    }

    if IS_MOBILE:
        info["is_tv"] = True
        if sys.platform == "android" or hasattr(sys, "getandroidapilevel"):
            info["tv_type"] = "Android Device"
        elif sys.platform == "ios":
            info["tv_type"] = "iOS Device"
        try:
            info_obj = pygame.display.Info()
            w, h = info_obj.current_w, info_obj.current_h
            info["resolution"] = f"{w}x{h}"
            info["overscan补偿"] = 0.0
        except Exception:
            pass
        return info

    info["is_tv"] = detect_tv_mode()

    if info["is_tv"] and sys.platform == "win32":
        try:
            import subprocess
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"],
                capture_output=True, timeout=5, creationflags=0x08000000
            )
            gpu = result.stdout.decode(errors="ignore").strip().lower()
            for kw, tv_type in [
                ("eko", "EKO HOME TV"), ("google", "Google TV"),
                ("android", "Android TV"), ("apple", "Apple TV"),
                ("fire", "Amazon Fire TV"), ("roku", "Roku TV"),
                ("samsung", "Samsung Smart TV"), ("lg", "LG Smart TV"),
            ]:
                if kw in gpu:
                    info["tv_type"] = tv_type
                    break
        except Exception:
            pass

        if info["tv_type"] == "Unknown":
            for kw, tv_type in [
                ("eko", "EKO HOME TV"), ("google", "Google TV"),
                ("android", "Android TV"), ("apple", "Apple TV"),
            ]:
                hostname = os.environ.get("COMPUTERNAME", "").lower()
                if kw in hostname:
                    info["tv_type"] = tv_type
                    break

    try:
        info_obj = pygame.display.Info()
        w, h = info_obj.current_w, info_obj.current_h
        info["resolution"] = f"{w}x{h}"
        if w <= 1280 and h <= 720:
            info["overscan补偿"] = 0.0
        else:
            info["overscan补偿"] = 0.04
    except Exception:
        pass

    try:
        info["controller_only"] = pygame.joystick.get_count() > 0
    except Exception:
        pass

    return info


def get_controller_name():
    try:
        if pygame.joystick.get_count() > 0:
            joy = pygame.joystick.Joystick(0)
            name = joy.get_name().lower()
            for kw, label in [
                ("xbox", "Xbox Controller"), ("xinput", "Xbox Controller"),
                ("dualshock", "PS Controller"), ("dualsense", "PS5 Controller"),
                ("switch", "Switch Pro Controller"),
                ("eko", "EKO HOME TV Remote"),
                ("google", "Google TV Remote"),
                ("android", "Android TV Remote"),
                ("apple", "Apple TV Remote"),
                ("fire", "Fire TV Remote"),
                ("roku", "Roku Remote"),
            ]:
                if kw in name:
                    return label
            return joy.get_name()
    except Exception:
        pass
    return None
