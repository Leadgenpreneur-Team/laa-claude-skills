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
| Bathroom Remodel | Free Estimate or Free In-Home Consultation | design consultation, remodel, installation, project, crew, warranty | We Review Your Request, Free In-Home Design Consultation, We Install Your New Bathroom | delivery, units, service call, technician |
| Dental | Free Consultation or New Patient Special (only as the practice offers it) | dentist, appointment, exam, cleaning, treatment, insurance | We Review Your Request, We Call to Schedule Your Visit, Your Appointment | quote, estimate, job, project, crew, technician, delivery |
| Rug Cleaning | Free Quote | pickup, cleaning, drying, return delivery, in-home cleaning | We Review Your Request, We Confirm Pickup or Your Cleaning Visit, Clean Rugs Back Home | assessment, project, crew, remodel, installation |
| Anything else | Whatever the business offers | The business's own words from its website | Review, Contact, Do the Work, in their words | Words from another service |

**Dental and law pages:** no promises about results ("pain-free", "guaranteed outcome", "best dentist in town"), prices only as the practice states them, and the doctor's or attorney's credentials only as the practice or firm lists them.

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

Reviews can come from **Google, Yelp, Angi (formerly Angie's List), HomeAdvisor (now part of Angi), and Facebook**. Use every platform the business actually has reviews on.

**Finding the profiles**
- Google first. Its phone, address, and website must match the business. If more than one listing could match, show the person the options (name, address, rating, count) and ask.
- Then search for the business on Yelp, Angi, HomeAdvisor, and Facebook, and ask the person in the same message: "Do they have reviews anywhere else, like Yelp, Angi, HomeAdvisor, or Facebook? Paste the links if so." Check each profile is the same business (name, city, phone) before using it.
- Review sites often block automated reading. If you can't read a profile, ask the person to paste the reviews plus that platform's current rating and count. Their paste counts as the source. Never write, edit, or "clean up" a review beyond fixing obvious line breaks.

**Rating lines**
- Each platform's rating is stated separately, with its exact count and a plus sign. Never average or add ratings across platforms, and never round.
- Lead with the platform that has the most reviews (usually Google): "4.9 From 318+ Google Reviews". Fill both rating slots (hero trust row and above the review cards) with that one.
- If a second platform is strong (4.5 or higher with 20+ reviews), add it as its own short line or badge under the first, e.g. "4.8 on Yelp (52+ Reviews)" or "Angi Super Service Award" (awards only if the profile shows them, with the year).
- Leave off any platform with a weak rating or only a handful of reviews.

**Choosing the six cards**
- Six reviews, quoted word for word. The LAA templates ship with three static cards. Fill those and add three more using the exact same card markup so there are six. Delete any review widget slot (we don't use review widgets). Five-star first, then the longest and most specific. Prefer reviews about this page's service.
- Mix platforms when they have good reviews, but keep Google as at least half unless the business barely uses Google.
- Skip one-liners, reviews with no text, anything mentioning a competitor or reading like spam, and reviews older than about three years when newer ones exist.
- Names: first name plus last initial ("John S."). Business names stay as written. If a platform only shows a first name or initials, use what it shows.
- If you have to use a review about another service, flag it in the report.

**Source marks on each card**
- Every card shows where that review really came from. Never guess, and never label a review with a platform it didn't come from.
- If the template already has a mark for that platform (e.g. the Google or Yelp icon), use it and delete the unused ones.
- If it doesn't (Angi, HomeAdvisor, Facebook), use a plain text label in the same spot styled like the template's small text: "Review on Angi", "Review on HomeAdvisor", "Review on Facebook". Don't draw or download another company's logo.

**Record it.** In `lander-notes.md`, list each platform used: profile link, rating, count, date read, and whether you read it or the person pasted it. edit-lander-laa uses this when the numbers are refreshed later.

## Thank-you page

- Title tag, meta description, and hero copy for this service.
- What Happens Next: three cards from the service table.
- Contact section background: a near-black shade of the accent. Mix the accent hex about 12 to 15% with `#0a0a0a`, hardcode it as `--accent-night` (don't rely on `color-mix()`), set `.contact { background: var(--accent-night); }`, and switch that section's heading, paragraph, list text, and check icons to light colors at 4.5:1 or better. The "Call Us Direct" card stays light with dark text.
- Don't reuse the lander's hero photo.

## Images

- Real photos first. Name files descriptively (`septic-truck-athens.jpg`), put them in `assets/`, reference them as `assets/filename.jpg`.
- Hero photos sit under a dark overlay. If text over a bright photo drops below 4.5:1, raise the overlay and note the change.
- Big photos: keep them under about 500 KB each (resize to 1600px wide) so the page loads fast on phones.
