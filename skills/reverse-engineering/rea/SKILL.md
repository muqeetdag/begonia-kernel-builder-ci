---
name: rea
description: Use REA (Reverse Engineer Anything) by morluto — an MCP + CLI + agents toolkit that lets an AI agent analyze binaries, apps, and runtime behavior from high level down to the binary level. Use when you want agent-assisted reverse engineering.
---

# REA — Reverse Engineer Anything (MCP + Agents)

- Repo: https://github.com/morluto/rea (TypeScript, MIT, ~8.9K★ as shown)
- Website: https://rea.tools · Discord: https://discord.gg/GkcryMnJDM
- npm: `rea-agents` (binaries: `rea`, `rea-agents`)
- Type: CLI tool + MCP server + pre-built agents.

## What it is

REA is a powerful open-source tool that helps reverse-engineer binaries,
applications, and runtime behavior. It uses MCP (Model Context Protocol)
and provides multiple tools and agents to analyze programs from high level
down to the binary level.

Main components:

- `rea.tools` → collection of tools used for analysis
- `rea-agents` → pre-built agents for specific tasks
- CLI → command-line interface for easy usage
- Documentation → guides, examples, and showcase

## Installation

Requires Node.js. Then:

```bash
npx rea-agents setup
```

This installs all required dependencies and sets up the REA environment.
You can now use REA from the terminal: run `rea --help` to get started.

## Basic usage

```bash
rea --help          # Show available commands
rea analyze <binary>  # Analyze a binary file
rea agent --list    # List available agents
rea run <program>   # Run analysis on a program
```

Commands: `analyze` (analyze a binary or application), `inspect` (app
overview with evidence), `compare` (compare two binaries),
`annotate-native-function`, `inspect-binary-layout`, and ~60 more.
(The notes' `rea show` does not exist in 6.7.0 — use `inspect`.)

## Example workflow

```
Target Program (program.exe)
  → REA Tools (analyze, disassemble, inspect, debug)
  → Analysis Output (assembly code, strings, functions, behavior)
  → Understand Program Logic
```

## Practical guide (from the notes)

```bash
git clone https://github.com/morluto/rea.git
cd rea
npm install
npx rea-agents setup        # optional: AI agents for advanced analysis
```

Build a sample program to analyze:

```c
#include <stdio.h>
int main() {
  printf("Hello REA!\n");
  return 0;
}
```

```bash
gcc test.c -o test.exe
npx rea analyze test.exe       # needs Ghidra/IDA/Hopper (deep provider)
npx rea inspect test.exe       # overview with evidence
```

REA shows functions, strings, imports, exports, control flow, and more.

## Real scenarios

1. **Malware analysis** — `npx rea analyze sample.exe`, then
   `npx rea inspect sample.exe` to see functions and imported APIs
   (e.g. `KERNEL32.dll → CreateFileA, ReadFile, CloseHandle`).
2. **Web application binary** — works on Linux ELF binaries too, not just
   Windows: `npx rea analyze app`.
3. **AI agents (optional)** — `npx rea-agents setup`:
   Binary File → REA Agent → Analysis Report (functions, strings,
   behavior, summary).

## Best practices

- Always use REA legally and ethically.
- Do not analyze malware on your main system — use a VM.
- Read the documentation for advanced features.
- Combine REA with other tools (Ghidra, radare2) for better analysis.
- Use it for learning, research, and security purposes only.

## Verified CLI (REA 6.7.0, installed in this repo)

The notes' commands are simplified. The real CLI is:

```bash
rea --help                      # ~60 commands
rea inspect <path>              # app overview with evidence
rea inspect-binary-layout <p>   # ELF/Mach-O layout, no execution
rea inspect-native-api <p> <address>
rea annotate-native-function <p> <procedure>
rea analyze <path>              # deep analysis
```

Deep analysis (`analyze`, `inspect`) needs one *deep* provider —
Ghidra, IDA, Hopper, or Kuna. Without one you get
`provider_unavailable … candidate_ids: ghidra,hopper,ida,kuna`.
`inspect-binary-layout` only needs a Python with
`pwntools==4.15.0 pyelftools==0.33 unicorn==2.1.2`:

```bash
export REA_PWNTOOLS_PYTHON=$HOME/.local/rea-venv/bin/python
export GHIDRA_INSTALL_DIR=$HOME/.local/ghidra     # enables `rea analyze`
```

The installer sets both up (`scripts/install-skills.sh`), Ghidra being
opt-in via `WITH_GHIDRA=1`.

## Begonia kernel use

```bash
# 1) triage without a deep provider
rabin2 -I begonia_dtb.bin; strings -n 6 begonia_dtb.bin | grep -i mt6785

# 2) once Ghidra is installed, let REA drive it
export GHIDRA_INSTALL_DIR=$HOME/.local/ghidra
rea analyze Image.gz-dtb
rea inspect-binary-layout Image.gz-dtb
```

REA detects the architecture, extracts functions and strings, and can
generate a control-flow graph — then an REA agent can explain the
`/dev/BYNb` ioctl handler in plain language.
