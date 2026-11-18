"""Static sanity checker for hand-written smali.

Catches the two mistakes that make ART crash at class load / first use and that
the smali assembler happily accepts:

 1. Register range errors (using vX beyond what .locals + params provide).
 2. Writes into the parameter register range, which silently aliases/clobbers
    `this` or an argument (e.g. `.locals 0` then `const/4 v0` overwrites p0).
 3. invoke-* whose receiver register provably holds the wrong object type.
"""
import re, sys, glob

WRITES = re.compile(
    r"^\s*(const/\d+|const|const-string/jumbo|const-string|const-wide/\d+|const-wide|"
    r"move|move-object|move-result|move-result-object|move-result-wide|"
    r"new-instance|new-array|iget\w*|sget\w*|aget\w*|add-int|sub-int|"
    r"xor-int|and-int|or-int|shl-int|shr-int|ushr-int|mul-int|div-int|rem-int|"
    r"int-to-\w+|char-to-\w+|array-length|instance-of)\s+(.*)$")

def parse_methods(path):
    src = open(path).read().splitlines()
    i = 0
    while i < len(src):
        line = src[i].strip()
        if line.startswith(".method"):
            m = re.match(r"\.method\s+(.*)$", line)
            if m:
                rest = m.group(1)
                mm = re.search(r"(\S+?)\((.*)\)(\S+)$", rest)
                m = mm
            body, start = [], i + 1
            j = i + 1
            while j < len(src) and not src[j].strip().startswith(".end method"):
                body.append((j + 1, src[j]))
                j += 1
            if m:
                yield (start + 1, line, m.group(1), m.group(2), m.group(3), body, path)
            i = j
        i += 1

def param_regs(sig):
    if not sig:
        return 0
    # count registers for params (wide types occupy 2)
    n = 0
    for t in re.findall(r"\[*(?:L[^;]+;|[ZBSCIJFD])", sig):
        n += 2 if t in ("J", "D") else 1
    return n

def check(path):
    problems = []
    for lineno, decl, name, sig, ret, body, _ in parse_methods(path):
        is_static = " static " in f" {decl} "
        nparams = param_regs(sig) + (0 if is_static else 1)   # +this
        locals_m = [l for _, l in body if l.strip().startswith(".locals")]
        nlocals = int(locals_m[0].split()[1]) if locals_m else None
        if nlocals is None:
            continue
        total = nlocals + nparams
        pbase = nlocals           # p0 == v(nlocals) (v-regs only cover .locals)
        p_named = {f"p{k}": nlocals + k for k in range(nparams)}

        for ln, line in body:
            s = line.strip()
            if not s or s.startswith(("#", ".", ":")):
                continue
            # register operands in braces
            for grp in re.findall(r"\{([^}]*)\}", s):
                for reg in re.split(r"[\s,]+", grp.strip()):
                    reg = reg.strip()
                    if not reg:
                        continue
                    if reg.startswith("v"):
                        n = int(reg[1:])
                        if n >= total:
                            problems.append(
                                f"{path}:{ln}: register {reg} out of range "
                                f"(.locals {nlocals} + {nparams} params = {total})")
                    elif re.fullmatch(r"p\d+", reg):
                        k = int(reg[1:])
                        if k >= nparams:
                            problems.append(
                                f"{path}:{ln}: parameter register {reg} out of range "
                                f"(method has {nparams} parameter registers)")
            # writes into the parameter range
            # register writes in any instruction form ('.locals 0' + const/4 v0 -> clobbers p0)
            wm2 = re.match(r"^[a-z][a-z0-9/_-]*\s+(v\d+)(?:\s*,\s*|\s*$)", s)
            if wm2:
                reg = int(wm2.group(1)[1:])
                if reg >= pbase and not (is_static and reg - pbase >= nparams):
                    alias = f"p{reg - pbase}"
                    problems.append(
                        f"{path}:{ln}: '{s.split()[0]}' writes {wm2.group(1)} which aliases "
                        f"{alias} (parameter register) — clobbers "
                        f"{'this' if (not is_static and reg == pbase) else 'an argument'}")
                continue
            wm = WRITES.match(s)
            if wm:
                rest = wm.group(2)
                first = re.match(r"\s*(v\d+)", rest)
                if first:
                    reg = int(first.group(1)[1:])
                    if reg >= pbase:
                        alias = f"p{reg - pbase}"
                        if is_static and reg - pbase >= nparams:
                            problems.append(
                                f"{path}:{ln}: '{s.split()[0]}' writes {first.group(1)} "
                                f"but the method only has .locals {nlocals} and no such param")
                        else:
                            problems.append(
                                f"{path}:{ln}: '{s.split()[0]}' writes {first.group(1)} "
                                f"which aliases {alias} (parameter register) — "
                                f"clobbers {'this' if (not is_static and reg == pbase) else 'an argument'}")
    return problems

if __name__ == "__main__":
    files = sys.argv[1:] or glob.glob("/tmp/build/smali/**/*.smali", recursive=True)
    allp = []
    for f in files:
        allp += check(f)
    if allp:
        print(f"{len(allp)} problem(s):\n")
        for p in allp:
            print("  " + p)
        sys.exit(1)
    print("no register problems found")
