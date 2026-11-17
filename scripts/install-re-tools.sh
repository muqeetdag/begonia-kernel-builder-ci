#!/usr/bin/env bash
# Install ONLY the reverse-engineering tools from the screenshots:
# radare2, Frida, REA (+ Ghidra/x64dbg/Binary Ninja notes).
# Thin wrapper around install-skills.sh --re-only.
set -e
cd "$(dirname "$0")/.."
exec ./scripts/install-skills.sh --re-only "$@"
