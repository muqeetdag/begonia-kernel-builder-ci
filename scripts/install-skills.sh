#!/usr/bin/env bash
# Install ALL skills from the screenshots into this repo + your machine.
#
# Skills covered:
#   Reverse engineering : radare2, Ghidra, x64dbg, Binary Ninja, Frida, REA
#   Free LLM / agents  : FreeLLMAPI, awesome-free-llm-apis, ECC, Freebuff,
#                        Modal, public-apis
#   Project            : begonia-kernel (this repo's RE workflow)
#
# Usage:
#   ./scripts/install-skills.sh              # full install
#   ./scripts/install-skills.sh --light      # npm/pip + skill sync only (fast)
#   ./scripts/install-skills.sh --re-only    # reverse-engineering tools only
#   ./scripts/install-skills.sh --llm-only   # free-LLM skills only
#   ./scripts/install-skills.sh --verify     # check what's installed
#   ./scripts/install-skills.sh --help
#
# What it does:
#   1. Syncs skills/*/SKILL.md -> .claude/skills/ (project) and
#      ~/.claude/skills/ (user) so Claude Code / Codex / Cursor find them.
#   2. Installs real tools: radare2 (apt), frida-tools (pip),
#      rea-agents + ecc-universal (npm).
#   3. Clones upstream repos into tools/ (git-ignored, NOT committed):
#      ECC, freellmapi, awesome-free-llm-apis, freebuff, public-apis, rea.
#   4. Prints a verification report.
#
# Safe to re-run (idempotent). Never commits keys or cloned repos.

set -u
cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
TOOLS_DIR="$REPO_ROOT/tools"

MODE="full"          # full | light | re-only | llm-only | verify
SKIP_APT=0
SKIP_CLONE=0

for arg in "$@"; do
  case "$arg" in
    --light) MODE="light" ;;
    --re-only) MODE="re-only" ;;
    --llm-only) MODE="llm-only" ;;
    --verify) MODE="verify" ;;
    --skip-apt) SKIP_APT=1 ;;
    --skip-clone) SKIP_CLONE=1 ;;
    --help|-h)
      sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $arg (try --help)"; exit 1 ;;
  esac
done

ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
fail() { printf '  \033[31m✗\033[0m %s\n' "$*"; }
step() { printf '\n\033[1m== %s ==\033[0m\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }

# ---------------------------------------------------------------- sync skills
sync_skills() {
  step "Syncing skills -> .claude/skills/ + ~/.claude/skills/"
  mkdir -p "$REPO_ROOT/.claude/skills" "$HOME/.claude/skills"
  local count=0
  # skills/<group>/<name>/SKILL.md and skills/<group>/SKILL.md
  while IFS= read -r f; do
    local rel="${f#skills/}"            # e.g. reverse-engineering/radare2/SKILL.md
    local dir="$(dirname "$rel")"       # e.g. reverse-engineering/radare2
    local name="$(basename "$dir")"
    # top-level group skills (reverse-engineering/SKILL.md) keep group name
    mkdir -p "$REPO_ROOT/.claude/skills/$name" "$HOME/.claude/skills/$name"
    cp "$f" "$REPO_ROOT/.claude/skills/$name/SKILL.md"
    cp "$f" "$HOME/.claude/skills/$name/SKILL.md"
    count=$((count + 1))
  done < <(find skills -name SKILL.md | sort)
  ok "Synced $count skills (project .claude/skills/ + user ~/.claude/skills/)"
  ls "$REPO_ROOT/.claude/skills/"
}

# ---------------------------------------------------------------- RE tools
install_re_tools() {
  step "Reverse-engineering tools (radare2, Frida, REA, Ghidra notes)"
  install_radare2() {
    if have r2; then ok "radare2 already installed: $(r2 -v | head -1)"; return; fi

    # 1) apt (Debian/Ubuntu, when the mirror has it)
    if [ "$SKIP_APT" -eq 0 ] && [ "$MODE" != "light" ] && have apt-get \
       && sudo -n true 2>/dev/null; then
      echo "  Installing radare2 via apt…"
      if sudo apt-get install -y -qq radare2 2>/dev/null; then
        have r2 && { ok "radare2 installed via apt"; return; }
      fi
      warn "apt has no radare2 — falling back to source build (~5 min)"
    fi

    # 2) Prebuilt .deb from GitHub releases (radare.org packages it there)
    if [ "$SKIP_APT" -eq 0 ] && [ "$MODE" != "light" ]; then
      local deb="/tmp/radare2.deb"
      echo "  Downloading radare2 .deb from GitHub releases…"
      if curl -fsSL -o "$deb" \
          "https://github.com/radareorg/radare2/releases/latest/download/radare2_amd64.deb" 2>/dev/null \
         || curl -fsSL -o "$deb" \
          "https://github.com/radareorg/radare2/releases/download/6.2.6/radare2_6.2.6_amd64.deb" 2>/dev/null; then
        if sudo apt-get install -y "$deb" >/dev/null 2>&1 && have r2; then
          ok "radare2 installed from .deb"; return
        fi
        rm -f "$deb"
      fi
      warn ".deb download unavailable — falling back to source build"
    fi

    # 3) Source build (works everywhere with gcc + make)
    if have gcc && have make && [ "$MODE" != "light" ] && [ "$SKIP_APT" -eq 0 ]; then
      echo "  Building radare2 from source into ~/.local (this takes a few minutes)…"
      local src="/tmp/radare2-src"
      rm -rf "$src"; mkdir -p "$src"
      if curl -fsSL "https://codeload.github.com/radareorg/radare2/tar.gz/refs/tags/6.2.6" \
           | tar xz -C "$src" --strip-components=1 2>/dev/null; then
        if ( cd "$src" && ./configure --prefix="$HOME/.local" >/dev/null 2>&1 \
             && make -j"$(nproc)" >/dev/null 2>&1 && make install >/dev/null 2>&1 ); then
          export PATH="$HOME/.local/bin:$PATH"
          # make the freshly installed libs visible to the loader
          if [ -w /etc/ld.so.conf.d ] 2>/dev/null || sudo -n true 2>/dev/null; then
            echo "$HOME/.local/lib" | sudo tee /etc/ld.so.conf.d/radare2.conf >/dev/null 2>&1
            sudo ldconfig 2>/dev/null
          fi
          ok "radare2 built from source into ~/.local/bin (add to PATH)"
          return
        fi
      fi
      warn "source build failed — see skills/reverse-engineering/radare2/SKILL.md"
    else
      warn "radare2 not installed (use full mode with gcc+make, or: sudo apt install radare2)"
    fi
  }
  install_radare2
  export PATH="$HOME/.local/bin:$PATH"

  if have pip3; then
    echo "  Installing frida-tools via pip…"
    # Debian/Ubuntu (PEP 668) needs --break-system-packages as fallback
    pip3 install --quiet --user frida-tools 2>/dev/null \
      || pip3 install --quiet --user --break-system-packages frida-tools 2>/dev/null \
      && ok "frida-tools installed (~/.local/bin)" || warn "pip frida-tools failed"
    export PATH="$HOME/.local/bin:$PATH"
  else
    warn "pip3 not found — skipping Frida"
  fi

  if have npm; then
    echo "  Installing rea-agents via npm (REA MCP + CLI)…"
    npm install -g rea-agents 2>/dev/null \
      && ok "rea-agents installed" || warn "npm rea-agents failed (try: npx rea-agents setup)"
  else
    warn "npm not found — skipping REA (needs Node.js)"
  fi
  install_rea_analysis_env

  echo "  Ghidra / x64dbg / Binary Ninja are GUI tools — see skills:"
  echo "    skills/reverse-engineering/{ghidra,x64dbg,binary-ninja}/SKILL.md"
  echo "    Ghidra: https://ghidra-sre.org · x64dbg: https://x64dbg.com · Binary Ninja: https://binary.ninja"
  install_ghidra
}

# ------------------------------------------------- REA analysis backend
# REA never installs Python packages itself; it wants a caller-supplied
# interpreter with pwntools / pyelftools / unicorn. We build one in a venv.
install_rea_analysis_env() {
  local venv="$HOME/.local/rea-venv"
  if [ -x "$venv/bin/python" ] && "$venv/bin/python" -c "import pwn, elftools, unicorn" 2>/dev/null; then
    ok "REA analysis env ready: $venv/bin/python"
  else
    echo "  Creating REA analysis venv (pwntools, pyelftools, unicorn)…"
    python3 -m venv "$venv" >/dev/null 2>&1 \
      && "$venv/bin/pip" -q install --upgrade pip >/dev/null 2>&1 \
      && "$venv/bin/pip" -q install "pwntools==4.15.0" "pyelftools==0.33" "unicorn==2.1.2" >/dev/null 2>&1 \
      && ok "REA analysis env created" \
      || warn "REA analysis venv failed — REA's pwntools provider will be unavailable"
  fi
  if [ -x "$venv/bin/python" ]; then
    echo "  Export for REA:  export REA_PWNTOOLS_PYTHON=$venv/bin/python"
  fi
}

# ---------------------------------------------------------------- Ghidra (opt-in)
install_ghidra() {
  [ "${WITH_GHIDRA:-0}" -eq 1 ] || {
    echo "  Ghidra skipped (large, needs a JDK). Enable with: WITH_GHIDRA=1 ./scripts/install-skills.sh"
    return
  }
  step "Ghidra decompiler (opt-in, ~550 MB + JDK)"
  local gdir="${GHIDRA_INSTALL_DIR:-$HOME/.local/ghidra}"
  if [ -d "$gdir/support" ]; then ok "Ghidra already at $gdir"; export GHIDRA_INSTALL_DIR="$gdir"; return; fi

  # JDK: system java, else a portable runtime from PyPI (jdk4py)
  if ! have java; then
    echo "  No system JDK — fetching a portable runtime (jdk4py)…"
    mkdir -p "$HOME/.local/jdk"
    if pip3 download --no-deps -q --dest /tmp/jdkdl jdk4py 2>/dev/null; then
      python3 -m zipfile -e /tmp/jdkdl/jdk4py-*.whl /tmp/jdkx >/dev/null 2>&1
      cp -r /tmp/jdkx/jdk4py/java-runtime/* "$HOME/.local/jdk/" 2>/dev/null
      chmod +x "$HOME/.local/jdk/bin/"* 2>/dev/null
      export PATH="$HOME/.local/jdk/bin:$PATH"
      have java && ok "portable JDK $(java -version 2>&1 | head -1)" || warn "portable JDK failed"
    else
      warn "could not fetch a JDK — install openjdk-17+ then re-run"
    fi
  else
    ok "java present: $(java -version 2>&1 | head -1)"
  fi

  local url="https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.2_build/ghidra_12.2_PUBLIC_20261016.zip"
  echo "  Downloading Ghidra 12.2 (~550 MB)…"
  if curl -fsSL --max-time 900 -o /tmp/ghidra.zip "$url" 2>/dev/null && [ -s /tmp/ghidra.zip ]; then
    mkdir -p "$HOME/.local/ghidra-unpack" && unzip -q -o /tmp/ghidra.zip -d "$HOME/.local/ghidra-unpack" 2>/dev/null
    local extracted; extracted="$(find "$HOME/.local/ghidra-unpack" -maxdepth 1 -type d -name 'ghidra_*' | head -1)"
    if [ -n "$extracted" ] && [ -f "$extracted/support/analyzeHeadless" ]; then
      rm -rf "$gdir"; mv "$extracted" "$gdir"
      chmod +x "$gdir/support/"* 2>/dev/null
      export GHIDRA_INSTALL_DIR="$gdir"
      ok "Ghidra installed at $gdir (export GHIDRA_INSTALL_DIR=$gdir)"
      return
    fi
  fi
  warn "Ghidra download blocked/unavailable — download manually from https://github.com/NationalSecurityAgency/ghidra/releases then:"
  echo "     export GHIDRA_INSTALL_DIR=/path/to/ghidra_12.2_PUBLIC"
}

# ---------------------------------------------------------------- LLM skills
install_llm_skills() {
  step "Free-LLM / agent skills (ECC, FreeLLMAPI, Freebuff, Modal, catalogs)"
  if have npm; then
    echo "  Installing ecc-universal via npm (ECC agent harness)…"
    npm install -g ecc-universal 2>/dev/null \
      && ok "ecc-universal installed" || warn "npm ecc-universal failed (try: npx ecc-universal@2.2.3 setup)"
    # Materialize ECC's 72 agents / 327 skills into this project's .claude/
    if have ecc && [ "$SKIP_CLONE" -eq 0 ]; then
      echo "  Installing ECC content into .claude/ (project scope, hooks off)…"
      ecc install --target claude-project --profile core --no-hooks >/dev/null 2>&1 \
        && ok "ECC agents/skills installed ($(ls .claude/skills 2>/dev/null | wc -l) skills in .claude/skills/)" \
        || warn "ecc install failed (run: ecc install --target claude-project --profile core --no-hooks)"
    else
      echo "  Tip: ecc install --target claude-project --profile core --no-hooks"
    fi
    echo "  FreeLLMAPI CLI: npx freellmapi (gateway: curl -fsSL https://freellmapi.co/install.sh | bash)"
  else
    warn "npm not found — skipping ECC/FreeLLMAPI (needs Node.js)"
  fi

  if have pip3; then
    echo "  Installing modal SDK via pip…"
    pip3 install --quiet --user modal 2>/dev/null \
      || pip3 install --quiet --user --break-system-packages modal 2>/dev/null \
      && ok "modal installed (~/.local/bin)" || warn "pip modal failed"
    export PATH="$HOME/.local/bin:$PATH"
  fi

  echo "  Freebuff: web app at https://freebuff.com (no install needed)"
  echo "  Free API keys: cp config/.env.example .env  # then paste keys"
  echo "  Catalog: config/free-llm-providers.json"
}

# ---------------------------------------------------------------- clones
clone_repos() {
  step "Cloning upstream repos into tools/ (git-ignored)"
  mkdir -p "$TOOLS_DIR"
  clone() { # clone <url> <dir>
    if [ -d "$TOOLS_DIR/$2/.git" ]; then
      ok "$2 already cloned"
    else
      git clone --depth=1 "$1" "$TOOLS_DIR/$2" 2>/dev/null \
        && ok "$2 cloned" || warn "$2 clone failed"
    fi
  }
  clone https://github.com/morluto/rea.git rea
  clone https://github.com/affaan-m/ECC.git ECC
  clone https://github.com/tashfeenahmed/freellmapi.git freellmapi
  clone https://github.com/mnfst/awesome-free-llm-apis.git awesome-free-llm-apis
  clone https://github.com/CodebuffAI/freebuff.git freebuff
  clone https://github.com/public-apis/public-apis.git public-apis
}

# ---------------------------------------------------------------- verify
verify() {
  export PATH="$HOME/.local/bin:$PATH"
  step "Verification report"
  echo "Skills in repo:"; find skills -name SKILL.md | sort | sed 's/^/  /'
  echo ""
  echo "Tools:"
  have r2        && r2 -v 2>&1 | head -1 | sed 's/^/  radare2: /' || echo "  radare2: NOT INSTALLED"
  have frida     && frida --version 2>&1 | head -1 | sed 's/^/  frida: /' || echo "  frida: NOT INSTALLED"
  have rea       && rea --help 2>&1 | head -1 | sed 's/^/  rea: /' || echo "  rea: NOT INSTALLED (try: npx rea-agents setup)"
  have ecc-universal && echo "  ecc-universal: installed" || echo "  ecc-universal: NOT INSTALLED (try: npx ecc-universal@2.2.3 setup)"
  have modal     && modal --version 2>&1 | head -1 | sed 's/^/  modal: /' || echo "  modal: NOT INSTALLED"
  echo ""
  echo "Cloned repos (tools/):"; ls "$TOOLS_DIR" 2>/dev/null | sed 's/^/  /' || echo "  (none — run without --skip-clone)"
  echo ""
  echo "Project skills (.claude/skills/):"; ls "$REPO_ROOT/.claude/skills" 2>/dev/null | sed 's/^/  /' || echo "  (none — run the installer)"
  echo ""
  echo "Free LLM helper:"
  python3 scripts/free_llm.py --list 2>&1 | head -20 | sed 's/^/  /'
}

# ---------------------------------------------------------------- main
case "$MODE" in
  verify) verify; exit 0 ;;
  light)
    sync_skills; install_re_tools; install_llm_skills
    echo ""; echo "Light install done. Run '$0 --verify' to check."
    ;;
  re-only)
    sync_skills; install_re_tools
    [ "$SKIP_CLONE" -eq 0 ] && clone_repos
    verify
    ;;
  llm-only)
    sync_skills; install_llm_skills
    [ "$SKIP_CLONE" -eq 0 ] && clone_repos
    verify
    ;;
  full)
    sync_skills; install_re_tools; install_llm_skills
    [ "$SKIP_CLONE" -eq 0 ] && clone_repos
    verify
    echo ""; echo "All skills installed! ✨"
    echo "Next: cp config/.env.example .env  # paste free API keys"
    ;;
esac
