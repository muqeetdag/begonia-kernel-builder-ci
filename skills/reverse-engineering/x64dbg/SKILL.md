---
name: x64dbg
description: Use x64dbg, the open-source Windows debugger, for dynamic analysis — set breakpoints, step through code, and find hardcoded passwords/keys at strcmp comparisons. Use for Windows executables and crackme-style challenges.
---

# x64dbg — Windows Debugger

- Repo: https://github.com/x64dbg/x64dbg (C++, ~50K★)
- Purpose: Debug and analyze Windows binaries. Good for beginners.
- Install: Windows only — download from https://x64dbg.com.
  (On Linux, use GDB / radare2 debugger instead.)

## Workflow (from the notes — Examples 3 & 5)

1. Open x64dbg → File → Open → select `password.exe` / `login.exe`.
2. The program loads with disassembly code.
3. Run the program in x64dbg (F9), enter any password, click Check.
4. The program stops at the point where it compares the entered password.
5. Analyze the instruction:

```asm
004013F6  push  offset aMaster123   ; "Master123"  ← hardcoded password
004013F8  push  [ebp+userInput]     ; entered password
004013FE  call  strcmp
00401403  test  eax, eax
00401405  jne   00401420            ; jump if not equal
```

`strcmp` compares two strings: same → returns 0, different → non-zero.

6. Verify in memory: open the **Strings window** — the same password is
   visible (`Master123`, `Sagar123`, …).
7. Run the program with the correct password → success dialog.

## Key takeaways

- Reverse engineering helps find hidden information inside a program.
- Tools like x64dbg let you analyze the program while it is running.
- You can find hardcoded strings, passwords, keys, etc.
- Real software uses more complex techniques (encryption, hashing),
  but this example shows the basic concept.
- Always use reverse engineering for learning, research, and security
  purposes only — ethically.

## Begonia kernel use

x64dbg is Windows-only, so for the ARM64 Begonia kernel use the Linux
equivalents: `gdb-multiarch` with `aarch64-linux-gnu-gdb`, or radare2's
debugger (`r2 -d`). The same breakpoint-on-`strcmp` technique applies to
any userspace helper binary.
