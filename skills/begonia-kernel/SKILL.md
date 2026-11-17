---
name: begonia-kernel
description: Project skill for this repo — reverse-engineer and verify the Begonia (Redmi Note 8 Pro, MT6785) 4.14.186 kernel image built by this CI, including the built-in /dev/BYNb driver loader (ioctl 0x803). Use when analyzing Image.gz-dtb, driver_loader_builtin.c, or the AnyKernel3 flashable zip.
---

# Begonia Kernel — Project RE Skill

Device: Redmi Note 8 Pro (`begonia`, MT6785) · Kernel: 4.14.186
Build: GitHub Actions (`.github/workflows/build_kernel.yml`) + `build.sh`
Output: `Begonia-4.14.186-driver-loader-DRKMUQEETT.zip` (AnyKernel3)

## What this repo builds

1. Clones the Kaeru kernel source (`Saikrishna1504/kernel_xiaomi_mt6785`,
   branch `kaeru`), patches version to 4.14.186.
2. Injects `driver_loader_builtin.c` into `drivers/misc/` as a **built-in**
   (`obj-y`), exposing `/dev/BYNb` (mode 0666) with ioctl magic `0x803`
   returning base address `0x70000000` (for the AngryMod Driver Loader).
3. Enables FolkPatch symbols: `KALLSYMS_ALL`, `KPROBES`, `OVERLAY_FS`.
4. Builds `Image.gz`, appends `begonia_dtb.bin` → `Image.gz-dtb`.
5. Packages an AnyKernel3 zip (device check disabled, `begonia`).

## RE workflow for the built image

### 1. Identify & collect

```bash
ls -lh Image.gz-dtb Begonia-*.zip
file Image.gz-dtb
sha256sum Image.gz-dtb
```

### 2. Static analysis (pick one tool)

```bash
# radare2 — fast CLI triage
rabin2 -I Image.gz-dtb
rabin2 -z Image.gz-dtb | grep -i -E "BYNb|driver_loader|uevents_records"
r2 -A -q -c 'afl~driver_loader; q' Image.gz-dtb

# REA — agent-assisted (MCP)
export GHIDRA_INSTALL_DIR=$HOME/.local/ghidra        # deep provider
export REA_PWNTOOLS_PYTHON=$HOME/.local/rea-venv/bin/python
rea analyze Image.gz-dtb
rea inspect-binary-layout Image.gz-dtb

# Ghidra — decompile the loader
# Import Image.gz-dtb (or gunzipped Image) → search decompiled code for
# driver_loader_builtin_init / dev_ioctl / 0x803
```

### 3. Verify the driver loader landed

Check for all of these in strings/symbols:

- `BYNb` (device name) and `uevents_records` (class name)
- `driver_loader_builtin_init` / `driver_loader_builtin_exit`
- ioctl magic `0x803` in `dev_ioctl`
- Return value `0x70000000`

```bash
strings Image.gz-dtb | grep -E "BYNb|uevents_records|driver_loader"
# With kallsyms: nm / kallsyms lookup for driver_loader_builtin_init
```

### 4. Dynamic analysis (on device)

```bash
adb shell ls -l /dev/BYNb          # expect crw-rw-rw-
adb shell "echo test > /dev/BYNb"  # write returns len, no crash
# Frida (userspace): instrument the loader app while kernel runs underneath
frida-ps -U
```

### 5. Document & verify

- Record: kernel version (`4.14.186-driver-loader`), defconfig deltas,
  DTB hash, and REA/Ghidra findings in the release notes.
- Rebuild via Actions and diff the new image's strings against the old one.

## Safety

- Only flash on `begonia` (MT6785). Wrong DTB = bootloop risk.
- Analyze untrusted images in a VM; never run unknown binaries on your
  main system.
- RE for learning/research only, with authorization.
