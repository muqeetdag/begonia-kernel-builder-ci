---
name: reverse-engineering
description: Master reverse-engineering workflow — analyze an existing product, software, or system to understand how it works and how it was designed. Use for binary analysis, malware analysis, kernel image inspection, and understanding unknown programs. Covers static, dynamic, and hybrid analysis.
---

# Reverse Engineering — Master Skill

> Source: @mastercode.sagar handwritten notes (Instagram carousel, 14 slides).

## Definition

Reverse engineering is the process of analyzing an existing product,
software, or system to understand how it works and how it was designed.

## Why it is used

- Understand the internal working of a system
- Learn the design and architecture
- Find bugs and security weaknesses
- Maintain or improve old software
- Recover missing documentation

## Basic process (5 steps)

1. Collect the existing product or software
2. Analyze its components and behavior
3. Identify structure, logic, and relationships
4. Create diagrams or documentation
5. Verify findings through testing

## How it works (4 stages)

1. **Analyze the target** — collect the software/device/file, understand its
   purpose and environment.
2. **Examine & extract** — study structure/code/data inside; use tools to view
   internal components (binaries, resources, memory).
3. **Understand the logic** — how different parts work together; identify
   algorithms, functions, and data flow.
4. **Document & verify** — create documentation/diagrams; test findings to
   confirm understanding.

Flow: `Target Software/File → Analyze & Extract → Understand Logic → Document & Verify`

## Steps (detailed)

1. **Identify the target** — determine the software/file/device to analyze;
   understand its purpose and environment.
2. **Collect the target** — obtain a copy of the program/binary/hardware;
   ensure it is legal and safe to analyze.
3. **Analyze the target** — use disassemblers and debuggers; study code,
   structure, and behavior.
4. **Understand the logic** — reconstruct flow, algorithms, and data
   structures; create diagrams/notes.
5. **Document the findings** — write down observations, code flow, and
   functions; create clear documentation for future reference.

## Types of analysis

| Type | What | Tools | Helps to |
|------|------|-------|----------|
| **Static** | Analyze code without executing it | IDA Pro, Ghidra, PEiView | Study structure, functions, strings |
| **Dynamic** | Analyze while the program is running | x64dbg, OllyDbg | Observe real-time behavior, memory, network |
| **Hybrid** | Combination of both | — | Deeper understanding; complex software / malware |

## Types of reverse engineering

- **Software** — studies code, binaries, and program behavior
- **Hardware** — studies physical components and circuits
- **Database** — discovers schema, tables, and relationships

## Common targets

- **Executable files (.exe, .dll)** — analyze program behavior and logic
- **Mobile applications (APK)** — study app features and security
- **Firmware** — understand embedded systems (routers, IoT devices)
- **Documents / file formats** — learn internal structure (PDF, DOCX)
- **Hardware devices** — analyze circuits and firmware inside devices

## Tools

| Tool | Converts / allows |
|------|-------------------|
| Disassemblers | Binary code → assembly code |
| Debuggers | Step-by-step execution and analysis |
| Decompilers | Assembly → high-level code (e.g. C) |
| Hex editors | View and modify raw binary data |
| Network analyzers | Analyze network traffic and protocols |
| Emulator / VM | Run and test software in a safe environment |

> The choice of tool depends on the type of target and purpose of analysis.
> See the sub-skills: [radare2](radare2/SKILL.md), [ghidra](ghidra/SKILL.md),
> [x64dbg](x64dbg/SKILL.md), [binary-ninja](binary-ninja/SKILL.md),
> [frida](frida/SKILL.md), [rea](rea/SKILL.md).

## Applications

- Malware analysis and cybersecurity
- Software debugging and patching
- Recovering lost source code
- Understanding proprietary formats
- Security research and vulnerability analysis
- Compatibility with older systems
- Learning and research purposes
- Hardware and embedded system analysis

## Example

Studying an application to understand its features and data flow when
original documentation is unavailable.

## Important note

Reverse engineering should be performed only with proper authorization and
respect for laws, licenses, and privacy. Always use it for learning,
research, and security purposes only — and ethically.
