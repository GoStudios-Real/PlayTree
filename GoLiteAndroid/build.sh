#!/bin/bash
# GoConsole Lite Android 12-16 — PlayTree for Nokia G21/G22/T10/T20/T21 + more
set -e
for codename in g21 g22 t10 t20 t21; do
  echo "=== $codename Android 16 Lite ==="
  source build/envsetup.sh
  lunch lineage_${codename}-userdebug
  mka bootimage systemimage -j$(nproc)
  echo "out/target/product/$codename/boot.img + system.img ready"
done
