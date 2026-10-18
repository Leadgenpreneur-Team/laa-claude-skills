# build-lander-laa v1.0.0

Builds a finished landing page for a local service business, lets you preview and change it, then hands it to **deploy-lander-laa** to put it live.

Works for agency owners (building for a client) and business owners (building their own page). Kickoff notes and onboarding surveys help but aren't required. Claude reads the business's website and Google reviews and asks you for anything else.

## What you get

```
~/Landers/[Business] [Service]/
  index-a.html       Variant A
  index-b.html       Variant B (one change, for the split test)
  thank-you.html     Thank-you page
  assets/            photos, logo, map
  lander-notes.md    sources, reviews used, open questions, deploy handoff
```

## How to use it

Say "build a lander" or `/build-lander-laa`. Claude asks a few questions, researches the business, writes the pages, and opens them in your browser. Then you can:

- Ask for changes in chat
- Get a shareable Claude artifact link to open on your phone or send to a client for comments
- Edit it by hand in Claude Design and give the export back

When you say it looks good, Claude offers to deploy it with deploy-lander-laa.

## What you need

- The Claude desktop app with Claude Code
- Python 3 (Macs: run `xcode-select --install` if it's missing)
- Optional: the **LAA Landing Page Templates** pack from Skool lesson M1.5. Unzip it into this skill's `templates/` folder, or Claude asks where it is. Without it, Claude builds from a standard layout.
- Optional: Playwright, for the automatic phone and desktop layout check (`pip3 install playwright && python3 -m playwright install chromium`). Without it, you check the layout by eye.

## Files

```
build-lander-laa/
  SKILL.md                  the steps Claude follows
  references/
    intake.md               the interview and the deploy handoff block
    templates.md            how the starting design is chosen
    page-layout.md          the standard layout when there's no template
    copy-rules.md           wording, phone links, reviews, thank-you page rules
    preview.md              browser, artifact, and Claude Design preview loop
  scripts/
    check_lander.py         placeholder, phone, image, and wording checks
    render_check.py         headline length and layout check at 390px and 1280px
    make_preview.py         builds the artifact preview copy
    unbundle.py             turns a Claude Design bundle into plain HTML
  templates/                put the M1.5 template pack here
```
