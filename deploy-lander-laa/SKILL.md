---
name: deploy-lander-laa
description: "Deploys a client landing page end-to-end for agency owners. Starts from a finished HTML file built in claude.ai/design. Handles GitHub repo creation, Cloudflare Pages + D1 + env vars, GHL form injection, split-test setup, tracking scripts, SEO/favicon, and domain connection. Triggers: deploy lander, deploy my lander, set up landing page, launch client lander, deploy lander for client, /deploy-lander-laa, /deploy-lander."
version: 3.3.0
---

# deploy-lander-laa

Deployment engine for client landing pages. The user builds their lander in Claude Design first — this skill handles everything after that: GitHub, Cloudflare, GHL form, split testing, tracking, and domain connection.

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

**DNS changes must use the Cloudflare dashboard.** The wrangler OAuth token has zone:read scope only — it cannot create or modify DNS records via API. Any DNS record additions or changes must be done in the Cloudflare dashboard directly.

You also need access to the client's GHL sub-account before Phase 4.

---

## Phase 1: Intake

Ask these questions up front. All are required except domain (can be TBD) and tracking scripts (can be deferred to Phase 9).

| Field | Notes |
|---|---|
| GitHub username or org | Where client repos will be created. Your GitHub username appears in your profile URL: `github.com/[username]`. If using an org, use the org name shown at `github.com/orgs/[orgname]`. When unsure, use your personal username. |
| index-a.html | Path to Variant A — the finished lander built in Claude Design |
| index-b.html | Path to Variant B — built in Claude Design before running the skill. Both variants are required. |
| Thank-you page | Path to `thank-you.html` — required. If they don't have one, stop and send them back to M1.4 to download it. |
| Client slug | Lowercase, hyphens only. Used for the GitHub repo name and Cloudflare project. If the client has multiple services or campaigns, differentiate by service to avoid naming conflicts — e.g. `smith-landscaping` and `smith-sprinkler-repair` for the same client. If it's their only service, keep it short: `smith-hvac`. |
| Business name | Exact name as it should appear on the page — shown in the reports dashboard header |
| Phone number | Any format — used to verify call tracking attributes are present |
| Variant A description | Briefly describe what Variant A shows — e.g. "Original layout — hero + form above fold" or "Headline: Get a Free Quote Today". This label appears in the reports dashboard for Round 1. |
| Variant B description | Briefly describe what Variant B tests vs Variant A. This label appears in the reports dashboard. Common split test types: image change, headline change, layout change, form on page instead of popup, different button color, different CTA text, hero section reorder. |
| Reports username | Username to log in to the reports dashboard. Suggest keeping it simple: `admin` or their first name. |
| Reports password | User chooses any password. Suggest a `word+word+number` format (e.g. `greentruck42`). No dashes or plus signs — these are hard to distinguish when typing in the login form. There is no recovery option — they must save this. |
| Domain name | Optional at this stage. Note it if they have one, skip if not — needed at Phase 10. |
| Agency logo URL | Optional. A hosted URL to your agency logo (PNG or SVG). This appears in the header of the client-facing reports dashboard. Leave blank if you don't want agency branding on the reports page. |

Confirm all fields before moving to Phase 2.

---

## Phase 2: Prep Working Files

### Step 1 — Copy lander to working folder

```bash
SLUG="[client-slug]"
WORK_DIR="/tmp/lander-$SLUG"
mkdir -p "$WORK_DIR"
cp "[PATH_TO_INDEX_A]" "$WORK_DIR/index-a.html"
cp "[PATH_TO_INDEX_B]" "$WORK_DIR/index-b.html"
cp "[PATH_TO_THANK_YOU]" "$WORK_DIR/thank-you.html"
```

If they do not have a thank-you page, stop here:
> "You need a thank-you page before we can continue. Go back to M1.4, download the thank-you template, and come back once you have it."

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
    template = template.split(uuid).join(`/assets/${filename}`);
  });
  fs.writeFileSync(inputPath, template, 'utf8');
  console.log('Stripped:', inputPath, '— extracted', Object.keys(manifest).length, 'assets');
}

// Run on whichever files had bundler matches
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

After bundler stripping, images and fonts are saved to `assets/` with UUID filenames. However, Claude Design sometimes references additional files by plain name (e.g. `src="logo.jpg"`) or as CSS `url()` values inside `<style>` blocks (e.g. `background-image: url('hero-clearing.jpg')`). Both will silently break on the live site.

```python
python3 - <<'PYEOF'
import re, os

work_dir = '/tmp/lander-[SLUG]'
missing = []

for fname in ['index-a.html', 'index-b.html', 'thank-you.html']:
    path = os.path.join(work_dir, fname)
    if not os.path.exists(path):
        continue
    with open(path) as f:
        html = f.read()

    # HTML src attributes
    for m in re.finditer(r'src="([^"]*\.(jpg|jpeg|png|svg|webp|gif))"', html, re.IGNORECASE):
        ref = m.group(1)
        if not (ref.startswith('/assets/') or ref.startswith('http') or ref.startswith('data:')):
            missing.append(f'{fname}: src="{ref}"')

    # CSS url() references (background images in <style> blocks)
    for m in re.finditer(r"url\(['\"]?([^)'\"]*\.(jpg|jpeg|png|svg|webp|gif))['\"]?\)", html, re.IGNORECASE):
        ref = m.group(1)
        if not (ref.startswith('/assets/') or ref.startswith('http') or ref.startswith('data:')):
            missing.append(f'{fname}: url({ref})')

if missing:
    for item in missing:
        print(f'MISSING: {item}')
else:
    print('No missing assets detected.')
PYEOF
```

If any missing assets are reported, tell the user:

> "Your page references [filename] but it wasn't included in your folder. Please provide that file before we continue."

**Spot-check for leftover template placeholders:**

```bash
grep -iEc "Your .* Co\.|City, ST|123-456-7890|1234567890|logo-ph|your company" "$WORK_DIR/index-a.html" || true
grep -iEc "Your .* Co\.|City, ST|123-456-7890|1234567890|logo-ph|your company" "$WORK_DIR/index-b.html" || true
```

If any are found, tell the user to fix them in Claude Design before continuing.

---

## Phase 3: Confirm Variants

Tell the user:
> "I have both variants ready in the working folder:
> - `index-a.html` — Variant A
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

# Clone to a separate path — avoids conflict with the WORK_DIR already at /tmp/lander-$SLUG
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
# Replace placeholders with the descriptions collected in Phase 1 intake
wrangler d1 execute lander-[SLUG]-db \
  --command "INSERT INTO rounds (round_number, variant_a_label, variant_b_label) VALUES (1, '[VARIANT_A_DESCRIPTION]', '[VARIANT_B_DESCRIPTION]')" \
  --remote
```

Generate a random token for the reports API (user never needs to see this):
```bash
REPORTS_TOKEN=$(openssl rand -hex 16)
echo "Reports token: $REPORTS_TOKEN"
```

Set all secrets (enter the value when prompted after each command):
```bash
# Reports dashboard auth
wrangler pages secret put REPORTS_USER --project-name lander-[SLUG]
# → enter the reports username from intake

wrangler pages secret put REPORTS_PASS --project-name lander-[SLUG]
# → enter the reports password from intake

wrangler pages secret put REPORTS_TOKEN --project-name lander-[SLUG]
# → enter the generated token from above

# Dashboard display values
wrangler pages secret put PROJECT_NAME --project-name lander-[SLUG]
# → enter the business name from intake

wrangler pages secret put PROJECT_SLUG --project-name lander-[SLUG]
# → enter the client slug

# Variant preview URLs (variant labels now come from the rounds table, seeded above)
wrangler pages secret put VARIANT_A_URL --project-name lander-[SLUG]
# → enter: /?ab_variant=a

wrangler pages secret put VARIANT_B_URL --project-name lander-[SLUG]
# → enter: /b
```

```bash
# Commit wrangler.toml and deploy
git add wrangler.toml && git commit -m "Add wrangler.toml with D1 binding"
git push
wrangler pages deploy . --project-name lander-[SLUG]
```

**Wire up the D1 binding via Cloudflare API** — `wrangler.toml` alone does NOT connect the database to the Pages project. This API call is required or the reports page will show "DB not configured":

```bash
CF_TOKEN=$(cat ~/Library/Preferences/.wrangler/config/default.toml 2>/dev/null | grep oauth_token | awk '{print $3}' | tr -d '"')
if [ -z "$CF_TOKEN" ]; then
  CF_TOKEN=$(cat ~/.wrangler/config/default.toml 2>/dev/null | grep oauth_token | awk '{print $3}' | tr -d '"')
fi
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
4. Close the incognito window and open a fresh one — confirm the variant alternates

Do not proceed until the split test cookie is confirmed working.

---

## Phase 8: SEO Meta + Favicon

Check what's already present in the lander:
```bash
grep -c 'noindex\|rel="icon"' index-a.html
```

Verify these tags are in `<head>` of **all four files** — add if missing:
- `<meta name="robots" content="noindex, nofollow">`
- `<link rel="icon" href="/favicon.png">` (adjust extension as needed)

The four files are: `index-a.html`, `index-b.html`, `thank-you.html`, `reports.html`

For the favicon file — ask the user to provide it:
> "Do you have a favicon file to add? Drag it into VS Code or give me the path.
>
> If you don't have one yet, use this Canva template to make one quickly — it takes about 2 minutes: https://canva.link/p1b06ycti45q64e
>
> Export it as PNG, then drag it in. Or type 'skip' to add it later."

If provided:
```bash
cp /path/to/favicon.png lander-[SLUG]/favicon.png
```

Update `README.md` — add the `.pages.dev` URL at the top under the project name.

```bash
git add . && git commit -m "Add favicon, confirm noindex" && git push
wrangler pages deploy . --project-name lander-[SLUG]
```

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
> "Do you have a Google Ads conversion event tag or Meta Lead event code? These fire on the thank-you page only. Paste them here or type 'skip'."

If provided, inject into the appropriate files:
- Head scripts (gtag, pixel base): place inside the `<!-- TRACKING SCRIPTS (HEAD) -->` comment block in `index-a.html`, `index-b.html`, and `thank-you.html`
- Call tracking swap script: place inside the `<!-- TRACKING SCRIPTS (BODY) -->` comment block in `index-a.html`, `index-b.html`, and `thank-you.html`
- Conversion events: place inside the `<!-- CONVERSION TRACKING -->` comment block in `thank-you.html` only

Commit and redeploy:
```bash
git add . && git commit -m "Add tracking scripts" && git push
wrangler pages deploy . --project-name lander-[SLUG]
```

---

## Phase 10: Domain Purchase + Connection

Load `references/cloudflare-steps.md` → "Purchasing and Connecting a Domain" and walk the user through the Cloudflare dashboard steps.

**Before connecting the domain, establish the canonical URL.** Ask:

> "Which URL do you want to use as the single canonical address for this lander — the apex domain (e.g. `bobsplumbing.com`) or the www subdomain (e.g. `www.bobsplumbing.com`)? Pick one — we'll set that as the primary and redirect the other to it."

The canonical URL is the one you'll set as the GHL form redirect URL in Phase 11. Using both without a redirect breaks UTM pass-through: a visitor lands on one domain, sessionStorage stores the UTMs there, but GHL redirects to the other domain where sessionStorage is empty.

**Step 1 — Add both custom domains in Cloudflare Pages:**

In Cloudflare Pages > lander-[SLUG] > Custom Domains, add both:
1. The apex domain (e.g. `bobsplumbing.com`)
2. The `www` subdomain (e.g. `www.bobsplumbing.com`)

If the domain is a **subdomain** (e.g. `quote.bobsplumbing.com`), only one custom domain entry is needed — skip the `www` entry and the redirect steps below.

**Step 2 — Add the missing DNS record manually:**

> **Important:** The wrangler OAuth token only has `zone:read` scope — it cannot create DNS records. All DNS changes must be made in the Cloudflare dashboard.

In the Cloudflare DNS tab for the domain, confirm both records exist (add manually if missing):
- Apex → CNAME or A record pointing to `lander-[SLUG].pages.dev` (Cloudflare may auto-create this when you add the apex as a custom domain)
- `www` → CNAME pointing to `lander-[SLUG].pages.dev` (this is typically NOT auto-created — add it manually)

Do not proceed to Step 3 until both domains resolve the lander.

**Step 3 — Add canonical redirect to `_worker.js`:**

This prevents UTM tracking loss when a visitor arrives on the non-canonical domain. Open `/tmp/repo-[SLUG]/_worker.js` and add this block at the very top of the `fetch` handler, before any existing routing:

```javascript
// Canonical redirect
const CANONICAL_HOST = '[CANONICAL_HOSTNAME]'; // e.g. 'bobsplumbing.com' or 'www.bobsplumbing.com'
const reqUrl = new URL(request.url);
if (reqUrl.hostname !== CANONICAL_HOST) {
  reqUrl.hostname = CANONICAL_HOST;
  return Response.redirect(reqUrl.toString(), 301);
}
```

Replace `[CANONICAL_HOSTNAME]` with whichever domain was chosen above. Skip this step entirely for subdomains.

```bash
cd /tmp/repo-[SLUG]
git add _worker.js && git commit -m "Add canonical redirect to [CANONICAL_HOSTNAME]"
git push
wrangler pages deploy . --project-name lander-[SLUG]
```

After redeployment, confirm: visiting the non-canonical domain redirects (301) to the canonical with all URL parameters preserved.

Do not proceed to Phase 11 until all domains resolve correctly and the canonical redirect (if applicable) is verified.

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

Print the following summary to the conversation and tell the user to save it somewhere they won't lose it (notes app, password manager, ClickUp task, etc.):

```
--- LANDER DEPLOYMENT COMPLETE ---

Client:        [BUSINESS NAME]
Live URL:      https://[DOMAIN]
Reports page:  https://[DOMAIN]/reports
Reports login: [USERNAME] / [PASSWORD]
GitHub repo:   https://github.com/[USER_GITHUB_ORG]/lander-[SLUG]

Save the reports password — there is no recovery option.
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
