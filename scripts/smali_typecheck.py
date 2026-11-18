"""Type-check invoke receivers in hand-written smali.

Tracks what object each register holds (params, new-instance, move-result-object,
iput/iget round-trips) and reports invoke-virtual/interface/direct whose receiver
class does not match -- or is not a subtype of -- the invoked method's owner.
This catches mistakes like calling WebView.setWebViewClient() on an Activity.
"""
import re, sys, glob

# minimal framework hierarchy we rely on
SUPER = {
    "Lcom/bizbuddy/app/MainActivity;": "Landroid/app/Activity;",
    "Lcom/bizbuddy/app/MainActivity$AssetClient;": "Landroid/webkit/WebViewClient;",
    "Landroid/app/Activity;": "Landroid/content/Context;",
    "Landroid/content/Context;": "Ljava/lang/Object;",
    "Landroid/webkit/WebView;": "Landroid/widget/AbsoluteLayout;",
    "Landroid/widget/AbsoluteLayout;": "Landroid/view/ViewGroup;",
    "Landroid/view/ViewGroup;": "Landroid/view/View;",
    "Landroid/view/View;": "Ljava/lang/Object;",
    "Landroid/widget/TextView;": "Landroid/view/View;",
    "Landroid/view/ViewGroup;": "Landroid/view/View;",
    "Landroid/webkit/WebViewClient;": "Ljava/lang/Object;",
    "Landroid/net/Uri;": "Ljava/lang/Object;",
    "Ljava/lang/String;": "Ljava/lang/Object;",
    "Landroid/webkit/WebResourceRequest;": "Ljava/lang/Object;",
    "Landroid/webkit/WebResourceResponse;": "Ljava/lang/Object;",
    "Landroid/content/res/AssetManager;": "Ljava/lang/Object;",
    "Ljava/io/InputStream;": "Ljava/lang/Object;",
}

# method -> (owner, param types) for the framework calls this app makes
METHODS = {
    ("Landroid/webkit/WebView;", "setWebViewClient"): ["Landroid/webkit/WebViewClient;"],
    ("Landroid/webkit/WebView;", "setWebChromeClient"): ["Landroid/webkit/WebChromeClient;"],
    ("Landroid/webkit/WebView;", "loadUrl"): ["Ljava/lang/String;"],
    ("Landroid/webkit/WebView;", "canGoBack"): [],
    ("Landroid/webkit/WebView;", "goBack"): [],
    ("Landroid/webkit/WebView;", "destroy"): [],
    ("Landroid/webkit/WebView;", "getSettings"): [],
    ("Landroid/webkit/WebView;", "setBackgroundColor"): ["I"],
    ("Landroid/webkit/WebView;", "setOverScrollMode"): ["I"],
    ("Landroid/app/Activity;", "setContentView"): ["Landroid/view/View;"],
    ("Ljava/lang/String;", "startsWith"): ["Ljava/lang/String;"],
    ("Ljava/lang/String;", "substring"): ["I"],
    ("Ljava/lang/String;", "endsWith"): ["Ljava/lang/String;"],
    ("Ljava/lang/String;", "toLowerCase"): [],
    ("Ljava/lang/String;", "length"): [],
    ("Landroid/content/Context;", "getAssets"): [],
    ("Landroid/content/res/AssetManager;", "open"): ["Ljava/lang/String;"],
    ("Landroid/net/Uri;", "toString"): [],
}


def is_subtype(have, want):
    seen, cur = set(), have
    while cur and cur not in seen:
        if cur == want:
            return True
        seen.add(cur)
        cur = SUPER.get(cur)
    return False


def param_types(sig):
    return re.findall(r"\[*(?:L[^;]+;|[ZBSCIJFD])", sig or "")


RET = {}


def check_file(path, problems):
    lines = open(path).read().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line.startswith(".method"):
            i += 1
            continue
        mm = re.search(r"(\S+?)\((.*)\)(\S+)$", line)
        decl = line
        start = i
        body = []
        j = i + 1
        while j < len(lines) and not lines[j].strip().startswith(".end method"):
            body.append((j + 1, lines[j].strip()))
            j += 1
        i = j + 1
        if not mm:
            continue
        name, sig, ret = mm.groups()
        is_static = bool(re.search(r"\bstatic\b", decl))
        ptypes = param_types(sig)
        nlocals = None
        for ln, s in body:
            if s.startswith(".locals"):
                nlocals = int(s.split()[1])
                break
        if nlocals is None:
            continue
        nparam = len(ptypes) + (0 if is_static else 1)
        total = nlocals + nparam
        # register -> type
        types = {}
        if not is_static:
            types["p0"] = "Lcom/bizbuddy/app/MainActivity;" if "MainActivity" in path and "$" not in name + path.split("/")[-1] else path.split("/")[-1].replace(".smali", "")
        # simpler: derive this type from the class declaration
        cls = re.search(r"^\.class.*?(L[^;\s]+;)", open(path).read(), re.M)
        this_type = cls.group(1) if cls else None
        vmap = {}
        if not is_static and this_type:
            vmap[nlocals] = this_type          # v(nlocals) == p0
        for k, t in enumerate(ptypes):
            base = nlocals + (0 if is_static else 1) + sum(
                2 if p in ("J", "D") else 1 for p in ptypes[:k]
            )
            vmap[base] = t
        reg = lambda r: ("v", int(r[1:])) if r.startswith("v") else ("p", int(r[1:]))
        def to_v(r):
            kind, n = reg(r)
            return n if kind == "v" else nlocals + n
        def name_of(v):
            return f"v{v}" if v < nlocals else f"p{v - nlocals}"

        for ln, s in body:
            if s.startswith(("invoke-",)):
                im = re.match(r"invoke-(\w+)\s+\{([^}]*)\},\s*(L[^;]+;)->(\w+)\(([^)]*)\)(\[*(?:L[^;]+;|[ZBSCIJFDV]))", s)
                if not im:
                    continue
                kind, regs, owner, mname, msig, mret = im.groups()
                RET["last"] = mret if mret.startswith("L") or mret.startswith("[") else None
                regs = [r.strip() for r in regs.split(",") if r.strip()]
                if not regs:
                    continue
                recv = to_v(regs[0])
                have = vmap.get(recv)
                key = (owner, mname)
                if have and key in METHODS:
                    if not is_subtype(have, owner):
                        problems.append(
                            f"{path}:{ln}: invoke-virtual receiver {name_of(recv)} is "
                            f"{have} but {owner}->{mname}() requires a {owner} "
                            f"(receiver should be the {owner.split('/')[-1][:-1]} instance)")
                        continue
                want = METHODS.get(key, [])
                args = regs[1:]
                for idx, w in enumerate(want):
                    if idx >= len(args):
                        break
                    have_t = vmap.get(to_v(args[idx]))
                    if have_t and w.startswith("L") and not is_subtype(have_t, w):
                        problems.append(
                            f"{path}:{ln}: arg {idx+1} of {mname}() is {have_t}, expected {w}")
                continue
            # track object producers
            m = re.match(r"const-string(?:/jumbo)?\s+(v\d+|p\d+)", s)
            if m:
                vmap[to_v(m.group(1))] = "Ljava/lang/String;"
                continue
            m = re.match(r"new-instance\s+(v\d+|p\d+),\s*(L[^;]+;)", s)
            if m:
                vmap[to_v(m.group(1))] = m.group(2)
                continue
            m = re.match(r"move-result-object\s+(v\d+|p\d+)", s)
            if m:
                if RET.get("last"):
                    vmap[to_v(m.group(1))] = RET["last"]
                continue
            m = re.match(r"iget-object\s+(v\d+|p\d+),\s*(v\d+|p\d+),\s*(L[^;]+;)->(\w+):(L[^;]+;)", s)
            if m:
                vmap[to_v(m.group(1))] = m.group(5)
                continue


if __name__ == "__main__":
    files = sys.argv[1:] or glob.glob("/tmp/build/smali/**/*.smali", recursive=True)
    problems = []
    for f in files:
        check_file(f, problems)
    if problems:
        print(f"{len(problems)} type problem(s):\n")
        for p in problems:
            print("  " + p)
        sys.exit(1)
    print("no receiver-type problems found")
