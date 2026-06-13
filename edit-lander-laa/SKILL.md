---
name: edit-lander-laa
description: "Makes a targeted edit to a live client landing page without replacing the whole HTML file. Use for client-requested changes like updating a phone number, headline, button text, image, or any other small content update. Works on index-a.html, index-b.html, thank-you.html, or all three. Triggers: edit lander, update phone number, change headline, client wants a change, fix the lander, /edit-lander-laa, /edit-lander."
version: 1.1.0
---

# edit-lander-laa

Makes a targeted content edit to a live landing page — phone number, headline, button text, image, GHL form embed, or any other change a client requests. Does not replace entire HTML files. Pulls the GitHub repo, makes the edit, redeploys, and verifies.

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

## Phase 1: Intake

Collect all required fields before proceeding:

| Field | Notes |
|---|---|
| Live URL | The current live lander URL (e.g. `https://samueldeck.com`) |
| GitHub username or org | The same one used when the lander was deployed. Your GitHub username appears in your profile URL: `github.com/[username]`. |
| Which file(s) to edit | `index-a.html`, `index-b.html`, `thank-you.html`, or multiple |
| What needs to change | Be specific — old value and new value if possible (e.g. "phone number: 916-555-1234 → 916-888-9999") |

If they aren't sure which file to edit, ask:
> "Is this change on the main landing page, the thank-you page, or both? And should it go on both variants (A and B) or just one?"

Do not start Phase 2 until the change is clearly understood.

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
gh repo clone $GITHUB_ORG/lander-$SLUG /tmp/edit-$SLUG
```

Verify the files to be edited are present:
```bash
ls /tmp/edit-$SLUG/index-a.html /tmp/edit-$SLUG/index-b.html /tmp/edit-$SLUG/thank-you.html
```

---

## Phase 4: Make the Edit

**Before editing, scan all three files for the content being changed** — even if they only asked to update one file. Some content (phone numbers, addresses, business names) appears in multiple places. Report what you find:

> "I found that value in 3 places: `index-a.html`, `index-b.html`, and `thank-you.html`. Should I update all three?"

This prevents partial updates where one file gets the old value and another gets the new one.

Once the scope is confirmed, read the relevant file(s) and make the targeted change. Show a diff or summary of exactly what changed before committing:

> "Here's what I'm changing:
> - File: `index-a.html`, `index-b.html`, `thank-you.html`
> - Old: `<a href="tel:9165551234">916-555-1234</a>`
> - New: `<a href="tel:9168889999">916-888-9999</a>`
>
> Does that look right?"

Do not commit until confirmed.

**Common edit types:**

- **Phone number:** Update both the `href="tel:..."` attribute and the visible text. Also re-run the `data-tel-link` check — the new number link must have the attribute or call tracking will break:
  ```python
  python3 - <<'PYEOF'
  import re, os
  work_dir = '/tmp/edit-[SLUG]'
  for fname in ['index-a.html', 'index-b.html', 'thank-you.html']:
      path = os.path.join(work_dir, fname)
      if not os.path.exists(path): continue
      with open(path) as f: html = f.read()
      tel_links = re.findall(r'href="tel:[^"]*"', html)
      tel_with_attr = re.findall(r'href="tel:[^"]*"\s+data-tel-link', html)
      if len(tel_links) != len(tel_with_attr):
          html = re.sub(r'(href="tel:[^"]+")(?!\s+data-tel-link)', r'\1 data-tel-link', html)
          with open(path, 'w') as f: f.write(html)
          print(f'{fname}: added data-tel-link to {len(tel_links) - len(tel_with_attr)} phone link(s)')
      else:
          print(f'{fname}: data-tel-link already present on all {len(tel_links)} phone link(s)')
  PYEOF
  ```

- **Headline or body text:** Find the exact text, replace it, confirm the surrounding HTML context looks right.

- **Button text or CTA:** Find the `<a>` or `<button>` element and update the text only.

- **Hero image:** Update the `src` attribute. If it's a new image file, ask them to provide the path and copy it to `assets/`:
  ```bash
  cp "/path/to/new-image.jpg" /tmp/edit-$SLUG/assets/
  ```

- **GHL form embed:** Replace the existing `<iframe>` block and `<script>` tag with the new embed code. Verify it is present after the change:
  ```bash
  grep -c "leadconnectorhq.com" /tmp/edit-$SLUG/index-a.html
  grep -c "leadconnectorhq.com" /tmp/edit-$SLUG/index-b.html
  ```

---

## Phase 5: Commit, Push, and Redeploy

```bash
cd /tmp/edit-$SLUG
git add .
git commit -m "Edit: [brief description of change]"
git push
wrangler pages deploy . --project-name lander-$SLUG
```

After the deploy completes, tell them:

> "Deployed. Cloudflare's cache can take 1-2 minutes to clear — if you don't see the change right away, wait a moment and do a hard refresh (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)."

---

## Phase 6: Log to Audit Log

Write the change to the D1 audit log so it's visible in the reports dashboard:

```bash
wrangler d1 execute lander-$SLUG-db \
  --command "INSERT INTO audit_log (action, detail) VALUES ('note', '[brief description of what changed, e.g. Phone number updated: 916-555-1234 to 916-888-9999 — all three files]')" \
  --remote
```

---

## Phase 7: Verify

Ask them to confirm the change looks correct on the live site. They should check:
- The change appears correctly
- Nothing else looks broken (layout, form, links)

For phone number changes: confirm the `tel:` link dials the right number, not just the visible text.

---

## Phase 8: Wrap-Up

Confirm the change is live and verified. Note what was updated and when, for your own records.
