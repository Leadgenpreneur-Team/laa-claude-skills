# Intake Questions

Ask these questions to collect everything needed before customizing templates. Group them naturally — don't read them as a dry list. Confirm all answers before moving to Phase 2.

---

## Available Niches + Template Labels

| Niche slug | Template folder | Page title label |
|---|---|---|
| `porta-potty` | `assets/templates/djm/porta-potty/` | "Porta Potty Rentals" |
| `dumpster-rental` | `assets/templates/djm/dumpster-rental/` | "Dumpster Rental" |
| `restroom-trailer` | `assets/templates/djm/restroom-trailer/` | "Restroom Trailer Rental" _(add when ready)_ |
| `septic` | `assets/templates/djm/septic/` | "Septic Services" _(add when ready)_ |

---

## Universal Questions (all niches)

1. **Business name** — exact legal/trade name as it should appear on the site (e.g. "Nature's Call Site Services")
2. **Client slug** — lowercase, hyphens only, no spaces. Used for the GitHub repo name and Cloudflare project. If the client has multiple services (e.g., porta potty AND dumpster rental), include the niche so the repos don't conflict: `pg-environmental-potty-lander`, `pg-environmental-dumpster-lander`. If it's their only service, keep it short: `natures-call`.
3. **Primary city and state** — the main market location shown in headline and title tag (e.g. "Atlanta, GA")
4. **Phone number** — just one number in any format (e.g. `(470) 494-2446` or `470-494-2446` or `4704942446`). The script will derive the digits-only version automatically.
5. **Service area** — list of counties or cities served. Any format is fine (newlines, commas, bullets) — the script normalizes it.
6. **Accent color** — the primary brand color used on all buttons, CTAs, and highlights throughout the page (e.g. `#D33B2C`). This is the conversion color — whatever draws the eye to "Get a Quote." If the client doesn't have a hex code, describe their brand colors and suggest one.
7. **Variant B test** — this can be decided now or deferred until after you approve Variant A. If you already know, give one sentence (e.g. "Variant B tests a headline that emphasizes same-day availability"). If not, skip and we'll come back to it before Phase 6.
8. **Domain name** — optional at this stage. If they have one, note it. If not, skip — we'll purchase and connect it in Phase 11. Suggest one now if helpful (e.g. `atlantaportapottyrentals.com`).
9. **Reports password** — team member chooses any password. Saved to ClickUp. Suggest a format like `[word][word][number]` (e.g. `greentruck42`, `dumpreports2026`, `bluebin99`).
10. **Tracking scripts** — do they have a Google Ads tag and/or Meta Pixel ready to add? (yes/no — can skip and add later)
11. **GHL sub-account** — which GHL sub-account has the quote form for this client? We need this in Phase 4 to grab the form embed code (`<iframe>` block) and inject it into the lander.

---

## Niche-Specific Questions

Only ask the section that matches the chosen niche. Answers feed directly into the product/unit cards in the template — collect them before Phase 2 so the script can reference them, or apply them as manual edits in Phase 3.

---

### Porta Potty

All porta potty companies are assumed to have standard units and handwash stations — don't ask about those. Only ask:

1. **Specialty units** — do they offer any of the following?
   - ADA / wheelchair accessible portable toilets
   - Luxury restroom trailers
   - Any other specialty units (high-rise, wedding unit, flushable unit, etc.)

2. **Same-day delivery?** — yes or no.

_Specialty unit answers add extra product cards in Phase 3. Standard units and handwash stations are always included by default._

---

### Dumpster Rental

1. **Sizes offered** — which of the following do they carry?
   - 7 yd
   - 10 yd
   - 15 yd
   - 20 yd
   - 25 yd
   - 30 yd
   - 40 yd

2. **Same-day delivery?** — yes or no.

_Size answers update the dumpster size cards in Phase 3._

---

### Restroom Trailer
- Trailer sizes/stall counts available?
- Events focus (weddings, corporate, festivals) or construction/long-term?
- ADA accessible unit available?

### Septic
- Services offered (pumping, inspection, installation, repair)?
- Residential, commercial, or both?

---

## Confirmation Checklist

Before starting Phase 2, confirm you have all of these:

- [ ] Business name (exact)
- [ ] Slug (lowercase, hyphens)
- [ ] Niche confirmed + template exists in assets/
- [ ] City and state
- [ ] Phone number (any format — script derives digits)
- [ ] Service area list (any format — script normalizes)
- [ ] Accent hex color
- [ ] Variant B description — or noted as TBD (needed before Phase 6)
- [ ] Domain name — or noted as TBD (needed at Phase 11)
- [ ] Reports password
- [ ] GHL sub-account name
