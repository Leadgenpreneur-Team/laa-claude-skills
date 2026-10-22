# Starting designs

## 1. LAA template pack (best)

The LAA Landing Page Templates zip is in the Skool classroom, lesson M1.4. Members download it once.

Where to look, in order:
1. `$SKILL_DIR/templates/` (already unzipped from a past run)
2. Ask the person. Usual spot: `~/Downloads/LAA Landing Page Templates.zip` or an unzipped folder of the same name. Search Downloads and Desktop for `*Landing Page*` and `*.zip` before asking.

When you find the zip, unzip it into `$SKILL_DIR/templates/` so it's there next time:
```bash
unzip -o "<path to zip>" -d "$SKILL_DIR/templates/"
```

**What's in the pack** (October 2026 version):

| File | Use it for |
|---|---|
| `Plumbing Landing Page.html` | Plumbing, drain, water heater |
| `Home Services Landing Page.html` | Roofing, HVAC, electrical, pest, landscaping, cleaning services, and any home service without its own template (septic, junk removal, etc.) |
| `Bathroom Remodel Landing Page Template.html` | Bathroom and kitchen remodels, tub and shower conversions. Uses the shared stylesheet `assets/styles.css`, so copy that file into the lander's `assets/` too |
| `Rug Cleaning Landing Page.html` | Rug, carpet, and upholstery cleaning |
| `Dental Landing Page Template.html` | Dental practices (general, cosmetic, implants, Invisalign) |
| `Family Law Landing Page.html` | Family law, and with care other law practice areas |
| `Home Services Thank You.html` | The thank-you page for **every** template. Rewrite its wording for the service (copy-rules.md, "Wording by service") |
| `privacy.html`, `terms.html` | Privacy policy and terms pages for every lander (see "Legal pages" below) |

Dumpster rental and porta potty aren't in the pack. Use Home Services for those and rewrite the wording with the Dumpster or Porta Potty row of the service table.

If a file name doesn't match this table (the pack gets updated), pick the closest clear match and say which one you used. If two could fit, ask.

**Things every template in the pack needs:**
- **Clean up first.** Run `scripts/unbundle.py` on every copied page, even plain ones. Several templates carry a leftover Claude Design `<template id="__bundler_thumbnail">` block, and the script removes it.
- **Placeholders come in many shapes:** `[PHONE]`, `[Business Name]`, `[City, ST]`, `[Town 1]`, `[First L.]`, `[N.N]`, `[X–X]`, `[Doctor Name]`, plus sample lines like "Drop in a real Google quote here" and the GHL form `src=".../widget/form/XXXX"`. `check_lander.py` finds all of these.
- **Logo:** templates point at `logo.svg` next to the page. Put the real logo in `assets/` and update every reference (header, footer, thank-you page).
- **Tracking comment:** templates have one `CONVERSION TRACKING PLACEHOLDER` comment in `<head>`. Replace it with `<!-- TRACKING SCRIPTS (HEAD) -->`, add `<!-- TRACKING SCRIPTS (BODY) -->` right after `<body>`, and on the thank-you page also add `<!-- CONVERSION TRACKING -->` in `<head>`. deploy-lander-laa looks for those exact comments.
- **Review widget slot:** Plumbing, Home Services, and Family Law have a "GO HIGH LEVEL REVIEW WIDGET" slot under the review cards. We don't use review widgets anymore. Delete the whole slot (the comment, the `.review-widget-wrap` div, and its contents) and use static review cards (copy-rules.md, "Reviews").
- **Sample badges:** strips like `cert-logo-ph` ("HomeAdvisor / Angi", "Google Reviews", BBB) are placeholders. Keep only badges a real profile supports, as plain text, and delete the rest.
- **Photos:** the pack ships without photos (Dental's `assets/before.jpg` and `assets/after.jpg` aren't included). Every image slot needs a real photo or gets removed cleanly.

### Legal pages

Google Ads and Meta both expect a privacy policy on pages that collect contact info. For every lander:
1. Copy `privacy.html` and `terms.html` into the lander folder (same names).
2. Fill every placeholder: business name, phone, city and state, email, and the date. Street address only if the business lists one publicly. Ask for a contact email if you can't find one.
3. Templates have the footer links commented out (they point at names like `plumbing-privacy.html`). Uncomment them on both pages and point them at `privacy.html` and `terms.html`.
4. These pages are standard boilerplate, not legal advice. Say so once in the report so the person can have someone review them if they want.

Never edit the files in `templates/`. Always work on a copy in the lander folder, and don't leave template copies behind.

## 2. A page the person likes

If they point you at a page (their old lander, a site they like, a Claude Design export):
- Use its **layout and section order** as the starting point.
- Never copy another business's words, photos, logo, or reviews.
- If it's a live site, save it with web fetch, keep the structure, and replace all content.

## 3. Standard layout (always available)

If there's no template, build from `references/page-layout.md`. Write clean, self-contained HTML with the CSS in a `<style>` block (Google Fonts are fine). No frameworks, no build step.
