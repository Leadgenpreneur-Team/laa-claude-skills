# Meta Conversions API (CAPI)

Server-side conversion tracking for the lander. Fires `Lead` (form submit) and `Contact` (qualified phone call) events to Meta directly from `_worker.js`, alongside the client-side Pixel. CAPI survives iOS privacy restrictions, ad blockers, and Safari ITP that block client-side Pixel events — so Meta sees conversions the browser can't report.

**Optional per client.** If the Meta secrets below are not set, `_worker.js` silently skips every CAPI call and the lander deploys and runs exactly as before. Only run this setup for clients who want server-side Meta tracking.

**Meta-only — Google Ads untouched.** The worker owns the `Lead`/`Contact` events for Meta only. Google Ads conversions are handled by your gtag snippet in the `CONVERSION TRACKING` block and run independently. A Google-Ads-only client (no Pixel, no Meta secrets) triggers nothing in the worker.

---

## Architecture (already built into the template)

| Conversion | Path | Meta event | Match key |
|---|---|---|---|
| Form submit | GHL form → thank-you redirect → `/api/track-event` → worker | `Lead` | hashed email + phone + name, `_fbp`/`_fbc` cookies, IP, UA |
| Qualified call ≥30s | GHL workflow → Webhook → `/api/ghl-call` → worker | `Contact` | hashed phone (+ fbc from fbclid if present) |

- **Dedup:** the thank-you script generates one `event_id`, fires the browser Pixel `Lead` with it (`fbq('track','Lead',{},{eventID})`) **and** sends it to the server. Meta merges the browser + server events instead of double-counting. Because the worker handles the Pixel `Lead` automatically, **do not also paste a manual `fbq('track','Lead')` into the thank-you page** — that would double-fire.
- **`_fbp`/`_fbc`:** set as first-party cookies by the Pixel base code in `<head>`. The same-origin fetch to `/api/track-event` carries them in the Cookie header, so the worker reads them with no extra wiring.
- **Calls have no browser session,** so the `Contact` event matches on the caller's hashed phone number. Match quality is lower than a form — expected, not a bug.
- **Reports dashboard:** when CAPI fires a `Contact`, the worker also logs a `qualified_call` event to D1, surfaced as a **Qualified Calls** total on `/reports` (separate from tap-based "Call Clicks"). Non-CAPI landers never get these rows — their dashboard is unchanged.

---

## Per-client secrets

Set these on the client's Pages project. Set them only for a CAPI client.

> **Hand these to the user ONE COMMAND AT A TIME.** The cadence is: give one command → they run it → they reply when it shows `✨ Success! Uploaded secret` → give the next one. A block of commands causes people to skip steps. Claude can set the non-secret `META_DATASET_ID` itself; the user runs the secret ones at the hidden prompt.

The full list (deliver one at a time, with `lander-<slug>` filled in):

1. `wrangler pages secret put META_DATASET_ID --project-name lander-<slug>` — the Dataset ID (public; **Claude sets this one**).
2. `wrangler pages secret put META_CAPI_TOKEN --project-name lander-<slug>` — the CAPI access token (**secret** — user pastes at the hidden prompt, never in chat).
3. First run `openssl rand -hex 24` (copy the output), then `wrangler pages secret put GHL_WEBHOOK_SECRET --project-name lander-<slug>` — guards the call webhook. The user will also paste this value into the GHL webhook header later.
4. *(optional)* `wrangler pages secret put CALL_MIN_DURATION --project-name lander-<slug>` — call gate in seconds (default 30).
5. *(testing only — REMOVE before go-live)* `wrangler pages secret put META_TEST_EVENT_CODE --project-name lander-<slug>`.

After **each** secret command, the user runs the bare command, waits for `? Enter a secret value:`, then pastes the value — **never on the command line.** Confirm each succeeds before moving to the next.

Redeploy after setting secrets:
```bash
wrangler pages deploy . --project-name lander-$SLUG
```

---

## What the user does in Meta (one-time per client)

1. **Get the Dataset ID.** In Meta Events Manager → **your dataset → Settings** → look for **Dataset ID**. (Same value as the Pixel ID — it's public.)
2. **Verify the domain.** In Meta Business Settings → Brand Safety → **Domains** → add the root domain (covers subdomains), verify via DNS TXT or meta-tag. Required for iOS attribution. Step-by-step guide: https://scribehow.com/o/Ihy9pFzrTvmhJ3z1PHTsaQ/viewer/Verifying_Your_Domain_in_Meta_Business_Suite__Iep-oJntTHufYnAde0e_TQ
3. **One dataset, two sources.** The Pixel (browser) and CAPI (server) must use the **same dataset ID**. Don't create a second dataset.
4. **Generate the CAPI token.** Events Manager → **your dataset → Settings** → scroll to the **Conversions API** section → click **Generate access token**. Don't paste it in chat — set it via the hidden Cloudflare prompt.
5. **Point the ad at the event.** In Ads Manager → campaign objective **Leads** (or Sales) → ad set conversion location **Website** → performance goal = **Lead** (and/or **Contact** for calls). This is what makes conversions show as a *Result* in the campaign. If the ad optimizes for anything else, events land in the dataset but won't show as campaign results.

> Aggregated Event Measurement / "Configure Web Events" event ranking is no longer a manual step — Meta automated it in mid-2025. If the account still shows an AEM tab, rank `Lead` first; otherwise nothing to do.

---

## GHL qualified-call workflow (walk the user through this in GHL)

This fires the `Contact` event for connected calls. The 30-second gate lives in the worker, not GHL — GHL sends every completed call and the worker drops anything under `CALL_MIN_DURATION`.

> ⚠️ **Snapshots do NOT carry this over.** When a new client sub-account is created from a GHL snapshot, the **Call Status filter** and the **Webhook action** are wiped — even if the workflow itself exists. Rebuild the trigger filter and webhook from scratch for every client.

**Step 1 — Open the workflow.** In GHL: log into the **client's sub-account** → left sidebar **Automation** → **Workflows** → open the Facebook Ads phone call workflow (name varies). If it doesn't exist, create a workflow.

**Step 2 — Trigger (rebuild ALL three filters).** Trigger = the **Call Status** trigger. Add three filters:
1. **Number pool → is → [this client's correct pool]**
2. **Call direction → is → `incoming`** (don't count outbound calls from your team)
3. **Call status → is → `completed`** (drops voicemail, no-answer, busy, canceled)

All three are wiped by the snapshot — set every one of them, every time.

**Step 3 — Webhook action (rebuild it).** Add or open the **Webhook** action and fill it exactly:

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `https://[DOMAIN]/api/ghl-call` |

**Custom Data** — click "Add another item" for each (use the tag picker to insert `{{…}}` merge fields):

| Key | Value |
|---|---|
| `phone` | `{{contact.phone}}` |
| `call_duration` | `{{phoneCall.duration}}` — search "duration" in the picker, pick **Phone Call → Phone Call Duration** |
| `first_name` | `{{contact.first_name}}` |
| `last_name` | `{{contact.last_name}}` |

**Headers** — one row (plain text, not a merge field):

| Key | Value |
|---|---|
| `X-Webhook-Secret` | the `GHL_WEBHOOK_SECRET` value from the `openssl rand` command above |

**Step 4 — Turn on Re-Entry.** In the open workflow, click the **Settings** tab at the top → scroll to **Allow Re-Entry** → toggle ON → Save. Without it, any contact who's already been through the workflow gets "Skipped" and the webhook never fires. This also lets a repeat caller count each time.

**Step 5 — Publish** (toggle top-right).

**Common mistakes to flag:**
- Pasting a secret value on the command line instead of the hidden prompt (Cloudflare side).
- Forgetting the `X-Webhook-Secret` header → every call returns `401`.
- Re-entry left off → second test call shows "Skipped," webhook never fires.
- The lander's displayed number isn't the pool's swapping number → call tracking never activates → real calls bypass GHL → nothing fires. Confirm the lander's phone number matches the pool's "Add Swapping Numbers" value.

---

## Webhook payload reference

GHL nests the workflow's Custom Data under a `customData` object. The worker reads `customData` first and pulls `fbclid` straight from the attribution block — you do not need to map `fbclid` as custom data.

```jsonc
{
  "phone": "+19164065756",                 // top-level standard field (caller ID)
  "customData": {
    "phone": "(916) 406-5756",
    "call_duration": "81",                 // {{phoneCall.duration}} — required for the gate
    "first_name": "", "last_name": ""
  },
  "contact": { "attributionSource": { "fbclid": "..." } }   // worker reads fbclid here automatically
}
```

`call_duration` (gate) and `phone` (match key) are the two that matter.

---

## Verification (Meta Test Events)

1. Set `META_TEST_EVENT_CODE` to the code from Events Manager → dataset → **Test Events**, then redeploy.
2. **Form test:** submit a test lead on the lander → in Test Events, confirm a **browser** `Lead` and a **server** `Lead` arrive and **dedupe into one** (not two). Check Event Match Quality is "Good" or better.
3. **Call test:**
   - First, point the pool forwarding to **your own phone** (GHL → the number pool → forwarding number). This way the test call reaches you, not the client. Revert it when done.
   - Make sure the workflow's **re-entry is ON** — workflow **Settings** tab → **Allow Re-Entry** → ON.
   - Call the lander number, and **once it connects, stay on for at least 60 seconds** before hanging up. The duration counts from when the call connects — 60 seconds gives a safe buffer over the 30-second gate.
   - In the GHL webhook's **View details**, confirm the response is `"events_received":1`.
   - ⚠️ **The Contact will NOT appear in the Test Events feed** — `phone_call`-source server events don't render there. This is normal. Verify the call via `events_received:1`, not the feed. Tell the user this before they look, or they'll think it's broken.
4. **Remove `META_TEST_EVENT_CODE`** and redeploy before going live, or events keep flagging as test traffic.

Quick endpoint smoke test (returns `{"ok":true,...}` and sends nothing to Meta unless secrets are set):
```bash
curl -s -X POST "https://[DOMAIN]/api/ghl-call" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: [GHL_WEBHOOK_SECRET]" \
  -d '{"phone":"9165551234","call_duration":"45","first_name":"Test"}'
# 401 → secret mismatch
# skipped:below_min_duration → gate works
# capi.skipped:true → CAPI secrets not set yet
```
