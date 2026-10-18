# LAA Claude Skills

Claude Code skills for Local Agency Accelerator (LAA) members: building, deploying, editing, and split-testing landing pages. They work for agency owners building for clients and for business owners building their own page.

## Skills

| Skill | What it does | Say |
|---|---|---|
| **build-lander-laa** | Builds the pages (Variant A, Variant B, thank-you) from the business's website and Google reviews, then lets you preview and change them before anything goes live | "build a lander" |
| **deploy-lander-laa** | Puts the pages live: GitHub, Cloudflare Pages and D1, split test, GHL form, tracking, reports dashboard, custom domain. Also clones a live lander for a new ad channel | "deploy my lander" or "clone my lander for Google Ads" |
| **edit-lander-laa** | Makes a small change to a live lander (phone number, headline, image, form) | "edit my lander" |
| **new-split-test-laa** | Starts a new A/B test round after a winner is picked | "start a new split test" |

The usual order: **build → deploy → (edit as needed) → new split test** when a test has a winner.

## Install

1. Download this repo as a zip (green **Code** button → **Download ZIP**) and unzip it.
2. Copy the four skill folders into `~/.claude/skills/` (create the folder if it doesn't exist).
3. Restart the Claude desktop app. Type `/` in Claude Code and you should see the skills listed.

## What you need

- The Claude desktop app with Claude Code
- Python 3 (Macs: `xcode-select --install` if it's missing)
- For deploying: a GitHub account with the GitHub CLI logged in (`gh auth login`), and a Cloudflare account with Wrangler logged in (`npm install -g wrangler`, then `wrangler login`). deploy-lander-laa checks both and walks you through anything missing.
- Optional: the **LAA Landing Page Templates** pack (Skool lesson M1.5) for build-lander-laa

## Template

Every deployed lander is created from [laa-lander-template](https://github.com/Leadgenpreneur-Team/laa-lander-template).
