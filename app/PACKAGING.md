# From PWA to installable app

I could not produce a `.apk` in this environment (no Android SDK, no Gradle,
both blocked by the network policy — see `BUILD_NOTES.md`). Here are the
routes that actually work, cheapest first.

---

## Option A — Install the PWA (works today, no build)

The app is already installable. Host the `app/` folder, open it on the phone:

- **Android/Chrome:** menu → *Add to Home screen* → *Install*
- **Desktop Chrome/Edge:** install icon in the address bar
- **iOS/Safari:** Share → *Add to Home Screen*

It opens fullscreen (no browser chrome), has its own icon, and works offline
via the service worker. This is a genuine installed app on the home screen —
not a bookmark.

**Hosting (free tiers, all in the hosting skill):** Vercel, Netlify, or
Cloudflare Pages — drag the `app/` folder in, done. `start_url` is
`bizbuddy.html`, `scope` is the folder, so it works from any subpath.

---

## Option B — Real APK via a cloud builder (no local SDK)

If Play Store distribution is needed, build in CI rather than locally:

1. Wrap the PWA with **[Bubblewrap](https://github.com/GoogleChromeLabs/bubblewrap)**
   (`@bubblewrap/cli`) — Google's tool that turns a PWA into a Trusted Web
   Activity APK. It needs the Android SDK, so run it on a machine/runner that
   has one.
2. Or use **PWABuilder** (pwabuilder.com) — upload the hosted URL, download a
   signed `.apk` / `.aab`. No local tooling at all.

Both give a real APK that opens your web app fullscreen without browser UI.
Caveat: a TWA still needs the site online for the first load (the service
worker covers offline after that).

---

## Option C — Native wrapper (Flutter / React Native)

Only worth it if you want native APIs (camera, Bluetooth, background GPS) or
a fully offline bundle. That means porting the UI — this app's landing page is
heavy on 3D/CSS effects that do not translate 1:1.

Rough shape:

```
bizbuddy_native/
├── lib/main.dart              # app shell + splash
├── lib/theme/                 # orange/amber tokens from the web app
├── lib/screens/landing.dart
├── lib/screens/auth.dart      # same PBKDF2 flow, flutter_secure_storage
├── lib/screens/dashboard.dart # ledger / invoices / inventory
├── lib/data/ledger_repo.dart  # sqflite or drift
└── assets/logo.png
```

`flutter build apk` on your machine (or `--release` in CI) produces the APK.
I can write this out in full — say the word — but it only makes sense if you
need native features.

---

## A warning about the current login

Auth here is **local-only**: accounts live in the browser's `localStorage` and
the password hash never leaves the device. That is honest for a single-device
demo, but it means:

- Clearing browser data deletes the account and its workspace.
- There is no password reset, no multi-device sync, no admin view.
- Anyone with the device can read the stored business data (it is not
  encrypted at rest).

For a real product you want a backend. Supabase is already connected in this
conversation and gives you email/password auth + Postgres + row-level security
in a few hours of work. Say the word and I will wire it — the app's data model
(`user`, `ledger[]`, `invoices[]`, `inventory[]`) maps to four tables cleanly.
