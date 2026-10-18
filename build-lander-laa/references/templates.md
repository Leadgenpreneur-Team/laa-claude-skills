# Starting designs

## 1. LAA template pack (best)

The LAA Landing Page Templates zip is in the Skool classroom, lesson M1.5. Members download it once.

Where to look, in order:
1. `$SKILL_DIR/templates/` (already unzipped from a past run)
2. Ask the person. Usual spot: `~/Downloads/LAA Landing Page Templates.zip` or an unzipped folder of the same name. Search Downloads and Desktop for `*Landing Page*` and `*.zip` before asking.

When you find the zip, unzip it into `$SKILL_DIR/templates/` so it's there next time:
```bash
unzip -o "<path to zip>" -d "$SKILL_DIR/templates/"
```

**Pick the template:** list the folder, match on the service name in the file or folder name (dumpster, porta potty, septic, plumbing, roofing, HVAC, home services, law, etc.). If nothing clearly matches, use the closest general one (usually "Home Services") and say which you used. If two could fit, ask.

If the pack has no thank-you page for this service, use the general thank-you page and rewrite its wording for this service.

**Check every file's format.** If it contains `<script type="__bundler/template">`, it's a Claude Design bundle. Copy it into the lander folder, then run `scripts/unbundle.py` on the copy.

Never edit the files in `templates/`. Always work on a copy in the lander folder, and don't leave template copies behind.

## 2. A page the person likes

If they point you at a page (their old lander, a site they like, a Claude Design export):
- Use its **layout and section order** as the starting point.
- Never copy another business's words, photos, logo, or reviews.
- If it's a live site, save it with web fetch, keep the structure, and replace all content.

## 3. Standard layout (always available)

If there's no template, build from `references/page-layout.md`. Write clean, self-contained HTML with the CSS in a `<style>` block (Google Fonts are fine). No frameworks, no build step.
