---
name: binary-ninja
description: Use Binary Ninja for interactive binary analysis — disassembly, decompilation, and debugging with a modern UI and Python API. Use when Ghidra/radare2 are not enough and a polished interactive platform is needed.
---

# Binary Ninja — Interactive Binary Analysis

- Repo (API/examples): https://github.com/Vector35/binaryninja-api (C++ + Python API)
- Purpose: Interactive binary analysis — disassembly, decompilation, debugging.
- Install: https://binary.ninja — free evaluation version available for learning.
- Language: C++ (with Python API).

## When to use

- You want a modern, interactive alternative to IDA/Ghidra.
- You need a Python API to automate analysis (`binaryninja` Python module).
- You are analyzing complex binaries and want clean decompilation views.

## Workflow

1. Open the binary in Binary Ninja.
2. Let auto-analysis finish.
3. Use the graph / linear disassembly views to follow control flow.
4. Switch to the decompiler view for C-like pseudocode.
5. Use the Python console / API to script searches (strings, xrefs, patterns).

```python
import binaryninja
bv = binaryninja.load("target.exe")
for s in bv.get_strings():
    print(hex(s.start), s.value)
```

## Notes

- Free version is available for learning; full features need a license.
- Combine with Ghidra (free, open source) — Ghidra first, Binary Ninja
  when you need its interactive UI / API.
- Always use legally and for learning purposes only.
