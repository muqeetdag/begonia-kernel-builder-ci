---
name: ghidra
description: Use Ghidra (NSA software reverse engineering framework) to decompile binaries into C-like code and understand program logic without source. Use for static analysis of executables, firmware, and kernel images.
---

# Ghidra — Decompiler / SRE Framework

- Repo: https://github.com/NationalSecurityAgency/ghidra (Java, ~100K★)
- Purpose: Analyze malware and binaries; supports decompilation, disassembly, debugging.
- Install: download from https://ghidra-sre.org (needs JDK 21+).
  Headless: `ghidraRun` / `analyzeHeadless`.

## Workflow (from the notes — Example 4)

1. Download and install Ghidra from the official website.
2. Open Ghidra and create a new project.
3. Import the executable file (e.g. `crackme.exe`).
4. Ghidra analyzes the binary.
5. Open the **Decompile** window.
6. Read C-like code similar to the original source to understand logic.

```c
// What Ghidra shows (decompiled main)
int main(void) {
  char local_20 [20];
  printf("Enter key: ");
  scanf("%s", local_20);
  if (strcmp(local_20, "sagar123") == 0) {
    puts("Correct Key!");
  } else {
    puts("Wrong Key!");
  }
  return 0;
}
```

## Key takeaways

- Reverse engineering helps understand how a program works without source code.
- Ghidra can decompile binary files and show human-readable code.
- You can find important information: passwords, keys, logic, and algorithms.
- This example is for learning and security research only.
- Always use reverse engineering legally and ethically.

## Begonia kernel use

Import `Image.gz-dtb` (or the raw `Image` after `gunzip`) into Ghidra,
search decompiled code for `BYNb`, `driver_loader_builtin_init`, and the
ioctl handler `dev_ioctl` (magic `0x803`) to verify the built-in loader
landed in the image.
