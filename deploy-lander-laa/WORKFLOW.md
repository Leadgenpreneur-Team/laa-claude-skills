# How to Use: deploy-lander-laa

## What This Skill Does

Deploys a client landing page end-to-end for agency owners — from a finished HTML file to a live URL with split testing, lead tracking, and a reports dashboard. You build the lander first in claude.ai/design, then run this skill to handle everything else.

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
| Finished lander HTML file | Downloaded from claude.ai/design |
| Thank-you page HTML (optional) | Downloaded from claude.ai/design, or the skill generates one |
| Client business name | From onboarding or the client |
| Phone number | From the client |
| Variant B test idea | What single element to test (headline, button color, etc.) |
| GHL sub-account access | GHL > Agency > Sub-accounts |
| GHL form embed code | GHL > Client sub-account > Sites > Forms (may already be in your HTML) |
| Favicon file | Client brand kit, or make one with the Canva link provided in Phase 10 |
| Domain name | Purchased in Cloudflare (skill walks you through it in Phase 11) |
| Reports dashboard password | You choose — format like `greentruck42` |
| Agency logo URL (optional) | Hosted URL to your agency logo — appears in the reports dashboard header |

---

## How a Deployment Flows

```
Phase 1:  Intake — Claude collects all client info
Phase 2:  Prep files — Copy HTML, verify call tracking, check for GHL form
Phase 3:  Variant B — Claude creates the B variant with one change
Phase 4:  GHL form — Confirm or inject the form embed
Phase 5:  GitHub repo — Claude creates a private repo from the LAA template
Phase 6:  Cloudflare — Claude creates Pages project + D1 database + deploys
Phase 7:  Verify — Split test cookie, form submit, call button tracking
Phase 8:  GHL redirect (temp) — You set the .pages.dev redirect URL in GHL
Phase 9:  Tracking scripts — Google Ads tag, Meta Pixel (optional)
Phase 10: SEO + Favicon — You provide the favicon file
Phase 11: Domain — Claude walks you through purchasing + connecting in Cloudflare
Phase 12: Wrap-up — Claude prints a credential summary for you to save
```

---

## Your Job vs. Claude's Job

**Claude does:**
- Copies and preps your HTML files
- Creates the GitHub repo from the LAA template
- Creates the Cloudflare Pages project, D1 database, and sets all secrets
- Deploys the site
- Verifies everything works

**You do:**
- Build the lander in claude.ai/design before running the skill
- Copy the GHL form embed code and paste it if needed (Phase 4)
- Set the GHL form redirect URL (Phase 8 and Phase 11)
- Provide the favicon and any tracking scripts
- Confirm each phase before Claude moves forward

---

## GHL Form Redirect URL Format

When Claude tells you to set the redirect URL in GHL, always use this exact format — do not remove the query string:

**Temp (.pages.dev):**
```
https://lander-[slug].pages.dev/thank-you?name={{contact.name}}&email={{contact.email}}&phone={{contact.phone}}
```

**Final (custom domain):**
```
https://[domain]/thank-you?name={{contact.name}}&email={{contact.email}}&phone={{contact.phone}}
```

The `{{contact.name}}`, `{{contact.email}}`, and `{{contact.phone}}` are GHL merge fields that pass the lead's info to the thank-you page so it shows up in the reports dashboard.

---

## Testing After Phase 8

After setting the GHL redirect URL, Claude will give you a test URL. Open it in an **incognito window**, fill out the form, and submit. Then check `/reports` to confirm:
- Lead shows up with the correct name, email, and phone
- All UTM columns are populated
- Variant is correct (a or b)

**Always use incognito** — your regular browser already has a tracking cookie set from previous visits, which prevents the pageview from logging.

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

---

## Troubleshooting

| Problem | What to Check |
|---------|---------------|
| Form submits but no lead in reports | GHL redirect URL is missing the query string — re-set it with `?name={{contact.name}}&email=...` |
| Lead shows up but UTM columns are blank | Make sure you used the test URL with UTM params; test in incognito |
| Call clicks not showing in reports | The `data-tel-link` attribute should be on all `tel:` links — the Phase 2 script adds this automatically |
| Pageview not recording on repeat visits | Normal — pageviews only log on first visit (new cookie). Use incognito to test. |
| Split test cookie not present | Check DevTools > Application > Cookies after a fresh incognito visit |
