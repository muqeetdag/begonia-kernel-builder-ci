# Skills — Begonia Kernel Builder CI

All skills from the Instagram screenshots, installed as agent skills
(`SKILL.md` format — Claude Code / Codex / Cursor / ECC / REA compatible).

| # | Skill | Source (screenshot) | What it does |
|---|-------|---------------------|--------------|
| 1 | [reverse-engineering](reverse-engineering/SKILL.md) | @mastercode.sagar notes | Master RE workflow: identify → collect → analyze → understand → document |
| 2 | [radare2](reverse-engineering/radare2/SKILL.md) | GitHub Trending list | CLI disassembly / binary analysis (`r2`, `rabin2`, `radare2`) |
| 3 | [ghidra](reverse-engineering/ghidra/SKILL.md) | GitHub Trending list | NSA decompiler — binary → C-like code |
| 4 | [x64dbg](reverse-engineering/x64dbg/SKILL.md) | GitHub Trending list | Windows debugger — breakpoints, `strcmp` password checks |
| 5 | [binary-ninja](reverse-engineering/binary-ninja/SKILL.md) | GitHub Trending list | Interactive binary analysis platform |
| 6 | [frida](reverse-engineering/frida/SKILL.md) | GitHub Trending list | Dynamic instrumentation (Android / iOS / Windows) |
| 7 | [rea](reverse-engineering/rea/SKILL.md) | morluto/rea (8.9K★) | MCP reverse-engineering agent — `npx rea-agents setup` |
| 8 | [free-llm](free-llm/SKILL.md) | @aiwithshivang + reels | Master free-LLM workflow: pick provider → get key → plug in |
| 9 | [freellmapi](free-llm/freellmapi/SKILL.md) | tashfeenahmed/freellmapi | 87 free providers behind one `/v1` endpoint |
| 10 | [awesome-free-llm-apis](free-llm/awesome-free-llm-apis/SKILL.md) | freellm.net / mnfst list | 513+ free LLM APIs from 30 providers (Cohere, HF, Cloudflare, xAI, DeepSeek, OpenRouter, Alibaba…) |
| 11 | [ecc](free-llm/ecc/SKILL.md) | affaan-m/ECC (237K★ reel) | Agent harness — 72 agents, 327 skills, turns Claude into an AI agent |
| 12 | [freebuff](free-llm/freebuff/SKILL.md) | @matty.buff "sauce" reel | Free coding agent (CodebuffAI/freebuff) |
| 13 | [modal](free-llm/modal/SKILL.md) | @ezsnippet reel ($30 free) | Modal.com — free AI infra / GPU endpoints |
| 14 | [public-apis](free-llm/public-apis/SKILL.md) | @its_hunter_275 comment | public-apis/public-apis — collective free API list |
| 15 | [begonia-kernel](begonia-kernel/SKILL.md) | this repo | Project skill: RE the Begonia `Image.gz-dtb` + `/dev/BYNb` driver loader |

## Install everything

```bash
chmod +x scripts/install-skills.sh
./scripts/install-skills.sh            # full install (RE tools + npm agents + clones)
./scripts/install-skills.sh --light    # npm/pip only, skip apt + big clones (fast)
./scripts/install-skills.sh --re-only  # only reverse-engineering tools
./scripts/install-skills.sh --llm-only # only free-LLM skills
```

The installer syncs `skills/*/SKILL.md` into `.claude/skills/` (project)
and `~/.claude/skills/` (user) so Claude Code / Codex / Cursor pick them up,
installs the real tools (`radare2`, `frida-tools`, `rea-agents`,
`ecc-universal`, …), and clones the upstream repos into `tools/` (git-ignored).

Ghidra is opt-in (≈550 MB + JDK):

```bash
WITH_GHIDRA=1 ./scripts/install-skills.sh   # downloads Ghidra 12.2 to ~/.local/ghidra
```

## Verify

```bash
./scripts/install-skills.sh --verify
# verified in this workspace:
#   radare2 6.2.6 · frida 17.26.4 · rea 6.7.0 · ecc-universal · modal 1.6.4
#   .claude/skills/ = 63 skills (15 from the screenshots + 48 from ECC)
ls .claude/skills/ | wc -l
```

Environment variables the tools want:

```bash
export PATH="$HOME/.local/bin:$PATH"                  # r2, frida, rea, ecc, modal
export REA_PWNTOOLS_PYTHON=$HOME/.local/rea-venv/bin/python  # REA binary layout
export GHIDRA_INSTALL_DIR=$HOME/.local/ghidra         # REA deep analysis
```

## Layout

```
skills/
├── README.md                  ← this file
├── reverse-engineering/
│   ├── SKILL.md               ← master RE workflow (from the notes)
│   ├── radare2/SKILL.md
│   ├── ghidra/SKILL.md
│   ├── x64dbg/SKILL.md
│   ├── binary-ninja/SKILL.md
│   ├── frida/SKILL.md
│   └── rea/SKILL.md
├── free-llm/
│   ├── SKILL.md               ← master free-LLM workflow (pick → key → plug in)
│   ├── freellmapi/SKILL.md
│   ├── awesome-free-llm-apis/SKILL.md
│   ├── ecc/SKILL.md
│   ├── freebuff/SKILL.md
│   ├── modal/SKILL.md
│   └── public-apis/SKILL.md
└── begonia-kernel/
    └── SKILL.md               ← RE workflow for this repo's kernel image
scripts/
├── install-skills.sh          ← one-command installer for all skills
├── install-re-tools.sh        ← RE tools only (radare2, Ghidra, Frida, REA…)
└── free_llm.py                ← call any free LLM provider (OpenAI-compatible)
config/
├── free-llm-providers.json    ← provider catalog from the screenshots
└── .env.example               ← copy to .env, paste your free API keys
```

> ⚠️ Ethics (from the notes): reverse engineering only with proper
> authorization, for learning / security research / your own binaries.
> Free LLM APIs: personal experimentation only — respect each provider's
> terms, rate limits, and non-commercial restrictions.
