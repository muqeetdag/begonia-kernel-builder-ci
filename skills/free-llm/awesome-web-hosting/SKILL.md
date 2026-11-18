---
name: awesome-web-hosting
description: Use Awesome-Web-Hosting-2026 (iSoumyaDey) — a curated comparison of 100+ free-tier vs paid cloud hosting platforms (Vercel, Netlify, Heroku, AWS, VPS). Use when picking where to host an app, bot backend, or preview deployment for free.
---

# Awesome Web Hosting 2026 — free hosting catalog

- Repo: https://github.com/iSoumyaDey/Awesome-Web-Hosting-2026
- Verified 2026-11-18: exists, ~352★, MIT, last push 2025-12-30.
- Claim: "150+ free cloud hosting platforms" (repo describes 100+ free
  tier vs paid platforms).

## What it covers

Comparison tables of free tiers vs paid plans across categories:

- **Static / frontend** — Vercel, Netlify, Cloudflare Pages, GitHub Pages,
  Surge, Render static
- **App / PaaS** — Render, Railway, Fly.io, Koyeb, Heroku (legacy free),
  Deta, Cyclic
- **Serverless / functions** — AWS Lambda, Cloudflare Workers, Vercel
  Functions, Deno Deploy, Val Town
- **Databases / storage** — Supabase, Neon, Turso, PlanetScale, MongoDB
  Atlas, Cloudflare R2
- **VPS / containers** — Oracle Cloud free tier, Google Cloud free tier,
  Hetzner, Akamai/Linode credits
- **Bots / cron / workers** — platforms suitable for long-running
  processes and scheduled jobs

## How to use it

1. Open the repo README; scan the table for your category.
2. Compare **free tier limits** (hours, bandwidth, cold starts, sleep
   behavior) — the repo's main value is these columns side by side.
3. Check the **always-free vs trial-credit** distinction before committing:
   trial credits expire; always-free tiers usually have hard ceilings.
4. Verify anything time-sensitive against the vendor's own pricing page —
   the repo last pushed 2025-12-30, so 2026 changes may not be reflected.

## Project fit (this repo)

Useful for hosting alongside the Begonia kernel CI:

- **Backend for the driver loader / POX app** — Render, Fly.io, or a
  free-tier VPS that can run a long-lived process.
- **Release hosting** — Cloudflare R2 or GitHub Releases for the
  AnyKernel3 zips (note: a 60 MB+ zip exceeds some free tiers).
- **Databases** — Supabase (already connected in this conversation) or
  Neon for Postgres.
- **Preview deploys** — Vercel (also connected here).

⚠️ Free tiers that **sleep** are wrong for a bot or a socket server;
prefer a platform with always-on support, or a free VPS.
