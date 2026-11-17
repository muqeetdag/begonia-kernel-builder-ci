---
name: radare2
description: Use radare2 (r2) for command-line binary analysis — disassemble, inspect functions, strings, imports/exports, and analyze binaries on any architecture including ARM64 kernel images. Use when a fast terminal-based RE tool is needed.
---

# radare2 — CLI Reverse Engineering

- Repo: https://github.com/radareorg/radare2 (C, ~25K★)
- Purpose: Disassemble, debug, analyze binaries.
- Install: `sudo apt install radare2` (Debian/Ubuntu) or build from source.
  Verify: `r2 -v`

## Core commands

```bash
r2 -A ./target            # open + auto-analyze (aaa)
rabin2 -I ./target        # file info (arch, bits, OS)
rabin2 -i ./target        # imports
rabin2 -s ./target        # symbols / functions
rabin2 -z ./target        # strings
rabin2 -S ./target        # sections
```

Inside `r2`:

```
aaa            # analyze all
afl            # list functions
pdf @ main     # disassemble function
px 64 @ addr   # hex dump
iz             # strings
ii             # imports
axt <addr>     # xrefs to address
```

## Begonia kernel use

```bash
# Inspect the built kernel image (ARM64)
rabin2 -I Image.gz-dtb
rabin2 -z Image.gz-dtb | grep -i -E "BYNb|driver_loader|0x803"
r2 -A -q -c 'afl; q' Image.gz-dtb
```

## Tips

- Beginners can learn basic commands easily — it's a UNIX-like framework.
- Combine with `rea` (MCP agent) for AI-assisted analysis of the same binary.
- Always analyze in a VM / safe environment for untrusted samples.
