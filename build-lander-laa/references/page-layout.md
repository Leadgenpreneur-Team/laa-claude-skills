# Standard layout (when there's no template)

A proven single-service local lander. Build it as one HTML file with a `<style>` block. Mobile first: design at 390px wide, then make sure it looks right at 1280px.

## Landing page (`index-a.html`), top to bottom

1. **Header:** logo left, phone button right (a `tel:` link styled as a button). Sticky is fine.
2. **Hero:**
   - Eyebrow: the service and city ("Septic Pumping in Athens, GA").
   - H1: the main promise for this service. **Three lines max** on phone and desktop.
   - Subhead: one or two sentences, what they get and why this business.
   - 3 or 4 short proof bullets (only sourced facts).
   - Two buttons: **Call** (`.btn .btn-call`, brightest accent color) and **Get [Offer]** (`.btn .btn-quote`, scrolls to the form).
   - Trust row: "★ 4.9 From 318+ Google Reviews" plus one or two real proof points.
   - The form sits in the hero on desktop (right column) and right below the hero on mobile.
3. **Form block:** `id="quote"`, a short heading ("Get Your Free Quote in 2 Minutes"), then the GHL form embed or the `<!-- GHL FORM EMBED -->` slot.
4. **Problems or reasons to call:** 3 to 6 cards, specific to this service.
5. **How it works:** 3 or 4 steps (wording from the service table in copy-rules.md).
6. **Reviews:** rating line plus six review cards (name, stars, text, Google mark).
7. **Why choose us:** 4 benefits, sourced only.
8. **Service area:** 10 to 14 towns weighted to the biggest ones, plus a map image if available.
9. **FAQ:** 4 to 6 questions answered only from sourced facts. Use `<details>` so it works without JavaScript.
10. **Final CTA band:** headline, call button, quote button.
11. **Footer:** business name, city, phone link, © year. No links away from the page.
12. **Sticky mobile call bar** (phones only): one full-width "Call Now" link, class `mobile-call-bar`.

Give the main sections `id`s (`quote`, `how-it-works`, `reviews`, `service-area`, `faq`) so Google Ads sitelinks can point at them later.

## Thank-you page (`thank-you.html`)

1. Header (same as the lander, phone button).
2. Hero: "Thanks! We Got Your Request." plus one line on what happens next, and a "Need It Sooner? Call [phone]" button (Family Law: "Need to Talk Sooner?").
3. **What Happens Next:** three cards. First card has an "In Progress" pill, the others "Next Step". Steps from the service table.
4. Contact section on a near-black shade of the accent (see copy-rules.md) with a light "Call Us Direct" card, three proof points, and hours.
5. Footer.

## Design basics

- Colors: the business's main brand color as `--accent` (for buttons, links, highlights only), a darker `--accent-deep` for hover, near-black text, white and light tints of the accent for alternating section backgrounds.
- Fonts: one Google Font for headings and one for body at most, or a system font stack.
- Buttons at least 48px tall, full width on phones.
- Body text at least 16px. Contrast 4.5:1 or better everywhere, including text over hero photos (use a dark overlay).
- Images: `object-fit: cover`, explicit `width`/`height` or `aspect-ratio`, `loading="lazy"` below the hero.
- No external JavaScript libraries. Small inline scripts are fine (smooth scroll, mobile menu).
- Add `<meta name="viewport" content="width=device-width, initial-scale=1">` and a real `<title>` and meta description.
