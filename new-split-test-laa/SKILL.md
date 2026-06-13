---
name: new-split-test-laa
description: "Starts a new A/B split test round on a live client landing page. Use when an A/B test has a winner and it's time to promote the winner and deploy a new challenger. If Variant B won, it becomes the new Variant A and the new challenger becomes Variant B. If Variant A won, the new challenger simply replaces Variant B. Handles bundler detection, GitHub file swap, Cloudflare secret update, redeploy, and verification. Triggers: new split test, start new test, variant won, new challenger, promote winner, /new-split-test-laa, /new-split-test."
version: 1.1.0
---

# new-split-test-laa

Starts a new A/B test round on a live landing page after a test concludes. You provide a new challenger HTML file (built in Claude Design), tell Claude which variant won, and Claude handles the file swap in GitHub, updates the reports dashboard label, optionally resets stats, and redeploys.

## Prerequisites

Run these checks before starting. If either fails, stop and resolve before continuing.

```bash
gh auth status     # must be logged in — any GitHub account
wrangler whoami    # must be logged in — any Cloudflare account
```

**What to look for:**
- `gh auth status` → "Logged in to github.com as [your-username]"
- `wrangler whoami` → shows your Cloudflare account email

If either fails, run `gh auth login` or `wrangler login` to authenticate first.

---

## Phase 1A: Initial Intake

Collect these three fields first — you need them to pull the current files before the user builds the challenger:

| Field | Notes |
|---|---|
| Live URL | The current live lander URL (e.g. `https://samueldeck.com`) |
| GitHub username or org | The same one used when the lander was deployed. Your GitHub username appears in your profile URL: `github.com/[username]`. |
| Which variant won? | A or B |

Once you have these three, proceed immediately to Phase 2 and Phase 3 to clone the repo — do not ask for the challenger file yet.

---

## Phase 2: Identify the Project

Use the live URL to find the Cloudflare Pages project name and GitHub repo slug.

```bash
wrangler pages project list
```

Look for the project whose custom domain matches the provided URL. The project name will be `lander-[SLUG]`. If you can't identify it automatically, show the list and ask:

> "Which project in that list is the one for this client? The project name should look like `lander-[client-slug]`."

Once confirmed:
```bash
SLUG="[client-slug]"
GITHUB_ORG="[USER_GITHUB_ORG]"  # from intake
```

---

## Phase 3: Clone the Repo

```bash
gh repo clone $GITHUB_ORG/lander-$SLUG /tmp/update-$SLUG
```

Verify the key files are present:
```bash
ls /tmp/update-$SLUG/index-a.html /tmp/update-$SLUG/index-b.html /tmp/update-$SLUG/_worker.js
```

If any are missing, stop and investigate before continuing.

Then ask the user how they want to build the challenger:

> "I have the current variant files. How do you want to build the new challenger?
>
> **A — Simple edit (headline, button text, CTA copy, etc.):** Tell me what you want to change and I'll edit the file directly. No Claude Design needed.
>
> **B — Full redesign in Claude Design:** I'll save the current files to `~/Downloads/lander-$SLUG-variants/` so you can upload one into Claude Design, build the new variant there, and export it as a folder."

**If they choose A (simple edit):**

Ask what change they want and which variant it should be based on (the winner, or the current Variant A/B). Make the edit directly to the cloned file:

```bash
# Edit /tmp/update-$SLUG/index-a.html or index-b.html as appropriate
```

After editing, set `/tmp/new-challenger.html` to the edited file path for use in Phase 5:

```bash
cp /tmp/update-$SLUG/[EDITED_FILE] /tmp/new-challenger.html
```

Skip Phase 4 entirely and proceed to Phase 1B.

**If they choose B (Claude Design):**

```bash
mkdir -p ~/Downloads/lander-$SLUG-variants
cp /tmp/update-$SLUG/index-a.html ~/Downloads/lander-$SLUG-variants/index-a.html
cp /tmp/update-$SLUG/index-b.html ~/Downloads/lander-$SLUG-variants/index-b.html
```

Tell them:

> "Saved to `~/Downloads/lander-$SLUG-variants/`. Upload whichever file you want to start from into Claude Design, build your challenger, then export it to a folder on your computer."

---

## Phase 1B: Challenger Intake

Collect the remaining fields:

| Field | Notes |
|---|---|
| New challenger folder path | Only needed if they chose Claude Design (option B) — path to the exported folder |
| New Variant B test description | What one thing does the new Variant B test? (e.g. "New headline — 'Free Estimates This Week Only'"). Keep it short — this label appears in the reports dashboard. |
| Reset stats? | Yes to archive all existing pageview and lead data for a clean comparison; No to keep historical data visible alongside the new test |

If they chose option B (Claude Design), prompt:

> "Put your new challenger HTML file and any new asset files it uses into a folder. Paste the full folder path here when it's ready."

Do not start Phase 4 until the folder path is confirmed. If they chose option A (simple edit), skip Phase 4 entirely.

---

## Phase 4: New Challenger File — Bundler Check

Identify the new challenger HTML file in the provided folder:
```bash
ls "[PROVIDED_FOLDER_PATH]"/*.html
```

If there is more than one `.html` file, ask which one is the new challenger.

**Check for Claude Design bundler wrapper:**

```bash
grep -c "__bundler_loading\|__bundler_thumbnail" "[PROVIDED_FOLDER_PATH]/[CHALLENGER_FILENAME]" || true
```

If it returns `1` or higher, auto-strip using Node.js:

```bash
node << 'NODESCRIPT'
const fs = require('fs');
const zlib = require('zlib');

function processFile(inputPath, outputPath) {
  const html = fs.readFileSync(inputPath, 'utf8');
  const manifestMatch = html.match(/<script type="__bundler\/manifest">([\s\S]*?)<\/script>/);
  const templateMatch = html.match(/<script type="__bundler\/template">([\s\S]*?)<\/script>/);
  if (!manifestMatch || !templateMatch) {
    console.log('Could not find bundler tags — check manually');
    return;
  }
  const manifest = JSON.parse(manifestMatch[1].trim());
  let template = JSON.parse(templateMatch[1].trim());
  const assetsDir = outputPath.replace(/\/[^/]+$/, '/assets');
  if (!fs.existsSync(assetsDir)) fs.mkdirSync(assetsDir, { recursive: true });
  Object.keys(manifest).forEach(uuid => {
    const entry = manifest[uuid];
    let data = Buffer.from(entry.data, 'base64');
    if (entry.compressed) { try { data = zlib.gunzipSync(data); } catch(e) {} }
    const ext = { 'image/png':'png','image/jpeg':'jpg','image/svg+xml':'svg','image/webp':'webp','font/woff2':'woff2','font/woff':'woff','font/ttf':'ttf' }[entry.mime] || 'bin';
    const filename = `${uuid}.${ext}`;
    fs.writeFileSync(`${assetsDir}/${filename}`, data);
    template = template.split(uuid).join(`/assets/${filename}`);
  });
  fs.writeFileSync(outputPath, template, 'utf8');
  console.log('Stripped:', outputPath, '— extracted', Object.keys(manifest).length, 'assets');
}

processFile('[PROVIDED_FOLDER_PATH]/[CHALLENGER_FILENAME]', '/tmp/new-challenger.html');
NODESCRIPT
```

If auto-stripping fails, tell them:

> "Your file is in Claude Design's bundled format. To get the plain HTML: open the file in Chrome, wait for it to fully load, then go to File > Save Page As > choose 'Webpage, HTML Only'. Replace the file in your folder with that saved version and let me know."

Do not proceed until the challenger file is confirmed to be plain HTML.

**Check for missing referenced assets:**

```bash
grep -oE 'src="[^"]*\.(jpg|jpeg|png|svg|webp|gif)"' /tmp/new-challenger.html \
  | grep -v 'src="/assets/\|src="http\|src="data:' || echo "No missing assets detected"
```

If any plain filenames are found, tell the user:

> "Your page references [filename] but it wasn't included in your folder. Please provide that file before we continue."

**Check for leftover template placeholders:**

```bash
grep -iEc "Your .* Co\.|City, ST|123-456-7890|1234567890|logo-ph|your company" /tmp/new-challenger.html || true
```

If any matches are found, tell the user to fix them in Claude Design before continuing.

**Add `data-tel-link` to phone links in the new challenger:**

```python
python3 - <<'PYEOF'
import re

path = '/tmp/new-challenger.html'
with open(path) as f: html = f.read()
tel_links = re.findall(r'href="tel:[^"]*"', html)
tel_with_attr = re.findall(r'href="tel:[^"]*"\s+data-tel-link', html)
if len(tel_links) != len(tel_with_attr):
    html = re.sub(r'(href="tel:[^"]+")(?!\s+data-tel-link)', r'\1 data-tel-link', html)
    with open(path, 'w') as f: f.write(html)
    print(f'Added data-tel-link to {len(tel_links) - len(tel_with_attr)} phone link(s)')
else:
    print(f'data-tel-link already present on all {len(tel_links)} phone link(s)')
PYEOF
```

**Verify GHL form embed is present in the new challenger:**

```python
python3 - <<'PYEOF'
import re
with open('/tmp/new-challenger.html') as f:
    html = f.read()
if re.search(r'leadconnectorhq\.com/widget/form/', html):
    print('GHL form embed: FOUND')
else:
    print('GHL form embed: NOT FOUND — stop here')
PYEOF
```

If not found, stop and tell the user:

> "The new challenger is missing the GHL form embed. Go back to Claude Design, make sure the form iframe (`https://api.leadconnectorhq.com/widget/form/...`) is in the design, then re-export and try again."

Copy any new asset files (non-HTML) from the challenger folder into the repo's `assets/` folder:
```bash
for f in "[PROVIDED_FOLDER_PATH]"/*; do
  [[ "$f" == *.html ]] && continue
  cp "$f" /tmp/update-$SLUG/assets/
done
```

Also copy any bundler-stripped assets — the bundler script saves these to `/tmp/assets/` (sibling of `/tmp/new-challenger.html`):
```bash
if [ -d "/tmp/assets" ] && [ "$(ls -A /tmp/assets)" ]; then
  cp -r /tmp/assets/. /tmp/update-$SLUG/assets/
fi
```

**Re-inject tracking scripts from the existing lander into the new challenger:**

The existing `index-a.html` has the Google Tag, Meta Pixel, and call tracking scripts that were injected during the original deployment. The new challenger from Claude Design does not — copy them over now before the file swap.

```python
python3 - <<'PYEOF'
import re

def find_block(html, keyword):
    """Find a tracking comment block. Handles two formats:
      Simple:    <!-- TRACKING SCRIPTS (X) --> ... <!-- /TRACKING SCRIPTS (X) -->
      Decorated: <!-- === TRACKING SCRIPTS (X) === --> ... <!-- ===...=== -->
    Returns (block_text, end_pos) or (None, -1).
    """
    open_re = re.compile(r'<!--[^>]*' + re.escape(keyword) + r'[^>]*-->', re.IGNORECASE)
    m = open_re.search(html)
    if not m:
        return None, -1
    after = m.end()
    # Try simple closing tag first
    close_simple = f'<!-- /{keyword} -->'
    pos = html.find(close_simple, after)
    if pos != -1:
        end = pos + len(close_simple)
        return html[m.start():end], end
    # Try decorated closing: <!-- ===...=== -->
    cm = re.search(r'<!--\s*=+\s*-->', html[after:])
    if cm:
        end = after + cm.end()
        return html[m.start():end], end
    return None, -1

def replace_or_insert(html, new_block, keyword, anchor_tag):
    """Replace existing keyword block in html, or insert new_block before anchor_tag."""
    open_re = re.compile(r'<!--[^>]*' + re.escape(keyword) + r'[^>]*-->', re.IGNORECASE)
    m = open_re.search(html)
    if m:
        after = m.end()
        close_simple = f'<!-- /{keyword} -->'
        pos = html.find(close_simple, after)
        if pos != -1:
            return html[:m.start()] + new_block + html[pos + len(close_simple):]
        cm = re.search(r'<!--\s*=+\s*-->', html[after:])
        if cm:
            return html[:m.start()] + new_block + html[after + cm.end():]
    return html.replace(anchor_tag, new_block + '\n' + anchor_tag, 1)

with open('/tmp/update-[SLUG]/index-a.html') as f:
    source = f.read()
with open('/tmp/new-challenger.html') as f:
    challenger = f.read()

# ---- HEAD SCRIPTS ----
head_block, _ = find_block(source, 'TRACKING SCRIPTS (HEAD)')

if head_block and '<script' in head_block:
    challenger = replace_or_insert(challenger, head_block, 'TRACKING SCRIPTS (HEAD)', '</head>')
    print('Head scripts: injected via comment block.')
else:
    fallback = re.findall(
        r'<script\b[^>]*(?:googletagmanager\.com|connect\.facebook\.net)[^>]*>[\s\S]*?</script>',
        source, re.IGNORECASE
    )
    if fallback:
        wrapped = '<!-- TRACKING SCRIPTS (HEAD) -->\n' + '\n'.join(fallback) + '\n<!-- /TRACKING SCRIPTS (HEAD) -->'
        challenger = replace_or_insert(challenger, wrapped, 'TRACKING SCRIPTS (HEAD)', '</head>')
        print(f'Head scripts: {len(fallback)} script(s) via pattern fallback.')
    else:
        print('Head scripts: none found — skipped.')

# ---- BODY SCRIPTS ----
body_block, body_end = find_block(source, 'TRACKING SCRIPTS (BODY)')

# Also capture scripts placed AFTER the closing body comment block, before </body>
# (some deployments place call tracking scripts outside the comment markers)
extra_body = []
if body_end != -1:
    body_close = source.lower().rfind('</body>')
    if body_close != -1:
        tail = source[body_end:body_close]
        extra_body = re.findall(
            r'<script\b[^>]*(?:leadconnectorhq|callrail|number_pool|user_session|numberswap)[^>]*>[\s\S]*?</script>',
            tail, re.IGNORECASE
        )

if body_block and ('<script' in body_block or extra_body):
    full = body_block + ('\n' + '\n'.join(extra_body) if extra_body else '')
    challenger = replace_or_insert(challenger, full, 'TRACKING SCRIPTS (BODY)', '</body>')
    note = 'comment block' + (f' + {len(extra_body)} extra script(s) after block' if extra_body else '')
    print(f'Body scripts: injected via {note}.')
else:
    fallback = re.findall(
        r'<script\b[^>]*(?:leadconnectorhq|callrail|number_pool|user_session|numberswap)[^>]*>[\s\S]*?</script>',
        source, re.IGNORECASE
    )
    if fallback:
        wrapped = '<!-- TRACKING SCRIPTS (BODY) -->\n' + '\n'.join(fallback) + '\n<!-- /TRACKING SCRIPTS (BODY) -->'
        challenger = replace_or_insert(challenger, wrapped, 'TRACKING SCRIPTS (BODY)', '</body>')
        print(f'Body scripts: {len(fallback)} script(s) via pattern fallback.')
    else:
        print('Body scripts: none found — skipped.')

with open('/tmp/new-challenger.html', 'w') as f:
    f.write(challenger)
PYEOF
```

If all outputs say "none found — skipped", tell the user:

> "No tracking scripts were found in the existing lander. If tracking was never set up this is expected. If it was, re-add tracking via the deploy skill's Phase 9 after this completes."

---

## Phase 5: Champion Swap

Confirm the file swap with the user before executing.

**If Variant B won** (B becomes the new control, challenger becomes new B):

> "Here's what I'm about to do:
> - Move `index-b.html` (the winner) to `index-a.html` — it becomes the new control
> - Copy your new challenger to `index-b.html` — it becomes the new challenger
>
> Does that look right?"

```bash
cp /tmp/update-$SLUG/index-b.html /tmp/update-$SLUG/index-a.html
cp /tmp/new-challenger.html /tmp/update-$SLUG/index-b.html
```

**If Variant A won** (A stays as-is, challenger replaces B):

> "Here's what I'm about to do:
> - Keep `index-a.html` unchanged — Variant A is still the control
> - Copy your new challenger to `index-b.html` — it becomes the new challenger
>
> Does that look right?"

```bash
cp /tmp/new-challenger.html /tmp/update-$SLUG/index-b.html
```

---

## Phase 6: Update Variant B Label

```bash
# Enter the new test description when prompted
wrangler pages secret put VARIANT_B_LABEL --project-name lander-$SLUG
```

The value to enter is the new Variant B test description from Phase 1 (e.g. `New Headline — "Free Estimates This Week Only"`). This updates the label shown in the reports dashboard.

---

## Phase 7: Reset Stats (if requested)

If they chose to reset stats in Phase 1:

```bash
# Archive all existing events — keeps history but excludes them from active dashboard view
wrangler d1 execute lander-$SLUG-db \
  --command "UPDATE events SET archived = 1 WHERE archived = 0 OR archived IS NULL" \
  --remote

# Log the reset in the audit log
wrangler d1 execute lander-$SLUG-db \
  --command "INSERT INTO audit_log (action, detail) VALUES ('reset', 'Stats reset — new challenger deployed: [NEW_TEST_DESCRIPTION]')" \
  --remote
```

Note: events are archived, not deleted. The reports dashboard filters them out of active stats but the data still exists in the database.

---

## Phase 8: Commit, Push, and Redeploy

```bash
cd /tmp/update-$SLUG
git add index-a.html index-b.html assets/
git commit -m "New split test: [new test description]"
git push
wrangler pages deploy . --project-name lander-$SLUG
```

Wait for the deployment to complete before proceeding.

---

## Phase 9: Verify

**Use a fresh incognito window for all tests.**

**Step 1 — Verify new Variant B:**

Open `https://[DOMAIN]/b` in a fresh incognito window. Confirm the new challenger HTML is showing (not the old one). Check visually — a different headline or image should be immediately visible.

**Step 2 — Verify Variant A:**

Open `https://[DOMAIN]/?ab_variant=a` in a fresh incognito window. Confirm Variant A loads correctly:
- If Variant B won, this should now show the former Variant B (the winner).
- If Variant A won, this should look the same as before.

**Step 3 — Verify reports dashboard label:**

Open `https://[DOMAIN]/reports` and confirm the Variant B column label reflects the new test description.

If any step fails, diagnose before marking complete.

---

## Phase 10: Wrap-Up

Print a summary to the conversation:

```
--- NEW SPLIT TEST DEPLOYED ---

Client:             [BUSINESS NAME]
Live URL:           https://[DOMAIN]
Variant A:          [description — previous winner or original control]
Variant B (new):    [new test description]
Stats reset:        [Yes / No]
Reports page:       https://[DOMAIN]/reports
---
```

Then remind them to log the test transition in the reports dashboard:

> "Head to the reports dashboard at `https://[DOMAIN]/reports` and add two audit log entries:
> 1. Log **what the winning variant was** and its result (e.g. 'Variant B won — 4.2% CVR vs 2.8% for A')
> 2. Log **what the new Variant B is testing**
>
> This keeps a clean record inside the dashboard of every test you've run for this client."
