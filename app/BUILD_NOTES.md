# BizBuddy — build notes

Source: `bizbuddy_spatial_fintech_gst_os by -Dipes Mondal (1).html`
(a Cloudflare-saved single-file web app, 209 KB, shared via Drive).

## What changed

| Area | Change |
|---|---|
| **Logo** | New mark: a "B" with rising bars (business growth), orange→amber gradient. Files: `logo.png` (512), `logo.svg`, `icon-192.png`, `icon-512.png`. Also swapped into the in-page brand slot and the splash. |
| **Opening animation** | Full-screen boot splash — mark scales in, bars grow one by one, wordmark fades up, progress bar fills, then fades out (~2.1 s). Skipped on repeat visits in the same session; respects `prefers-reduced-motion`. |
| **Login** | Real accounts: email + password, PBKDF2-SHA256 (150k iterations, WebCrypto), random 16-byte salt per account. Wrong password is rejected. Sign-up collects owner/business/GSTIN; login only asks email + password. |
| **Session** | Persists in `localStorage`; reload opens the dashboard directly. `bbSignOut()` clears it. |
| **Data** | Ledger / invoices / inventory autosave per account (`bb_data_v1:<email>`) and reload with the session. A brand-new account starts empty rather than showing the demo numbers. |
| **PWA** | `manifest.json` + `sw.js` — installable to the home screen, works offline. |

Everything else (landing page, 3D sections, GST engine, market intel, AI drawer)
is untouched.

## Two real bugs found in the source file

1. **All scripts were dead.** Cloudflare's "Rocket Loader" had rewritten every
   `<script>` tag to `type="d1536dedf0a0c465101e9d16-text/javascript"`, which no
   browser executes. The app shipped with **zero working JavaScript** — no
   login, no dashboard, no effects. Fixed by stripping the bogus `type` and
   removing the `rocket-loader.min.js` stub (its path is host-absolute and 404s
   off Cloudflare).
2. **Hard dependency on `cdn.tailwindcss.com`.** Offline, the whole UI lost its
   styling. Added a `window.tailwind` guard so the page still boots without the
   CDN.

## Verification (jsdom, no browser available in this sandbox)

```
1. splash exists ......................... true
2. auth modal hidden initially ........... true
3. modal opens ........................... true
4. weak password rejected ................ "Password must be at least 8 characters."
5. signup succeeded ...................... true
6. dashboard visible ..................... true
7. account stored ........................ hash 64 chars, plaintext absent
8. GSTIN normalised ...................... 29AABCA8492K1Z5
9. session written ....................... {"email":"muqeet@drklabs.in"}
10. sign out returns to landing .......... true
11. login mode hides owner/biz fields .... true
12. wrong password rejected .............. "Incorrect email or password."
13. correct login works .................. true
14. workspace saved ...................... ledger has "Test Sale"
+ reload restores session without login .. true
JS errors: none
```

Not tested in a real browser: the 3D/canvas effects (jsdom cannot render
canvas). Those sections are unchanged from the original.

## Why there is no `.apk` here

This sandbox cannot build an Android binary — verified:

- `dl.google.com`, `repo1.maven.org`, `services.gradle.org` → all blocked
  (egress allows only npm/PyPI/GitHub)
- no `sdkmanager`, `gradle`, `aapt2`, `apksigner`, `zipalign`, `d8`

So this is a **PWA**, not a compiled APK. See `PACKAGING.md` for the three
honest routes to a real installable app, including one that needs no SDK.

## Running it

```bash
cd app && python3 -m http.server 8000
# open http://localhost:8000/
```

Serve over `http://`, not `file://` — `crypto.subtle` (password hashing) and
service workers both require a secure context (`localhost` counts).
