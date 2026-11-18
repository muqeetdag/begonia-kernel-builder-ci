# begonia-kernel-builder-ci

GitHub Actions CI that builds a **4.14.186 kernel with a built-in driver
loader** for the Redmi Note 8 Pro (`begonia`, MT6785) and packages it as
an AnyKernel3 flashable zip.

- Kernel source: `Saikrishna1504/kernel_xiaomi_mt6785` (branch `kaeru`),
  patched to 4.14.186
- Driver loader: `driver_loader_builtin.c` → `/dev/BYNb`, ioctl `0x803`
- Output: `Begonia-4.14.186-driver-loader-DRKMUQEETT.zip`
- Workflow: `.github/workflows/build_kernel.yml` (see `build.sh` for local)

Agents working in this repo: see [`AGENT.md`](AGENT.md) for the
working agreement and verified environment constraints.

## ✨ Skills (all installed)

Every skill from the screenshots is installed as an agent skill
(`SKILL.md`) under [`skills/`](skills/README.md):

**Reverse engineering** — [radare2](skills/reverse-engineering/radare2/SKILL.md) ·
[Ghidra](skills/reverse-engineering/ghidra/SKILL.md) ·
[x64dbg](skills/reverse-engineering/x64dbg/SKILL.md) ·
[Binary Ninja](skills/reverse-engineering/binary-ninja/SKILL.md) ·
[Frida](skills/reverse-engineering/frida/SKILL.md) ·
[REA (MCP)](skills/reverse-engineering/rea/SKILL.md) ·
[master workflow](skills/reverse-engineering/SKILL.md)

**Free LLM / agents** — [FreeLLMAPI](skills/free-llm/freellmapi/SKILL.md) ·
[awesome-free-llm-apis](skills/free-llm/awesome-free-llm-apis/SKILL.md) ·
[ECC](skills/free-llm/ecc/SKILL.md) ·
[Freebuff](skills/free-llm/freebuff/SKILL.md) ·
[Modal](skills/free-llm/modal/SKILL.md) ·
[public-apis](skills/free-llm/public-apis/SKILL.md) ·
[master workflow](skills/free-llm/SKILL.md)

**Project** — [begonia-kernel RE workflow](skills/begonia-kernel/SKILL.md)
(analyze `Image.gz-dtb`, verify `/dev/BYNb`)

```bash
chmod +x scripts/install-skills.sh
./scripts/install-skills.sh            # install everything
./scripts/install-skills.sh --verify   # check what's installed
WITH_GHIDRA=1 ./scripts/install-skills.sh   # + Ghidra 12.2 (≈550 MB, opt-in)
cp config/.env.example .env            # paste free API keys
python3 scripts/free_llm.py --list     # free LLM providers
```

Installed & verified in this workspace:

| Tool | Version | Source skill |
|------|---------|--------------|
| radare2 | 6.2.6 | `reverse-engineering/radare2` |
| Frida | 17.26.4 | `reverse-engineering/frida` |
| REA | 6.7.0 (rea-agents) | `reverse-engineering/rea` |
| ECC | ecc-universal + 63 skills in `.claude/skills/` | `free-llm/ecc` |
| Modal | 1.6.4 | `free-llm/modal` |
| Ghidra | opt-in (`WITH_GHIDRA=1`) | `reverse-engineering/ghidra` |

Ghidra, x64dbg, and Binary Ninja are GUI/desktop tools — their skills
document the workflow and the exact install source; the CLI stack above
runs headless in this container/CI.
