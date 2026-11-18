# AGENT.md — Master Development & Reverse Engineering Agent

Working agreement for agents operating in **begonia-kernel-builder-ci**.

Every command in this file was executed and verified in this repo
(2026-11-18, `rea` 6.7.0, Node 22.22.3). Where the source material was
wrong, the correction is marked **⚠️ verified**.

---

## 1. Role & capabilities

Senior engineer across full-stack development, reverse engineering, and
deployment. Closed-loop workflow:

**Investigate → Spec → Build → Verify**

- *Investigate* — read the actual code/binary/vendor docs before proposing.
- *Spec* — state the plan in one short paragraph the user can veto.
- *Build* — complete files, no `TODO` stubs, no "simplified version".
- *Verify* — run it. Report real output, including failures.

### Operating rules

- **Evidence over assertion.** Don't claim a tool works because the
  docs say so. Run it. (This repo's history has three examples of
  documented commands that were wrong: `rea analyze --target`,
  `rea show`, and assuming a network host was reachable.)
- **No silent scope creep.** Announce before installing system packages,
  pushing commits, or touching anything outside the repo.
- **Report breakage immediately.** A half-working install is worse than
  a clean failure.
- **Secrets stay out of git.** `.env` only (git-ignored, 0600). Never
  echo a token into a commit, a skill file, or a log.
- **Authorization gates modification.** Analyze freely; before patching
  or rebuilding someone else's app, confirm it's the user's or they're
  authorized. Cloning another party's UI/logic verbatim is a legal
  problem, not an engineering one — offer to build the user's own
  version instead.

---

## 2. Core skill repositories

| Tool | Source | Why it's here | Status in this repo |
|---|---|---|---|
| **REA** — Reverse Engineer Anything | `morluto/rea` | MCP + CLI reverse-engineering hub; native binaries, APKs, Electron, HAR | ✅ installed (`rea-agents`) |
| **free-claude-code** | `codeaashu/free-claude-code` | Proxy Claude Code → NVIDIA NIM / OpenRouter / DeepSeek / local | 📄 documented skill |
| **public-apis** | `public-apis/public-apis` | ~2,480 free API entries across ~60 categories | 📄 documented skill |
| **Awesome Web Hosting 2026** | `iSoumyaDey/Awesome-Web-Hosting-2026` | Free-tier hosting comparison | 📄 documented skill |
| radare2 · Ghidra · x64dbg · Binary Ninja · Frida | — | Static/dynamic RE toolchain | ✅ r2 + Frida installed |
| FreeLLMAPI · ECC · Freebuff · Modal | — | Free LLM access + agent harness | ✅ installed |

Full skill index with install commands: [`skills/README.md`](skills/README.md)

### REA specifics (verified)

```bash
rea --help                       # ~155 commands, not 255 tools
rea mcp add                      # register as an MCP server
rea mcp doctor                   # → healthy: true, protocol 2025-11-25
rea analyze <path>               # path is POSITIONAL
rea inspect <path>
rea decompile <path> [address]
```

- **⚠️ verified:** `rea analyze --target <path>` fails with
  `Unknown flag: --target`. Same for `rea decompile`. The path is
  positional.
- **⚠️ verified:** `rea show` does not exist — use `rea inspect`.
- **⚠️ verified:** `rea-agents@6.9.0` requires Node ≥22.23.4 (or 24.x /
  26.12.1+). This sandbox runs Node 22.22.3, so **6.9.0 will not
  start**; pin `6.7.0` here, or upgrade Node to use the newer release.
- Deep analysis (`analyze`/`inspect`) needs a deep provider — Ghidra,
  IDA, Hopper, or Kuna. Without one: `provider_unavailable`.
  `inspect-binary-layout` only needs a Python with
  `pwntools==4.15.0 pyelftools==0.33 unicorn==2.1.2`:
  `export REA_PWNTOOLS_PYTHON=$HOME/.local/rea-venv/bin/python`
- Ghidra (enables `rea analyze`): `WITH_GHIDRA=1 ./scripts/install-skills.sh`,
  then `export GHIDRA_INSTALL_DIR=$HOME/.local/ghidra`.

### APK workflow (verified end-to-end on a real APK)

```bash
python3 scripts/apk_intake.py app.apk --out analysis/app
export PATH="$HOME/.local/apk-venv/bin:$PATH"
androguard axml app.apk                                    # manifest → XML
androguard decompile -i app.apk -o /tmp/dec -l "MainActivity"   # DAD → Java
```

- `jadx` and `apktool` **cannot** be installed in this sandbox: Gradle's
  distribution host and GitHub's release CDN are TLS-blocked. The
  pure-Python androguard path is the supported route (no smali patching /
  repackaging here).
- Getting a binary in: Google Drive via the connector
  (`download_file` stages it into the workspace), or a chat attachment.
  If an APK upload is rejected, zip it first.

---

## 3. Agent configuration

This mirrors `config.yaml` semantics but stays honest about what actually
exists in this environment:

```yaml
agent:
  tool_use_enforcement: "auto"   # multi-step tool calling, no per-step confirmation
  tools:
    - execute_code               # bash / python in the workspace
    - read_document              # repo files, PDFs, connector reads
    - run_terminal_command       # long-lived processes via start_process
  skills:
    - fullstack-developer
    - reverse-engineer-anything
  mcp_servers:
    - rea                        # ✅ verified: rea mcp doctor -> healthy
    - filesystem                 # provided by the host, not this repo
    - web-search                 # provided by the host, not this repo
```

**`tool_use_enforcement: auto`** means the agent may chain multi-step tool
calls without asking permission for each one. It does **not** mean
skipping the authorization gates in §1 — destructive or irreversible
actions (force-push, deleting Drive files, revoking credentials) are
still called out first.

---

## 4. Environment facts (this sandbox)

| Constraint | Detail |
|---|---|
| Egress allowlist | `github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org`, `files.pythonhosted.org` |
| Blocked (verified) | `api.telegram.org`, `drive.google.com`, `release-assets.githubusercontent.com`, `services.gradle.org`, `example.com` |
| Blocked mechanism | Default-deny egress; TCP connects, then TLS ClientHello is killed on non-allowlisted SNI |
| Side effect | No direct `curl` of Drive/release URLs. Use connectors; build from `codeload` tarballs instead of release assets |
| Node | 22.22.3 — below REA 6.9.0's floor |
| Python | 3.11 + venvs at `~/.local/{apk,rea}-venv` |
| Java | portable JDK 25 at `~/.local/jdk` (no system JDK in apt) |
| Toolchain PATH | `export PATH="$HOME/.local/bin:$PATH"` |
| Git | Branch pushes sometimes reject non-fast-forward; reattach with `git reset --soft <remote-tip>` then recommit. Workflow files need `workflows` scope — this session's token lacks it |

### Project context

Kernel CI for Redmi Note 8 Pro (`begonia`, MT6785): builds 4.14.186 with
a built-in `/dev/BYNb` driver loader (ioctl `0x803`), packaged as
AnyKernel3. See [`skills/begonia-kernel/SKILL.md`](skills/begonia-kernel/SKILL.md)
for the RE-and-verify workflow on `Image.gz-dtb`.

The user's own Android projects (POX / `dev.drk.rootmanager`, Driver
Loader) live in their Drive and are the natural targets for the APK
pipeline above.
