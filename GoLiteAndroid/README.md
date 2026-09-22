# GoLiteAndroid — Lite Android 12-16 PlayTree for Nokia G21/G22/T10/T20/T21 + more
GoConsoleOS Lite — fully touchscreen + on-screen keyboard + on-screen controls + Bluetooth:
- Xbox One X/S, Xbox Series X/S
- PlayStation 4/5 (DualShock/DualSense)
- Nintendo Switch 1/2 Joy-Con/Pro
- GoConsoleOS 1 Phone Touchscreen Controller (virtual)

Devices: Nokia G21 (T606), G22 (T606), T10 (T606), T20 (T610), T21 (T612) — add more in device/nokia/*

Build:
```
repo init -u https://github.com/LineageOS/android.git -b lineage-20.0
git clone https://github.com/GoStudios-Real/PlayTree GoLiteAndroid
source build/envsetup.sh
lunch lineage_g21-userdebug && mka bootimage
```

Touch: vendor/goconsole/config/playtree_touch.mk — on-screen keyboard via PlayTree/src/touch_controls.py VirtualKeyboard ported to Android InputMethod.

BT: vendor/goconsole/config/bt/*.cfg — Xbox/PS/Switch/GoConsole
