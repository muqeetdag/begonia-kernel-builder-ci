#!/bin/bash
set -e

echo "=== Installing dependencies ==="
sudo apt-get update
sudo apt-get install -y build-essential bc gcc-aarch64-linux-gnu gcc-arm-linux-gnueabi libssl-dev libelf-dev flex bison zip curl git

echo "=== Cloning Proton Clang 13 ==="
if [ ! -d "clang" ]; then
  git clone --depth=1 https://github.com/kdrag0n/proton-clang.git clang
fi

echo "=== Cloning Begonia Kernel Source 4.14.186 ==="
if [ ! -d "kernel_src" ]; then
  git clone --depth=1 https://github.com/WuXing90/begonia_kernel_dev.git -b Suzaku-bka kernel_src
fi

echo "=== Injecting Driver Loader Source ==="
cp driver_loader_builtin.c kernel_src/drivers/misc/
if ! grep -q "driver_loader_builtin.o" kernel_src/drivers/misc/Makefile; then
  echo "obj-y += driver_loader_builtin.o" >> kernel_src/drivers/misc/Makefile
fi

echo "=== Applying FolkPatch Symbol Defconfig ==="
cat << 'DEFCONFIG_EOF' >> kernel_src/arch/arm64/configs/begonia_user_defconfig
CONFIG_KALLSYMS=y
CONFIG_KALLSYMS_ALL=y
CONFIG_KALLSYMS_BASE_RELATIVE=y
CONFIG_KPROBES=y
CONFIG_HAVE_KPROBES=y
CONFIG_OVERLAY_FS=y
CONFIG_OVERLAY_FS_REDIRECT_DIR=y
CONFIG_OVERLAY_FS_INDEX=y
DEFCONFIG_EOF

echo "=== Compiling Kernel Image.gz-dtb ==="
cd kernel_src
export PATH="$GITHUB_WORKSPACE/clang/bin:$PATH"
export ARCH=arm64
export SUBARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
export CROSS_COMPILE_ARM32=arm-linux-gnueabi-

# Fix compiler flags for clang cross target
export CC=clang
export CLANG_TRIPLE=aarch64-linux-gnu-

make O=out begonia_user_defconfig
make -j$(nproc --all) O=out CC=clang CLANG_TRIPLE=aarch64-linux-gnu- Image.gz-dtb
cp out/arch/arm64/boot/Image.gz-dtb $GITHUB_WORKSPACE/Image.gz-dtb
cd $GITHUB_WORKSPACE

echo "=== Packaging AnyKernel3 Flashable Zip ==="
git clone --depth=1 https://github.com/osm0sis/AnyKernel3.git AnyKernel3
sed -i 's/do.devicecheck=1/do.devicecheck=0/' AnyKernel3/anykernel.sh
sed -i 's/device.name1=.*/device.name1=begonia/' AnyKernel3/anykernel.sh
cp Image.gz-dtb AnyKernel3/Image.gz-dtb
cd AnyKernel3
zip -r -q -9 $GITHUB_WORKSPACE/Begonia-4.14.186-DriverLoader-FolkPatch.zip *
echo "=== Done! Flashable Zip created successfully ==="
