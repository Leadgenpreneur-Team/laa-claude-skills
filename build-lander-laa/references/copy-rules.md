# Copy rules

These are the rules our agency uses on every lander. Follow all of them.

## Facts

- **The template's words are not a source.** Every claim baked into a template (same-day delivery, licensed, insured, guaranteed, years in business, jobs completed, $0 service call, family owned, financing, 24/7, BBB or Angi ratings, association badges) is a placeholder. Delete it unless a source supports it. That includes the `<title>` and meta description.
- Sample text like "Your Dumpster Co.", "123-456-7890", "City, ST", "Same Day Delivery", "Lorem ipsum", anything in `[brackets]` is placeholder. None of it may survive.
- If a proof point has no source, delete it and use a real one instead (the Google rating is always available).
- If a section can't be filled from sources (FAQ question, "since [YEAR]", financing), delete that item. Don't make things up to fill space.
- Every headline, section, and proof point is about **this one service**, not the business in general.

## Headlines and wording

- Match the tone of the business's website: professional, local, trustworthy.
- Keep the template's structure and section order. Swap content only.
- **Title Case** for headlines, subheads, bullets, eyebrows, trust items, pills, and buttons. Short words stay lowercase (and, or, if, to, of, a, the, in, for, on).
- **No em dashes** anywhere on either page. Go easy on hyphens.
- Headlines use `text-wrap: balance`. The last line of any headline has at least four words; reword if not.
- **The hero H1 is three lines or fewer** at 390px and 1280px, on both pages. If it's longer, shorten the words. Don't shrink the font, change the CSS, or add `<br>` tags.
- One phone number and one CTA phrase, used the same way everywhere.
- The call button is the brightest accent color on the page.
- Add a few section backgrounds tinted from the accent color so the page doesn't look like one white wall.

## Wording by service

Templates get shared between services, so their words often belong to another one. Rewrite every button, step, pill, FAQ, and thank-you card to fit this service. Use the business's own terms where they differ.

| Service | Offer words | Process words | What Happens Next (thank-you) | Avoid |
|---|---|---|---|---|
| Dumpster | Free Quote, Book Your Dumpster | delivery, drop-off, fill, haul away, yard sizes | We Review Your Request, We Confirm Delivery, We Drop Off Your Dumpster | assessment, technician, estimate visit |
| Porta Potty | Free Quote, Reserve Units | delivery, setup, servicing, pickup, event or job site | We Review Your Request, We Confirm Units and Delivery, We Deliver and Set Up | assessment, technician, repair |
| Home Services (roofing, HVAC, remodeling, etc.) | Free Estimate | on-site assessment, itemized quote, project, crew | We Review Your Request, Free On-Site Assessment, We Get to Work | delivery, units |
| Septic | Free Estimate or Free Quote | pumping, inspection, repair, installation, tank, drain field, technician, service visit | We Review Your Request, We Schedule Your Service Visit, We Get the Job Done | delivery, units, remodel, project crew |
| Plumbing | Free Estimate (or their service-call offer) | plumber, technician, diagnose, upfront pricing, repair | We Review Your Request, A Plumber Contacts You, We Fix the Problem | delivery, units |
| Family Law | Free Consultation (only as the firm states it) | attorney, case, consultation, confidential, representation | We Review Your Inquiry, An Attorney Reaches Out, Your Consultation | quote, estimate, job, project, crew, service visit |
| Anything else | Whatever the business offers | The business's own words from its website | Review, Contact, Do the Work, in their words | Words from another service |

The thank-you hero button says "Need It Sooner? Call [phone]" for every service except Family Law, which says "Need to Talk Sooner? Call [phone]".

## Phone numbers

- The page's number is the one the person told you calls should ring. If the website shows a different number, use the person's and note the difference in `lander-notes.md`.
- **Every** phone number shown anywhere (hero, body, FAQ, footer, final CTA, mobile bar) is a clickable link: `<a href="tel:+1XXXXXXXXXX" data-tel-link>`. No plain-text numbers.
- Phone links that aren't buttons are accent colored and underlined. Add this as one block at the **end** of the page's `<style>` (use whatever the template calls its accent variable):
  ```css
  a[href^="tel:"]:not(.btn):not(.tel-plain) { color: var(--accent); text-decoration: underline; text-underline-offset: 2px; font-weight: 600; }
  a[href^="tel:"]:not(.btn):not(.tel-plain):hover { color: var(--accent-deep, var(--accent)); }
  ```
- On dark backgrounds, use a lighter tint of the accent so the link still reaches 4.5:1 contrast. It stays accent colored and underlined.
- Buttons (`.btn`, `.btn-call`, `.btn-quote`) and the mobile call bar keep their own styling.
- **Exceptions** get `class="tel-plain"`: the big number in the thank-you "Call Us Direct" card (keeps the template's dark ink color, add `text-decoration: none`) and every `.mobile-call-bar a`.

## Reviews

- Find the right Google Business Profile: its phone, address, and website must match the business. If more than one listing could match, show the person the options (name, address, rating, count) and ask.
- Use the **current** rating and review count from the live profile. If you can only reach a third-party copy, say so and give the date.
- Show the rating with a plus sign and the exact count, in both places on the page (hero trust row and above the review cards): "4.9 From 318+ Google Reviews" and "4.9 Average Rating From 318+ Google Reviews". Never round, never "hundreds of".
- Quote **six** reviews word for word. Five-star first, longest and most specific first. Skip one-liners, reviews with no text, anything mentioning a competitor or reading like spam.
- Names: first name plus last initial ("John S."). Business names stay as written.
- Prefer reviews about this service. If you have to use reviews about another service, flag it.
- Keep only the Google (or Yelp) mark that matches where each review really came from.
- If you can't reach the reviews at all, ask the person to paste six reviews plus the rating and count. Never write reviews yourself.
- Record the rating, count, source, and date in `lander-notes.md`.

## Thank-you page

- Title tag, meta description, and hero copy for this service.
- What Happens Next: three cards from the service table.
- Contact section background: a near-black shade of the accent. Mix the accent hex about 12 to 15% with `#0a0a0a`, hardcode it as `--accent-night` (don't rely on `color-mix()`), set `.contact { background: var(--accent-night); }`, and switch that section's heading, paragraph, list text, and check icons to light colors at 4.5:1 or better. The "Call Us Direct" card stays light with dark text.
- Don't reuse the lander's hero photo.

## Images

- Real photos first. Name files descriptively (`septic-truck-athens.jpg`), put them in `assets/`, reference them as `assets/filename.jpg`.
- Hero photos sit under a dark overlay. If text over a bright photo drops below 4.5:1, raise the overlay and note the change.
- Big photos: keep them under about 500 KB each (resize to 1600px wide) so the page loads fast on phones.
