
# GoConsoleOS Touch + on-screen keyboard/controls + BT Xbox/PS/Switch/GoConsole
PRODUCT_PACKAGES += \
    PlayTreeTouchService \
    GoConsoleKeyboard \
    android.hardware.touchscreen.multitouch.jazzhand.xml

PRODUCT_COPY_FILES += \
    vendor/goconsole/config/bt/xbox.cfg:system/etc/bluetooth/xbox.cfg \
    vendor/goconsole/config/bt/ps.cfg:system/etc/bluetooth/ps.cfg \
    vendor/goconsole/config/bt/switch.cfg:system/etc/bluetooth/switch.cfg \
    vendor/goconsole/config/bt/goconsole.cfg:system/etc/bluetooth/goconsole.cfg

# Touch
PRODUCT_PROPERTY_OVERRIDES += \
    ro.input.noresponse=0 \
    persist.sys.touch.size=12

# PlayTree prebuilt
PRODUCT_COPY_FILES += \
    vendor/goconsole/prebuilt/PlayTree.apk:system/app/PlayTree/PlayTree.apk
