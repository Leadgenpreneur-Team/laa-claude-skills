# deploy-lander-laa v4.1.0

Puts a landing page live, end to end: GitHub repo, Cloudflare Pages and D1, the 50/50 split test, GHL form, tracking scripts, optional Meta Conversions API, the reports dashboard, and a custom domain.

Start it with "deploy my lander" or `/deploy-lander-laa`. See `WORKFLOW.md` for the full walkthrough.

## Three ways to start

- **From build-lander-laa:** give it the folder build-lander-laa made. Most questions are already answered.
- **From your own files:** a folder with your Variant A, Variant B, and thank-you HTML (from Claude Design or anywhere else).
- **Clone:** copy a lander that's already live onto a new ad channel, with its own form, phone number, tracking, and reports.

## What you need

| Tool | Check | Install |
|------|-------|---------|
| GitHub CLI | `gh auth status` | [cli.github.com](https://cli.github.com), then `gh auth login` |
| Wrangler (Cloudflare) | `wrangler whoami` | `npm install -g wrangler`, then `wrangler login` |
| Python 3 | `python3 --version` | Mac: `xcode-select --install`. Windows: [python.org](https://python.org) |

Plus access to the GoHighLevel sub-account the form lives in (if you use GHL).

## Files

```
deploy-lander-laa/
  SKILL.md                        the steps Claude follows
  WORKFLOW.md                     plain-English walkthrough (start here)
  README.md                       this file
  references/
    clone-mode.md                 cloning a live lander for a new ad channel
    ghl-steps.md                  getting the form embed, setting the redirect URL
    cloudflare-steps.md           domain purchase, DNS, split test check
    meta-capi.md                  optional Meta Conversions API setup
```

## What changed in v4.1.0

- New Phase 0: start from a build-lander-laa folder, your own files, or a clone of a live lander
- Clone mode added (`references/clone-mode.md`)
- The reports password is now generated for you (random, unique per lander) and never written into any file
- Reports dashboard "Preview A" link fixed: now `/a` (was `/?ab_variant=a`, which didn't force Variant A)
- Image checks accept `assets/...` paths and confirm each file exists
- After deploy, checks that `README.md`, `wrangler.toml`, and `schema.sql` return 404, and that no password text is in any `.md` file
- Cloudflare login token is found on Mac, Windows, and Linux
- Meta CAPI call test now says to call a pool tracking number from a different phone than the one it forwards to
