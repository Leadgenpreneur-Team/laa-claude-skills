# How to Use: deploy-lander-laa

## What This Skill Does

Deploys a client landing page end-to-end — from finished HTML files to a live custom domain with split testing, lead tracking, and a reports dashboard. You build the lander in claude.ai/design first, then run this skill to handle everything else.

## Quick Start

Trigger the skill by saying any of:
- "Deploy a lander for [client name]"
- "Set up a landing page for [client]"
- "Launch a new client lander"
- `/deploy-lander-laa`

Claude will ask for the intake details, then walk you through each phase.

---

## What You'll Need Before Starting

| Item | Where to Get It |
|------|-----------------|
| Variant A HTML file | Built in claude.ai/design |
| Variant B HTML file | Built in claude.ai/design — one change from Variant A |
| Thank-you page HTML | Built in claude.ai/design |
| A folder containing all three files | Put them in one folder on your computer — you don't need to rename them |
| Client business name | From the client |
| Phone number | From the client |
| Variant A description | What does Variant A show? e.g. "Headline: Get a Free Quote Today" |
| Variant B test idea | What one thing does Variant B test? e.g. different headline, hero image |
| GHL sub-account access | GHL > Agency > Sub-accounts |
| Meta tracking level | Full CAPI / Pixel-only / No Meta (see Phase 1 for the question to ask) |
| Favicon file | Client brand kit, or make one with the Canva link in Phase 8 |
| Domain name | Can be TBD — only needed at Phase 10 |
| Reports dashboard password | You choose — format like `greentruck42` |
| Agency logo URL (optional) | Hosted URL to your agency logo — appears in the reports dashboard |

---

## How a Deployment Flows

```
Phase 1:   Intake — Claude collects all info; you put your HTML files in a folder
Phase 2:   Prep files — Claude identifies and copies files, checks bundler, call tracking, assets
Phase 3:   Confirm variants — You confirm the file mapping before Claude proceeds
Phase 4:   GHL form — Claude verifies or injects the form embed in both variants
Phase 5:   GitHub repo — Claude creates a private repo from the LAA template
Phase 6:   Cloudflare — Claude creates Pages project + D1 database + sets secrets + deploys
Phase 7:   Verify split test — Cookie check on the .pages.dev URL
Phase 8:   SEO + Favicon — Claude updates title tags; you provide the favicon
Phase 9:   Tracking scripts — Google Ads tag, Meta Pixel (if applicable)
Phase 9.5: Meta CAPI (optional) — Server-side Meta conversion tracking (full-capi only)
Phase 10:  Domain — Claude automates custom domain add, DNS records, and Active polling
Phase 11:  GHL redirect + testing — Set redirect URL, full end-to-end UTM and lead test
Phase 12:  Wrap-up — Credential summary + optional Google Ads sitelinks
```

---

## Your Job vs. Claude's Job

**Claude does:**
- Identifies your HTML files by filename and confirms the mapping
- Strips the Claude Design bundler wrapper if present
- Adds `data-tel-link` to all phone links
- Creates the GitHub repo from the LAA template
- Creates the Cloudflare Pages project, D1 database, and sets all secrets
- Deploys the site and verifies the split test cookie
- Updates SEO title tags
- Injects tracking scripts
- Automates domain setup, DNS records, and polling for Active status
- Adds a canonical redirect to the worker for UTM safety

**You do:**
- Build your lander files in claude.ai/design and put them in a folder
- Confirm the file mapping before Claude copies them
- Copy the GHL form embed code and paste it if it's missing (Phase 4)
- Provide the favicon file (Phase 8)
- Paste tracking scripts (Phase 9) — or skip
- Handle CAPI setup in GHL if doing full server-side tracking (Phase 9.5)
- Set the GHL form redirect URL (Phase 11)
- Confirm each phase before Claude moves forward

---

## Meta Tracking Options

Claude asks about this at intake. Three paths:

**Full CAPI** — You have a Meta Pixel AND a Conversions API access token for this client. Claude sets up the pixel base code in Phase 9, then walks you through the CAPI secrets and GHL call webhook in Phase 9.5. Server-side Lead + Contact events, deduped. Best for clients running active Meta campaigns where you want reliable conversion data.

**Pixel-only** — You have the Meta Pixel but no CAPI access token. Claude adds the pixel base code in Phase 9 and a client-side `fbq('track','Lead')` event on the thank-you page. Solid baseline tracking. Skip Phase 9.5.

**No Meta** — This client isn't running Meta ads. Skip all Meta tracking. Claude only adds Google Ads and call tracking if you provide them in Phase 9.

---

## GHL Form Redirect URL Format

When Claude tells you to set the redirect URL in GHL (Phase 11), always use this exact format — do not remove the query string:

```
https://[domain]/thank-you?name={{contact.name}}&email={{contact.email}}&phone={{contact.phone}}
```

The `{{contact.name}}`, `{{contact.email}}`, and `{{contact.phone}}` are GHL merge fields that pass the lead's info to the thank-you page so it shows up in the reports dashboard.

---

## Testing After Phase 11

After setting the GHL redirect URL, Claude will give you a test URL. Open it in an **incognito window**, fill out the form, and submit. Then check `/reports` to confirm:
- Lead shows up with the correct name, email, and phone
- All UTM columns are populated
- Variant is correct (a or b)

**Always use incognito** — your regular browser already has a tracking cookie, which prevents the pageview from logging.

---

## Reports Dashboard

After deployment, the reports dashboard lives at:
```
https://[domain]/reports
```

Login: the username and password you chose during intake.

The dashboard shows:
- Pageviews by variant (A vs. B)
- Leads with name, email, phone, and all UTM parameters
- Call click events
- Conversion rate by variant
- Round history (updated when you run `/new-split-test-laa`)

---

## Troubleshooting

| Problem | What to Check |
|---------|---------------|
| Form submits but no lead in reports | GHL redirect URL is missing the query string — re-set it with `?name={{contact.name}}&email=...` |
| Lead shows up but UTM columns are blank | Make sure you used the test URL with UTM params; test in incognito |
| Call clicks not showing in reports | The `data-tel-link` attribute should be on all `tel:` links — Phase 2 adds this automatically |
| Pageview not recording on repeat visits | Normal — pageviews only log on first visit (new cookie). Use incognito to test. |
| Split test cookie not present | Check DevTools > Application > Cookies after a fresh incognito visit |
| Domain stuck on Pending | A DNS record is probably missing — check both the apex CNAME and www CNAME in the Cloudflare DNS tab |
| Reports page shows "DB not configured" | The D1 binding wasn't wired up via API — re-run the `curl PATCH` command in Phase 6 |
