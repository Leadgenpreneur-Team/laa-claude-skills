# deploy-lander — v1.2.0

Full end-to-end deployment skill for DJM client landing pages. Handles template customization, GitHub repo creation, Cloudflare Pages + D1, GHL form injection, split-test verification, UTM tracking, call click tracking, and domain setup.

## Installation

1. Download `deploy-lander-v1.2.0.zip`
2. In Claude Code, run:
   ```
   /install-skill deploy-lander-v1.2.0.zip
   ```
3. Follow the prompts

## Prerequisites

These tools must be installed and authenticated on your machine before using the skill:

| Tool | Check | Install |
|------|-------|---------|
| GitHub CLI | `gh auth status` | [cli.github.com](https://cli.github.com) |
| Wrangler (Cloudflare) | `wrangler whoami` | `npm install -g wrangler` |
| Python 3 | `python3 --version` | [python.org](https://python.org) |

You also need:
- Access to the **strive-marketing** GitHub org
- Wrangler authenticated to the **Strive Marketing** Cloudflare account
- Access to the client's GHL sub-account

## Dependencies

No Python packages or Node modules required. The skill uses only Python standard library and shell commands.

## Usage

```
/deploy-lander
```

Or say: "Deploy a lander for [client name]"

Claude will collect intake info and walk you through all 12 phases.

## What's Included

```
deploy-lander/
├── SKILL.md          — skill definition and phase-by-phase instructions
├── WORKFLOW.md       — usage guide (start here)
├── README.md         — this file
├── references/
│   ├── intake.md     — intake form template
│   ├── ghl-steps.md  — GHL form embed and redirect instructions
│   └── cloudflare-steps.md — Cloudflare domain and split-test steps
└── assets/
    └── templates/
        └── djm/
            ├── porta-potty/     — porta potty lander template
            └── dumpster-rental/ — dumpster rental lander template
```

## What Changed in v1.2.0

- Fixed GHL merge tag: `{{contact.first_name}}` corrected to `{{contact.name}}`
- Phase 2 script now adds `data-tel-link` to all call buttons automatically (fixes call click tracking)
- Phase 7 simplified — no longer tries to verify merge tags before GHL redirect is set
- Phase 8 now includes a full verification test: incognito window, UTM test URL with all tracked parameters, reports dashboard check
- Phase 11 now requires repeating the full verification test after switching to the custom domain
- Added CRITICAL warning in GHL steps about not dropping the query string from the redirect URL
- Generated WORKFLOW.md with troubleshooting guide
