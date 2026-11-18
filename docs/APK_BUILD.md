# BizBuddy APK — how it is built (v1.1)

The APK is a **thin native WebView shell around the BizBuddy PWA**. It contains no
third-party app code: the old "All Driver" host (`com.alldriver.bymahbub`) was
abandoned because it has no WebView at all and could never render BizBuddy.

## Package facts

| Field | Value |
| --- | --- |
| package | `com.bizbuddy.app` |
| version | 1.0 (code 1) |
| launcher activity | `com.bizbuddy.app.MainActivity` |
| label | BizBuddy |
| minSdk / targetSdk | 21 / 34 |
| signature | v1 + v2 + v3, `CN=BizBuddy` (keystore `dist/bizbuddy.p12`) |
| payload | `assets/index.html` = `app/bizbuddy.html` (byte-identical) |
| size | ~131 KB |

Runtime logic lives in two smali classes only:

* `MainActivity` — creates the `WebView`, enables JS/DOM storage, loads the app.
* `MainActivity$AssetClient` — a `WebViewClient` that serves `assets/` over
  `https://appassets.androidplatform.net/assets/`, giving the page a real
  **https origin** so `localStorage` and `crypto.subtle` behave like on the web.
  If that ever fails it falls back once to `file:///android_asset/index.html`.

## Why the shell is not `file://`

Loading `file://` directly is broken on modern WebView: the origin is opaque, so
`localStorage` throws `SecurityError` and `crypto.subtle` is `undefined`. That
would have meant a login screen that cannot save anything. The virtual-https
loader fixes it. As a belt-and-braces measure the page also ships:

* a pure-JS **PBKDF2-SHA256** fallback (verified byte-identical to Node/OpenSSL),
* a `localStorage` memory shim for opaque origins,
* `IntersectionObserver` / `ResizeObserver` stubs for old WebViews,
* **prebuilt Tailwind CSS** inlined at build time, so no CDN is needed offline.

## Build chain (no Android SDK, no javac in this environment)

```bash
# 1. smali -> dex (apktool builds sources before resources, which is all we need)
apktool b /tmp/build -o /tmp/unused.apk          # emits /tmp/build/build/apk/classes.dex

# 2. resources + manifest -> base apk
aapt2 compile --dir /tmp/build/res --legacy -o /tmp/bb_res.zip
aapt2 link -o /tmp/bb_base.apk \
  -I ~/.local/share/apktool/framework/1.apk \
  --manifest /tmp/build/AndroidManifest.xml \
  --min-sdk-version 21 --target-sdk-version 34 \
  -R /tmp/bb_res.zip --auto-add-overlay

# 3. stitch base + classes.dex + assets/index.html, then sign
apksigner sign --ks dist/bizbuddy.p12 --ks-key-alias bizbuddy \
  --min-sdk-version 21 --out dist/BizBuddy-v1.1-signed.apk unsigned.apk
```

Tailwind is compiled ahead of time with the project's own config:

```bash
npx tailwindcss -c tailwind.config.js -i in.css -o tailwind.out.css --minify
# output is inlined into app/bizbuddy.html as <style id="tailwind-prebuilt">
```

## Verification performed

* `apksigner verify --verbose` → v1, v2, v3 all true.
* `androguard` → package `com.bizbuddy.app`, label `BizBuddy`, one activity.
* `apktool d` round-trip → both smali classes and the asset decode back out.
* `classes.dex` defines only the two BizBuddy classes; zero occurrences of the
  old host strings (`Mahbub` / `alldriver`) anywhere in the APK.
* jsdom run under device-accurate conditions (no `crypto.subtle`, no storage):
  14/14 assertions — splash, signup, hashed password, session, persistence,
  wrong-password rejection, correct-password login.

## Install

Download the APK, allow "install unknown apps" for the browser/files app, tap it.
First launch shows the BizBuddy splash, then the login/signup screen; accounts and
all business data stay on the device (`bb_accounts_v1`, `bb_data_v1:<email>`).
