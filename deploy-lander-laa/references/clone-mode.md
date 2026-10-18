# Clone Mode

Used when Phase 0 of `SKILL.md` is **Clone**. Run **Phase 1 (Clone Intake)** and **Phase 2 (Clone File Setup)** here, then go back to `SKILL.md` at **Phase 3** and run every phase from there to the end.

A clone copies a live lander onto a new ad channel (for example, a Google Ads version of the Facebook lander). It changes only two things compared with a normal deploy:

1. The three page files come from the **source lander's repo**, not a folder.
2. The **GHL form, phone number, and tracking scripts** are swapped for the new channel.

Everything else (GitHub repo, Pages project, D1 database, secrets) is created **fresh** by the normal phases. The clone never shares anything with the source. Never copy the source's `wrangler.toml`, `_worker.js`, `reports.html`, or `schema.sql`. Copying `wrangler.toml` in particular would point the clone at the **source's** database and mix both landers' reports.

---

## Phase 1: Clone Intake

Ask these together, then confirm the answers back.

**1. Source lander**
> "What's the live URL of the lander you're copying? (e.g. https://bobsplumbing.com)"

Find its repo. Match the domain to a Cloudflare Pages project, then to the GitHub repo of the same name:
```bash
wrangler pages project list          # find the project whose domain or *.pages.dev matches
gh repo list [GITHUB_ORG] --limit 200 | grep lander-
```
Confirm: "Found the source repo `[GITHUB_ORG]/lander-[source-slug]`. I'll copy its pages from there. Correct?"

**2. Channel**
> "What ad channel is the copy for? (Google Ads, Facebook, TikTok, etc.)"

**3. New slug**
Suggest the source slug plus the channel: `[source-slug]-google`. Lowercase, hyphens only. This is `[SLUG]` everywhere in `SKILL.md` from Phase 3 on.

**4. Business name.** Same as the source. Confirm it.

**5. GHL form (required, hard stop)**
> "Paste the GHL form embed for **this** channel (the form that tags leads into this channel's pipeline). It replaces the form on the copied page. If we keep the old form, every lead from this channel gets tagged as the old channel."

Record the **new form ID** (the id in `.../widget/form/<id>`) and the **source form ID** from the source pages.

**6. Phone number**
> "What phone number should this channel show? Usually a different tracking number from the original, so you can tell the calls apart."

**7. Head tracking**
> "Paste the tracking code for this channel (e.g. the Google Ads tag). The copy still has the original channel's tracking (e.g. the Meta Pixel). Should I remove it, or keep both? Usually remove, so the wrong channel isn't counting this traffic."

**8. Thank-you conversion event**
> "Paste the conversion event for the thank-you page (e.g. the Google Ads conversion tag), or say 'skip'."

**9. Meta tracking level** for the copy: Full CAPI, Pixel-only, or None (same question as the main intake). CAPI secrets do not carry over from the source. If the copy is Full CAPI, Phase 9.5 sets them fresh for this project.

**10. Split test**
> "Two ways to start the copy's split test:
> - (a) Copy both variants as they are and keep testing what the original was testing.
> - (b) Start fresh: the current winning page becomes Variant A and we make a new Variant B. What one thing should B test?"

Record the Variant A and B descriptions for the Round 1 seed in Phase 6.

**11. Reports username.** The password is generated in Phase 6, same as a normal deploy. Never reuse the source's.

**12. Domain.** Can be TBD until Phase 10.

---

## Phase 2: Clone File Setup

```bash
SLUG="[new-slug]"
SRC_SLUG="[source-slug]"
GITHUB_ORG="[GITHUB_ORG]"
WORK_DIR="/tmp/lander-$SLUG"
SRC_DIR="/tmp/src-$SLUG"
mkdir -p "$WORK_DIR/assets"

# Pull the source repo only to copy its pages
gh repo clone "$GITHUB_ORG/lander-$SRC_SLUG" "$SRC_DIR"

# Copy ONLY the three pages and assets. Never the infrastructure files.
cp "$SRC_DIR"/index-a.html "$SRC_DIR"/index-b.html "$SRC_DIR"/thank-you.html "$WORK_DIR/"
cp -R "$SRC_DIR"/assets/. "$WORK_DIR/assets/" 2>/dev/null || true
[ -f "$SRC_DIR/favicon.png" ] && cp "$SRC_DIR/favicon.png" "$WORK_DIR/assets/"

ls "$WORK_DIR"/wrangler.toml "$WORK_DIR"/_worker.js "$WORK_DIR"/reports.html "$WORK_DIR"/schema.sql 2>/dev/null \
  && echo "STOP: an infrastructure file was copied. Delete it; only pages and assets belong here." \
  || echo "Clean: only pages and assets copied"
```

If split test option (b) was chosen, rebuild `index-b.html` from the new Variant B (build-lander-laa can make it from `index-a.html` with the one change), then run the normal Phase 2 checks on it.

### Swap for the new channel

**a. GHL form.** In `index-a.html` and `index-b.html`, replace the source form's whole `<iframe ...></iframe>` block with the new embed. Keep exactly one `form_embed.js` script tag per file.

**b. Phone number.** Replace it everywhere, in both forms it appears (digits in `tel:` links, formatted in visible text):
```bash
for f in index-a.html index-b.html thank-you.html; do
  python3 - "$WORK_DIR/$f" <<'PY'
import sys, re
p = sys.argv[1]; s = open(p).read()
OLD_DIGITS, NEW_DIGITS = "[OLD 10 digits]", "[NEW 10 digits]"
OLD_SHOWN,  NEW_SHOWN  = "[OLD as shown, e.g. (555) 123-4567]", "[NEW as shown]"
s = s.replace(OLD_SHOWN, NEW_SHOWN)
s = re.sub(r'(tel:\+?1?)' + OLD_DIGITS, r'\g<1>' + NEW_DIGITS, s)
open(p, "w").write(s)
print(p, "old number left:", s.count(OLD_DIGITS) + s.count(OLD_SHOWN))
PY
done
```
"old number left" must be 0 for every file. If the number appears in another format (e.g. 555.123.4567), run it again for that format.

**c. Remove the source channel's tracking** from all three pages if intake Q7 said remove (e.g. the Meta Pixel block in `<head>`, a pixel-only `fbq('track','Lead')` on the thank-you page). Leave the empty `TRACKING SCRIPTS` and `CONVERSION TRACKING` comment blocks in place. The new channel's scripts are added in the normal Phase 9.

**d. Call click tracking.** Make sure every `tel:` link still has `data-tel-link` (the normal Phase 2 Step 3 script does this; run it on `$WORK_DIR`).

---

## Back to SKILL.md

Go to **Phase 3** and continue to the end, with these extra checks:

- **Phase 4 (form), hard stop:** the new form ID is in both index files and the source form ID is in neither:
  ```bash
  grep -c "[NEW_FORM_ID]" $WORK_DIR/index-a.html $WORK_DIR/index-b.html   # 1+ each
  grep -c "[SRC_FORM_ID]" $WORK_DIR/index-a.html $WORK_DIR/index-b.html   # 0 each
  ```
- **Phase 6:** before deploying, `grep database_name wrangler.toml` must show `lander-[SLUG]-db`, never the source's database.
- **Phase 11:** submit a test lead and confirm in GHL it lands in the **new** channel's pipeline with the **new** tags. Confirm the reports page shows the new business label and only this lander's data.
