# PlayTree Lite Android 12 13 — fully touch + BT
$(call inherit-product, $$(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, vendor/goconsole/config/playtree_touch.mk)
PRODUCT_NAME := playtree_t10
PRODUCT_PACKAGES += PlayTree PlayTree_GoConsoleOS PlayTree_Launcher
PRODUCT_COPY_FILES += \
    vendor/goconsole/prebuilt/PlayTree.apk:system/app/PlayTree/PlayTree.apk
# BT controllers — Xbox One X/S Series X/S, PS4/5, Switch 1/2, GoConsole Phone
PRODUCT_PACKAGES += android.hardware.bluetooth@1.0-service
PRODUCT_PROPERTY_OVERRIDES += \
    bluetooth.device.class=0x0005C0 \
    persist.vendor.btstack.enable=true
