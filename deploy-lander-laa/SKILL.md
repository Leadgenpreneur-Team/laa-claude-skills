---
name: deploy-lander-laa
description: "Deploys a landing page end-to-end for agency owners and business owners. Starts from a folder made by build-lander-laa, finished HTML files from Claude Design, or a clone of a live lander for a new ad channel. Handles GitHub repo creation, Cloudflare Pages + D1 + env vars, GHL form injection, split-test setup, Meta tracking (pixel-only or full CAPI), tracking scripts, SEO/favicon, automated domain connection, and Google Ads sitelinks. Triggers: deploy lander, deploy my lander, clone lander, duplicate lander for google/facebook, set up landing page, launch client lander, deploy lander for client, /deploy-lander-laa, /deploy-lander."
version: 4.1.0
---

# deploy-lander-laa

Deployment engine for landing pages. Build the pages first (with **build-lander-laa**, or in Claude Design). This skill handles everything after that: GitHub, Cloudflare, GHL form, split testing, tracking, and domain connection.

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

**wrangler not in PATH?** If `wrangler whoami` fails with "command not found", try `npx wrangler whoami`. If that works, use `npx wrangler` for every wrangler command throughout the deployment. If neither works, run `npm install -g wrangler` first.

You also need access to the client's GHL sub-account before Phase 4.

---

## Phase 0: Where the pages come from

Ask (skip the question if the person already said, e.g. build-lander-laa handed off a folder):

> "Where are the pages coming from?
> - **build-lander-laa folder**: you just built them with build-lander-laa (or have the folder it made)
> - **My own files**: HTML files you made in Claude Design or elsewhere
> - **Clone**: copy a lander that's already live onto a new ad channel (e.g. make a Google Ads version of your Facebook lander, with its own form, tracking number, and reports)"

- **build-lander-laa folder** → read the `## Handoff to deploy-lander-laa` block at the end of `lander-notes.md` in that folder. Pre-fill every intake field it covers (business name, suggested slug, phone, Variant A and B descriptions, folder path) and only ask for the rest in Phase 1. Its pages are already named `index-a.html`, `index-b.html`, `thank-you.html`, so the Phase 2 mapping is automatic (still show it).
- **My own files** → run Phase 1 and Phase 2 below as written.
- **Clone** → run Phase 1 and Phase 2 from [`references/clone-mode.md`](references/clone-mode.md) **instead of** Phase 1 and Phase 2 below, then come back here at **Phase 3** and run every phase from there to the end. The clone gets its own repo, Pages project, D1 database, and secrets. It never shares anything with the source lander.

If they don't have pages yet: "No problem. Run build-lander-laa first (say 'build a lander'), and it will hand the folder back here when you're happy with it."

---

## Phase 1: Intake

Ask these questions up front. All are required except domain (can be TBD) and agency logo (optional).

| Field | Notes |
|---|---|
| GitHub username or org | Where client repos will be created. Your GitHub username appears in your profile URL: `github.com/[username]`. If using an org, use the org name shown at `github.com/orgs/[orgname]`. When unsure, use your personal username. |
| HTML folder path | Full path to the folder containing your lander files (pre-filled for a build-lander-laa folder). Put your Variant A file, Variant B file, and thank-you page in it. You don't need to rename them first. Claude will identify each one by filename and confirm before copying. |
| Client slug | Lowercase, hyphens only. Used for the GitHub repo name and Cloudflare project. If the client has multiple services, differentiate by service: `smith-landscaping` vs `smith-sprinkler-repair`. If it's their only service, keep it short: `smith-hvac`. |
| Business name | Exact name as it should appear in the reports dashboard and commits. |
| Phone number | Any format — used to verify call tracking attributes are present. |
| Variant A description | Briefly describe what Variant A shows — e.g. "Original layout — hero + form above fold" or "Headline: Get a Free Quote Today". Appears in the reports dashboard for Round 1. |
| Variant B description | What one thing does Variant B test vs Variant A? e.g. "New headline — 'Same-Day Service Available'". Appears in the reports dashboard. |
| Reports username | Username to log in to the reports dashboard. Suggest `admin` or the client's first name. |
| Reports password | **Don't ask. Claude generates it** in Phase 6 (`openssl rand -base64 24 \| tr -d '/+=' \| cut -c1-20`), unique per lander. Claude shows it once in Phase 12 and the person saves it in a password manager. It never goes in README.md or any file in the repo. |
| Meta tracking level | Ask: "Will you be running Meta (Facebook/Instagram) ads for this client? If so, do you have — or plan to get — a Conversions API access token?" Three options: **Full CAPI** — they have both a Meta Pixel and a CAPI access token. **Pixel-only** — they have the Pixel but no access token. **No Meta** — no Meta ads at all. |
| Domain name | Optional at this stage. Note it if they have one — needed at Phase 10. |
| Agency logo URL | Optional. A hosted URL to your agency logo (PNG or SVG). Appears in the header of the client-facing reports dashboard. Leave blank to omit. |

After confirming all fields, set the Meta tracking level as a shell variable for use in later phases:

```bash
META_TRACKING="[full-capi or pixel-only or none]"
```

Confirm all fields before moving to Phase 2.

---

## Phase 2: Prep Working Files

### Step 1 — Identify and copy files

```bash
SLUG="[client-slug]"
WORK_DIR="/tmp/lander-$SLUG"
mkdir -p "$WORK_DIR/assets"

ls "[PROVIDED_FOLDER_PATH]"/*.html
```

Identify which file is which based on the filename:
- File with "variant b", "variant-b", "v2", or "- b" (case-insensitive) → `index-b.html`
- File with "thank you" or "thank-you" (case-insensitive) → `thank-you.html`
- The remaining HTML file → `index-a.html`

Confirm the mapping with the user before copying:

> "Here's how I'm mapping your files:
> - `index-a.html` ← [FILENAME]
> - `index-b.html` ← [FILENAME]
> - `thank-you.html` ← [FILENAME]
>
> Does that look right?"

Once confirmed:

```bash
cp "[PROVIDED_FOLDER_PATH]/[VARIANT_A_FILENAME]" "$WORK_DIR/index-a.html"
cp "[PROVIDED_FOLDER_PATH]/[VARIANT_B_FILENAME]" "$WORK_DIR/index-b.html"
cp "[PROVIDED_FOLDER_PATH]/[THANK_YOU_FILENAME]" "$WORK_DIR/thank-you.html"

# Copy images: the folder's assets/ subfolder (build-lander-laa and Claude Design exports)
# plus any loose image files sitting next to the pages. Notes (.md) are never copied.
if [ -d "[PROVIDED_FOLDER_PATH]/assets" ]; then
  cp -R "[PROVIDED_FOLDER_PATH]/assets/." "$WORK_DIR/assets/"
fi
for f in "[PROVIDED_FOLDER_PATH]"/*.{jpg,jpeg,png,webp,gif,svg,ico}; do
  [ -f "$f" ] && cp "$f" "$WORK_DIR/assets/"
done
```

If they do not have a thank-you page, stop here:
> "You need a thank-you page before we can continue. build-lander-laa can make one that matches your lander (say 'build a thank-you page for this lander'), or build one in Claude Design. Come back once you have it."

### Step 2 — Bundler strip

Claude Design wraps exported files in a bundler format. Check all three files:

```bash
grep -c "__bundler_loading\|__bundler_thumbnail" "$WORK_DIR/index-a.html" || true
grep -c "__bundler_loading\|__bundler_thumbnail" "$WORK_DIR/index-b.html" || true
grep -c "__bundler_loading\|__bundler_thumbnail" "$WORK_DIR/thank-you.html" || true
```

If any file returns `1` or higher, strip it using Node.js:

```bash
node << 'NODESCRIPT'
const fs = require('fs');
const zlib = require('zlib');

function processFile(inputPath) {
  const html = fs.readFileSync(inputPath, 'utf8');
  const manifestMatch = html.match(/<script type="__bundler\/manifest">([\s\S]*?)<\/script>/);
  const templateMatch = html.match(/<script type="__bundler\/template">([\s\S]*?)<\/script>/);
  if (!manifestMatch || !templateMatch) {
    console.log('Could not find bundler tags in', inputPath, '— skip or check manually');
    return;
  }
  const manifest = JSON.parse(manifestMatch[1].trim());
  let template = JSON.parse(templateMatch[1].trim());
  const assetsDir = inputPath.replace(/\/[^/]+$/, '/assets');
  if (!fs.existsSync(assetsDir)) fs.mkdirSync(assetsDir, { recursive: true });
  Object.keys(manifest).forEach(uuid => {
    const entry = manifest[uuid];
    let data = Buffer.from(entry.data, 'base64');
    if (entry.compressed) { try { data = zlib.gunzipSync(data); } catch(e) {} }
    const ext = { 'image/png':'png','image/jpeg':'jpg','image/svg+xml':'svg','image/webp':'webp','font/woff2':'woff2','font/woff':'woff','font/ttf':'ttf','application/font-woff2':'woff2' }[entry.mime] || 'bin';
    const filename = `${uuid}.${ext}`;
    fs.writeFileSync(`${assetsDir}/${filename}`, data);
    template = template.split(uuid).join(`assets/${filename}`);
  });
  fs.writeFileSync(inputPath, template, 'utf8');
  console.log('Stripped:', inputPath, '— extracted', Object.keys(manifest).length, 'assets');
}

processFile('/tmp/lander-[SLUG]/index-a.html');
processFile('/tmp/lander-[SLUG]/index-b.html');
processFile('/tmp/lander-[SLUG]/thank-you.html');
NODESCRIPT
```

After stripping, verify all three are clean:

```bash
grep -c "__bundler_loading\|__bundler_thumbnail" "$WORK_DIR/index-a.html" || true  # should be 0
grep -c "__bundler_loading\|__bundler_thumbnail" "$WORK_DIR/index-b.html" || true  # should be 0
grep -c "__bundler_loading\|__bundler_thumbnail" "$WORK_DIR/thank-you.html" || true  # should be 0
```

Images are referenced as relative `assets/...` paths, which work on every route (`/`, `/a`, `/b`, `/thank-you`).

If auto-stripping fails, tell the user:

> "Your file is in Claude Design's bundled format. To get the plain HTML: open the file in Chrome, wait for it to fully load, then go to File > Save Page As > choose 'Webpage, HTML Only'. Replace the file with that saved version and let me know."

Do not proceed until all three files are confirmed plain HTML.

### Step 3 — Verify call tracking attributes

The `data-tel-link` attribute must be present on all `tel:` links for call click tracking to work in the reports dashboard. Check and add if missing:

```python
python3 - <<'PYEOF'
import re, os

work_dir = '/tmp/lander-[SLUG]'

for fname in ['index-a.html', 'index-b.html', 'thank-you.html']:
    path = os.path.join(work_dir, fname)
    if not os.path.exists(path):
        continue
    with open(path) as f:
        html = f.read()

    tel_links = re.findall(r'href="tel:[^"]*"', html)
    tel_with_attr = re.findall(r'href="tel:[^"]*"\s+data-tel-link', html)

    if len(tel_links) == len(tel_with_attr):
        print(f'{fname}: data-tel-link already present on all {len(tel_links)} phone link(s) — no changes needed')
    else:
        html = re.sub(r'(href="tel:[^"]+")(?!\s+data-tel-link)', r'\1 data-tel-link', html)
        with open(path, 'w') as f:
            f.write(html)
        added = len(tel_links) - len(tel_with_attr)
        print(f'{fname}: added data-tel-link to {added} phone link(s)')
PYEOF
```

**Check for missing referenced assets:**

Pages may reference images as `assets/x.jpg`, `/assets/x.jpg`, a plain `x.jpg`, or a CSS `url()`. Every local reference must point inside `assets/` and the file must exist, or it breaks on the live site.

```python
python3 - <<'PYEOF'
import re, os

work_dir = '/tmp/lander-[SLUG]'
missing = []

for fname in ['index-a.html', 'index-b.html', 'thank-you.html']:
    path = os.path.join(work_dir, fname)
    if not os.path.exists(path):
        continue
    html = open(path).read()
    refs  = re.findall(r'(?:src|href)="([^"]*\.(?:jpg|jpeg|png|svg|webp|gif|ico))"', html, re.I)
    refs += re.findall(r"url\(['\"]?([^)'\"]*\.(?:jpg|jpeg|png|svg|webp|gif))['\"]?\)", html, re.I)
    for ref in set(refs):
        if ref.startswith(('http', 'data:', '//')):
            continue
        rel = ref.lstrip('/')
        if not rel.startswith('assets/'):
            missing.append(f'{fname}: {ref} is not inside assets/ (move the file into assets/ and update the reference)')
        elif not os.path.exists(os.path.join(work_dir, rel)):
            missing.append(f'{fname}: {ref} (file not found)')

print('\n'.join('MISSING: ' + m for m in missing) or 'No missing assets detected.')
PYEOF
```

If any missing assets are reported, tell the user:

> "Your page references [filename] but it wasn't included in your folder. Please provide that file before we continue."

**Spot-check for leftover template placeholders:**

```bash
grep -iEc "Your .* Co\.|City, ST|123-456-7890|1234567890|logo-ph|your company" "$WORK_DIR/index-a.html" || true
grep -iEc "Your .* Co\.|City, ST|123-456-7890|1234567890|logo-ph|your company" "$WORK_DIR/index-b.html" || true
```

If any are found, fix them (or, for a build-lander-laa folder, re-run its `check_lander.py`) before continuing.

---

## Phase 3: Confirm Variants

Tell the user:
> "I have both variants ready in the working folder:
> - `index-a.html` — Variant A ([Variant A description from intake])
> - `index-b.html` — Variant B ([Variant B description from intake])
>
> Confirm these are correct and we'll move on to the GHL form check."

Wait for confirmation before proceeding.

---

## Phase 4: GHL Form Embed

Check both variants for an existing GHL form embed:

```python
python3 - <<'PYEOF'
import re, os

work_dir = '/tmp/lander-[SLUG]'
pattern = r'<iframe[^>]+src="https://api\.leadconnectorhq\.com/widget/form/[^"]*"'
results = {}

for fname in ['index-a.html', 'index-b.html']:
    path = os.path.join(work_dir, fname)
    with open(path) as f:
        html = f.read()
    results[fname] = bool(re.search(pattern, html))
    print(f'{fname}: GHL form {"FOUND" if results[fname] else "NOT FOUND"}')
PYEOF
```

**Based on the result:**

- **Both files have the form** — confirm it's present and skip to Phase 5. No action needed.
- **Only one file has it** — inject the embed code into the other. Get the embed code by reading the file that already has it and copying the iframe block.
- **Neither file has the form** — load `references/ghl-steps.md` → "Getting the Form Embed Code" and walk the user through it.

Once the embed code is confirmed in both files, verify:
1. The iframe `src` URL is present in both `index-a.html` and `index-b.html`
2. The `<script src="https://link.msgsndr.com/js/form_embed.js">` tag is right after the iframe in both files
3. Any placeholder like `<!-- GHL FORM EMBED -->` or "Paste your form embed code here" is gone

---

## Phase 5: GitHub Repo

```bash
SLUG="[client-slug]"
WORK_DIR="/tmp/lander-$SLUG"
REPO_DIR="/tmp/repo-$SLUG"
GITHUB_ORG="[USER_GITHUB_ORG]"  # from intake

gh repo create $GITHUB_ORG/lander-$SLUG \
  --template Leadgenpreneur-Team/laa-lander-template \
  --private

# Give GitHub a moment to initialize the template before cloning
sleep 3

gh repo clone $GITHUB_ORG/lander-$SLUG $REPO_DIR
cd $REPO_DIR
```

**Before copying**, verify the infrastructure files exist in the cloned repo — they come from the template:
```bash
ls _worker.js reports.html schema.sql
```
If any are missing, stop — something went wrong with the template clone. Do not proceed until all three are present.

**If an agency logo URL was provided in intake**, inject it into the reports dashboard now:

```python
python3 - <<'PYEOF'
agency_logo_url = '[AGENCY_LOGO_URL]'  # leave empty string if not provided

with open('reports.html') as f:
    html = f.read()

if agency_logo_url:
    logo_tag = f'<img src="{agency_logo_url}" alt="Agency" style="max-height:28px;width:auto;display:block;margin-bottom:6px;">'
    html = html.replace(
        '<div class="dash-brand">',
        logo_tag + '\n      <div class="dash-brand">',
        1
    )
    with open('reports.html', 'w') as f:
        f.write(html)
    print('Agency logo injected into reports.html.')
else:
    print('No agency logo — reports.html unchanged.')
PYEOF
```

```bash
# Copy all customized files in (must be run from $REPO_DIR)
cp $WORK_DIR/index-a.html $WORK_DIR/index-b.html $WORK_DIR/thank-you.html .

# Copy assets folder if it exists (bundler-stripped images land here)
if [ -d "$WORK_DIR/assets" ] && [ "$(ls -A $WORK_DIR/assets)" ]; then
  mkdir -p assets
  cp -r $WORK_DIR/assets/. assets/
fi

git add .
git commit -m "Initial client setup: [Business Name]"
git push
```

**Note:** Do not `cp -r $WORK_DIR/* .` — that would overwrite `_worker.js`, `reports.html`, and `schema.sql` from the template.

---

## Phase 6: Cloudflare Pages + D1 + Env Vars

```bash
cd /tmp/repo-[SLUG]

# Create Pages project
wrangler pages project create lander-[SLUG] --production-branch main

# Check D1 database count before creating — Cloudflare's free tier limit is 10
wrangler d1 list
```

Count the databases in the list. If there are already 10, stop and tell the user:

> "You've hit Cloudflare's 10-database limit. You'll need to delete an unused database before we can continue. Run `wrangler d1 list` to see what's there and let me know which one to remove, or delete it yourself in the Cloudflare dashboard under Workers & Pages > D1."

Do not proceed until there's room for a new database.

```bash
# Create D1 database — copy the database_id from the output
wrangler d1 create lander-[SLUG]-db
```

Create `wrangler.toml` in the repo root (use the database_id from the command above):

```toml
name = "lander-[SLUG]"
compatibility_date = "2024-09-23"
pages_build_output_dir = "."

[[d1_databases]]
binding = "DB"
database_name = "lander-[SLUG]-db"
database_id = "[DATABASE_ID_FROM_ABOVE]"
```

```bash
# Run schema against remote D1
wrangler d1 execute lander-[SLUG]-db --file=schema.sql --remote

# Seed Round 1 — records what each variant is testing from day one
wrangler d1 execute lander-[SLUG]-db \
  --command "INSERT INTO rounds (round_number, variant_a_label, variant_b_label) VALUES (1, '[VARIANT_A_DESCRIPTION]', '[VARIANT_B_DESCRIPTION]')" \
  --remote
```

Generate the reports password and API token and set every secret in **one** command, so the generated values never have to be retyped. Both values are random and unique to this lander, never based on the slug or business name. Fill in the bracketed values first:

```bash
P=lander-[SLUG]
REPORTS_PASS=$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-20)
REPORTS_TOKEN=$(openssl rand -hex 16)
printf '%s' "[REPORTS_USERNAME]"   | wrangler pages secret put REPORTS_USER  --project-name $P
printf '%s' "$REPORTS_PASS"        | wrangler pages secret put REPORTS_PASS  --project-name $P
printf '%s' "$REPORTS_TOKEN"       | wrangler pages secret put REPORTS_TOKEN --project-name $P
printf '%s' "[BUSINESS NAME]"      | wrangler pages secret put PROJECT_NAME  --project-name $P
printf '%s' "[SLUG]"               | wrangler pages secret put PROJECT_SLUG  --project-name $P
printf '%s' "/a"                   | wrangler pages secret put VARIANT_A_URL --project-name $P
printf '%s' "/b"                   | wrangler pages secret put VARIANT_B_URL --project-name $P
echo "Reports password: $REPORTS_PASS"
```

Every line should end with `Success! Uploaded secret`. Note the printed password: it's shown to the person in Phase 12 and is **never** written into any file. (The token is only used by the dashboard; nobody needs to save it.)

If piping doesn't work on their machine, run each `wrangler pages secret put NAME --project-name lander-[SLUG]` on its own and paste the value at the hidden prompt. `VARIANT_A_URL` is `/a` and `VARIANT_B_URL` is `/b`.

```bash
# Commit wrangler.toml and deploy
git add wrangler.toml && git commit -m "Add wrangler.toml with D1 binding"
git push
wrangler pages deploy . --project-name lander-[SLUG]
```

**Wire up the D1 binding via Cloudflare API** — `wrangler.toml` alone does NOT connect the database to the Pages project. This API call is required or the reports page will show "DB not configured":

```bash
CF_TOKEN=""
for f in ~/Library/Preferences/.wrangler/config/default.toml ~/.config/.wrangler/config/default.toml ~/.wrangler/config/default.toml "$APPDATA/xdg.config/.wrangler/config/default.toml"; do
  [ -f "$f" ] && CF_TOKEN=$(grep oauth_token "$f" | awk '{print $3}' | tr -d '"') && [ -n "$CF_TOKEN" ] && break
done
if [ -z "$CF_TOKEN" ]; then
  echo "ERROR: Could not find Wrangler auth token. Make sure you're logged in (run: wrangler whoami) and try again."
  exit 1
fi
ACCOUNT_ID=$(wrangler whoami 2>&1 | grep -oE '[0-9a-f]{32}' | head -1)
DB_ID="[DATABASE_ID_FROM_ABOVE]"

curl -s -X PATCH "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/pages/projects/lander-[SLUG]" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"deployment_configs\": {
      \"production\": {\"d1_databases\": {\"DB\": {\"id\": \"${DB_ID}\"}}},
      \"preview\": {\"d1_databases\": {\"DB\": {\"id\": \"${DB_ID}\"}}}
    }
  }" | python3 -c "import sys,json; d=json.load(sys.stdin); print('D1 binding:', 'wired up' if d['success'] else 'FAILED', d.get('errors',''))"

# Redeploy after binding is set
wrangler pages deploy . --project-name lander-[SLUG]
```

Note the deployment URL from the output: `lander-[SLUG].pages.dev`

---

## Phase 7: Verify Split Test

Load `references/cloudflare-steps.md` → "Verifying the Split Test" and walk through:

1. Open `https://lander-[SLUG].pages.dev` in a fresh incognito window
2. DevTools (F12) → Network tab → reload → click the domain request → Cookies tab
3. Confirm `ab_variant=a` or `ab_variant=b` is present
4. Close the incognito window and open a fresh one. Confirm the variant alternates
5. Open `https://lander-[SLUG].pages.dev/a` and `/b`. Each always shows that variant (these are the preview links on the reports page)

Do not proceed until the split test cookie is confirmed working.

---

## Phase 8: SEO Meta + Favicon

Check what's already present in the lander:
```bash
grep -c 'noindex\|rel="icon"' /tmp/repo-[SLUG]/index-a.html
```

Verify these tags are in `<head>` of **all four files** — add if missing:
- `<meta name="robots" content="noindex, nofollow">`
- `<link rel="icon" href="/favicon.png">` (adjust extension as needed)

The four files are: `index-a.html`, `index-b.html`, `thank-you.html`, `reports.html`

**Update SEO title tags:**

Ask the user:
> "What is the primary service this lander is for? (e.g. 'HVAC Repair') And what city or region does it target? (e.g. 'Denver, CO')"

Update the `<title>` tag in all four files:
- `index-a.html` and `index-b.html`: `[Service] in [City] | [Business Name]`
- `thank-you.html`: `Thank You! | [Business Name]`
- `reports.html`: `Reports | [Business Name]` (if it has a placeholder title)

```bash
grep -h "<title>" /tmp/repo-[SLUG]/index-a.html /tmp/repo-[SLUG]/index-b.html /tmp/repo-[SLUG]/thank-you.html /tmp/repo-[SLUG]/reports.html
```

**For the favicon file**, ask the user:
> "Do you have a favicon file to add? Drag it into VS Code or give me the path.
>
> If you don't have one yet, use this Canva template — it takes about 2 minutes: https://canva.link/p1b06ycti45q64e
>
> Export as PNG, then drag it in. Or type 'skip' to add it later."

If provided:
```bash
cp /path/to/favicon.png /tmp/repo-[SLUG]/favicon.png
```

Update `README.md`: fill in the "Lander details" table (business, `.pages.dev` URL, date). **Never write the reports username, password, or token into README.md or any repo file.** The README lives in GitHub and every file in the folder is uploaded by `wrangler pages deploy .`. Check before committing:

```bash
grep -rniE "password|REPORTS_(PASS|TOKEN)\s*[:=|]" /tmp/repo-[SLUG] --include=*.md | grep -v "No passwords here" \
  && echo "STOP: credential text in a .md file, remove it" || echo "OK: no credentials in docs"
```

```bash
git add . && git commit -m "Add favicon, SEO titles, confirm noindex" && git push
wrangler pages deploy . --project-name lander-[SLUG]
```

Confirm internal files aren't public (the template's `_worker.js` returns 404 for them):
```bash
for f in README.md wrangler.toml schema.sql; do echo "$(curl -s -o /dev/null -w '%{http_code}' https://lander-[SLUG].pages.dev/$f) $f"; done   # all must be 404
```
If any return 200, the repo was made from an older copy of the template. Copy the "Internal files" block from the current `Leadgenpreneur-Team/laa-lander-template` `_worker.js` into this repo's `_worker.js` (just above the final `return env.ASSETS.fetch(request);`), commit, and redeploy.

---

## Phase 9: Tracking Scripts

Tell the user:
> "Time to add your tracking scripts. If you have any of the following, paste the code now:
> - Google Ads Global Site Tag (gtag)
> - Meta Pixel base code
> - Any other head-level tracking script
>
> These go in the `<head>` of all three lander pages. Type 'skip' if you don't have them yet."

Then ask:
> "Do you have a call tracking number swap script? This is a body-level script from a tool like CallRail or GHL that replaces the phone number on the page with a trackable one. Paste it here or type 'skip'."

Then ask:
> "Do you have a Google Ads conversion event tag for the thank-you page? Paste it here or type 'skip'."

**Meta Lead event — depends on `META_TRACKING` from intake:**

- **`full-capi`:** do NOT add a manual `fbq('track','Lead')` to the thank-you page. The worker already fires the Meta `Lead` event (browser + server, deduped) when the Pixel base code is present in `<head>`. A manual one would double-fire. Phase 9.5 handles the CAPI setup.
- **`pixel-only`:** the worker's CAPI won't fire (no access token), so add a client-side Lead event to `thank-you.html`. Inject this script in the `<!-- CONVERSION TRACKING -->` block:
  ```html
  <!-- Meta Pixel Lead Event (pixel-only — no CAPI) -->
  <script>
    if (typeof fbq === 'function') { fbq('track', 'Lead'); }
  </script>
  ```
  This requires the Meta Pixel base code in `<head>`. If the user didn't provide it above, ask for it now — the Lead event won't fire without it.
- **`none`:** skip all Meta tracking. No Pixel, no Lead event.

If provided, inject into the appropriate files:
- Head scripts (gtag, pixel base): place inside the `<!-- TRACKING SCRIPTS (HEAD) -->` comment block in `index-a.html`, `index-b.html`, and `thank-you.html`
- Call tracking swap script: place inside the `<!-- TRACKING SCRIPTS (BODY) -->` comment block in `index-a.html`, `index-b.html`, and `thank-you.html`
- Conversion events (Google Ads + pixel-only Meta Lead): place inside the `<!-- CONVERSION TRACKING -->` comment block in `thank-you.html` only

Commit and redeploy:
```bash
git add . && git commit -m "Add tracking scripts" && git push
wrangler pages deploy . --project-name lander-[SLUG]
```

---

## Phase 9.5: Meta Conversions API (optional)

**Skip this phase if `META_TRACKING` is `pixel-only` or `none`.** Move directly to Phase 10.

**Run this phase only if `META_TRACKING` is `full-capi`.**

The CAPI code is already built into `_worker.js` (form `Lead` + qualified-call `Contact`, deduped). Turning it on is config only — set the Meta secrets, build the GHL call-to-webhook workflow, and verify in Test Events.

Load `references/meta-capi.md` and follow it end to end. You'll need from the user: domain verified in Meta Business Suite, the dataset ID, the CAPI access token, and confirmation the ad set is optimizing for the `Lead` or `Contact` event.

Walk the GHL qualified-call workflow step-by-step using the instructions in `meta-capi.md` — don't just paste the doc at the user. Pre-fill the client's webhook URL (`https://[DOMAIN]/api/ghl-call`) and the `X-Webhook-Secret` value so they can't mistype them.

---

## Phase 10: Domain Purchase + Connection

**Subdomain vs. apex domain — determine this first:**

Ask the user whether the domain will be a subdomain (e.g. `quote.bobsplumbing.com`) or an apex domain (e.g. `bobsplumbing.com`).

- **Subdomain:** only one custom domain entry is needed — skip the www, canonical redirect, and Step 5 below. After Step 3, go straight to Step 4 (single domain polling), then skip to Phase 11.
- **Apex domain:** continue with all steps below.

**Step 1 — Domain purchase (manual):**

Load `references/cloudflare-steps.md` → "Purchasing and Connecting a Domain" and walk the user through registering the domain in the Cloudflare dashboard. Wait for confirmation before proceeding.

**Step 2 — Choose the canonical domain (apex only):**

> "Which URL do you want to use as the primary address for this lander — the bare domain (e.g. `bobsplumbing.com`) or the www version (e.g. `www.bobsplumbing.com`)? Pick one — we'll redirect the other to it. This matters for UTM tracking: a visitor who lands on one domain stores their UTM data there, so if GHL redirects to the other domain, that data is lost."

Most landers use the bare apex as canonical. Note the answer for Step 5.

**Step 3 — Add both custom domains (automated):**

```bash
CF_TOKEN=""
for f in ~/Library/Preferences/.wrangler/config/default.toml ~/.config/.wrangler/config/default.toml ~/.wrangler/config/default.toml "$APPDATA/xdg.config/.wrangler/config/default.toml"; do
  [ -f "$f" ] && CF_TOKEN=$(grep oauth_token "$f" | awk '{print $3}' | tr -d '"') && [ -n "$CF_TOKEN" ] && break
done
ACCOUNT_ID=$(wrangler whoami 2>&1 | grep -oE '[0-9a-f]{32}' | head -1)
DOMAIN="[DOMAIN]"

# Add apex domain
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/pages/projects/lander-${SLUG}/domains" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"${DOMAIN}\"}" | python3 -c "import sys,json; d=json.load(sys.stdin); print('Apex:', 'added' if d['success'] else 'FAILED', d.get('errors',''))"

# Add www domain
curl -s -X POST "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/pages/projects/lander-${SLUG}/domains" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"www.${DOMAIN}\"}" | python3 -c "import sys,json; d=json.load(sys.stdin); print('WWW:', 'added' if d['success'] else 'FAILED', d.get('errors',''))"
```

**Step 4 — Create DNS records + poll for Active (automated):**

```bash
# Get zone ID for the domain
ZONE_ID=$(curl -s "https://api.cloudflare.com/client/v4/zones?name=${DOMAIN}&account.id=${ACCOUNT_ID}" \
  -H "Authorization: Bearer ${CF_TOKEN}" | python3 -c "import sys,json; print(json.load(sys.stdin)['result'][0]['id'])")
echo "Zone ID: $ZONE_ID"

# Create apex CNAME (Cloudflare sometimes auto-creates this — safe to run regardless)
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"CNAME\",\"name\":\"${DOMAIN}\",\"content\":\"lander-${SLUG}.pages.dev\",\"proxied\":true}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('Apex DNS:', 'created' if d['success'] else d.get('errors',''))"

# Create www CNAME (almost never auto-created — always add manually)
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"CNAME\",\"name\":\"www\",\"content\":\"lander-${SLUG}.pages.dev\",\"proxied\":true}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('WWW DNS:', 'created' if d['success'] else d.get('errors',''))"
```

> If either DNS call returns a permission error (`zone:edit` scope missing on your token), fall back to manual: load `references/cloudflare-steps.md` → "Manual DNS Fallback" and walk the user through adding the records in the Cloudflare dashboard DNS tab.

Poll until both custom domains show Active — do not proceed until both pass:

```bash
for i in $(seq 1 20); do
  STATUSES=$(curl -s "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/pages/projects/lander-${SLUG}/domains" \
    -H "Authorization: Bearer ${CF_TOKEN}" \
    | python3 -c "
import sys, json
domains = json.load(sys.stdin)['result']
for d in domains:
    print(f\"{d['name']}: {d['status']}\")
")
  echo "$STATUSES"
  if echo "$STATUSES" | grep -q "pending\|initializing"; then
    echo "Waiting... (attempt $i/20)"
    sleep 15
  else
    echo "Both domains Active."
    break
  fi
done
```

If either domain stays Pending after 5 minutes: the most common cause is a missing DNS record. Check that both the apex CNAME and the www CNAME exist in the Cloudflare DNS tab for the domain.

**Step 5 — Add canonical redirect to `_worker.js` (apex only):**

Open `/tmp/repo-[SLUG]/_worker.js` and add this block at the very top of the `fetch` handler, before any existing routing:

```javascript
// Canonical redirect
const CANONICAL_HOST = '[CANONICAL_HOSTNAME]'; // e.g. 'bobsplumbing.com' or 'www.bobsplumbing.com'
const reqUrl = new URL(request.url);
if (reqUrl.hostname !== CANONICAL_HOST) {
  reqUrl.hostname = CANONICAL_HOST;
  return Response.redirect(reqUrl.toString(), 301);
}
```

Replace `[CANONICAL_HOSTNAME]` with the domain chosen in Step 2. Skip this step entirely for subdomains.

```bash
cd /tmp/repo-[SLUG]
git add _worker.js && git commit -m "Add canonical redirect to [CANONICAL_HOSTNAME]"
git push
wrangler pages deploy . --project-name lander-[SLUG]
```

After redeployment, confirm: visiting the non-canonical domain redirects (301) to the canonical with all URL parameters preserved.

Do not proceed to Phase 11 until all domains resolve correctly and the canonical redirect is verified.

---

## Phase 11: GHL Redirect + Full Testing

### Step 1 — Set GHL form redirect URL

Load `references/ghl-steps.md` → "Setting the Form Redirect URL".

Set the redirect to the custom domain URL (not the .pages.dev URL):
```
https://[DOMAIN]/thank-you?name={{contact.name}}&email={{contact.email}}&phone={{contact.phone}}
```

> ⚠️ **Do not drop the query string.** The `?name={{contact.name}}&email={{contact.email}}&phone={{contact.phone}}` part is required. These are GHL merge fields that pass the lead's info into the URL so the reports dashboard can capture the lead event. If the URL is saved without them, lead data will not be recorded.

Double-check the saved URL in GHL and confirm the full string is present before moving on.

### Step 2 — Full UTM test

Open this URL in a fresh incognito window (swap in the actual domain):
```
https://[DOMAIN]/?utm_source=google&utm_medium=cpc&utm_campaign=test-campaign&utm_content=test-ad&utm_term=local+service&gclid=test123&campaignid=111&adgroupid=222&keyword=local+service&matchtype=e&network=g
```

### Step 3 — Form submission test

Fill in a real name, email, and phone number and submit. The thank-you page URL should contain resolved values:
```
/thank-you?name=John+Smith&email=john@test.com&phone=9165551234
```
If you see the literal text `{{contact.name}}` in the URL, the redirect URL in GHL is missing the merge tags — stop and fix before continuing.

### Step 4 — Check reports

Visit `https://[DOMAIN]/reports` and log in. Confirm the lead row shows:
- Correct name, email, and phone (not blank)
- Correct variant (a or b)
- All UTM columns populated: utm_source, utm_medium, utm_campaign, utm_content, utm_term, gclid, campaign_id, ad_group_id, keyword, match_type, network

If any UTM columns are blank, the sessionStorage pass-through is broken — do not proceed.

### Step 5 — Call click test

Click a phone number link on the lander. Return to the reports page. Confirm a Call Click event appears with the correct variant.

Do not proceed to Phase 12 until all five steps pass.

---

## Phase 12: Wrap-Up

Print the following summary to the conversation and tell the user to save it in a password manager (or wherever they keep client logins). Don't save it to any file yourself:

```
--- LANDER DEPLOYMENT COMPLETE ---

Client:        [BUSINESS NAME]
Live URL:      https://[DOMAIN]
Reports page:  https://[DOMAIN]/reports
Reports login: [USERNAME] / [REPORTS_PASS generated in Phase 6]
Preview A / B: https://[DOMAIN]/a  and  https://[DOMAIN]/b
GitHub repo:   https://github.com/[USER_GITHUB_ORG]/lander-[SLUG]

Save the reports password now. It isn't stored anywhere else. (If it's ever lost, re-run `wrangler pages secret put REPORTS_PASS --project-name lander-[SLUG]` with a new one.)
---
```

Then run through this final checklist with the user before closing out:

```
FINAL CHECKS BEFORE GOING LIVE:

[ ] Reports page loads and you can log in
[ ] Lead row shows name, email, phone (not blank)
[ ] All UTM columns are populated (not blank)
[ ] Call click events are recording in reports
[ ] Split test cookie alternates between a and b (close and reopen incognito)
[ ] Favicon shows on all pages — lander, thank-you, and reports
[ ] Pages return noindex in source (right-click → View Source → search "noindex")
[ ] Phone numbers are formatted correctly and tap-to-call works
[ ] Thank-you page redirect URL has all GHL merge tags (name, email, phone)
[ ] GitHub repo is set to private
```

**Google Ads Sitelinks (offer this proactively):**

After printing the summary, offer:

> "Since this is a single-page lander, your Google Ads sitelinks need to use anchor links that jump to sections on the page (e.g. `https://[DOMAIN]/#reviews`). Want me to generate 4 sitelink URLs based on your page sections? I'll read the HTML and find the right anchors."

If they say yes, read `index-a.html` and identify 4 meaningful anchor targets (e.g. `#free-quote`, `#reviews`, `#how-it-works`, `#service-area`). If the sections don't have `id` attributes, add them to the HTML, commit, and redeploy, then output the sitelinks:

| Sitelink Label | URL |
|---|---|
| Get a Free Quote | `https://[DOMAIN]/#free-quote` |
| See Our Reviews | `https://[DOMAIN]/#reviews` |
| How It Works | `https://[DOMAIN]/#how-it-works` |
| Service Area | `https://[DOMAIN]/#service-area` |

Adjust labels and anchors to match the actual page content.
