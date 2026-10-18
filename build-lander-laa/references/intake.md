# Intake: the interview

The goal is to ask the fewest questions possible. Find what you can yourself (website, Google profile, photos on the site) and only ask for what's left. Ask in **one grouped message**, in plain language. No jargon (don't say "slug", "D1", "embed" without explaining it).

## Message 1: the basics

Ask these together:

> "Let's build your landing page. A few quick questions:
> 1. Is this page for **your own business** or for **a client**?
> 2. What's the **business name** and **website**?
> 3. What **one service** is this page selling? (One page per service works best, e.g. 'septic pumping', not 'all our services'.)
> 4. What **city or area** do they serve?
> 5. Do you have anything already written down about the business, like kickoff call notes, an onboarding survey, or an old landing page? Totally fine if not."

## Research, then message 2: only what's missing

After Phase 3 research, ask only for what you still don't know. Typical items:

| Item | How to ask | Default if they don't know |
|---|---|---|
| Phone number for calls | "What number should calls from this page ring? If you'll use a call tracking number, give me that one." | The number on the website, flagged |
| Offer | Propose one: "Free Quote" (rentals), "Free Estimate" (home services), "Free Consultation" (law, only as the firm offers it). "Want to use that, or something else (like $50 off)?" | The proposal |
| Google Business Profile | "I found this Google listing: [name, address, rating]. Is that the right one?" If several match, show them and ask. | Ask to paste 6 reviews |
| Other review sites | "Do they have reviews anywhere else, like Yelp, Angi, HomeAdvisor, or Facebook? Paste the links if so." Mention any you already found. | Google only |
| Service area map | "Do you have a service area map image? If not, the page lists the towns without a map." | Towns only, no map |
| Photos | "Do you have a folder of real job photos? Real photos beat stock. If not, I'll use photos from the website." | Website photos |
| Logo | Usually from the website. Ask only if you can't find a clean one. | Business name as text |
| Brand color | Pull from the website. Ask only if unclear. | Website's main button color |
| GHL form | "Do you have the GoHighLevel form for this page? If so, paste the embed code (it starts with `<iframe`). If not, we'll add it when we deploy." | Form slot left for deploy |
| Emergency or same-day service | Only for services where it matters (septic, plumbing, HVAC, restoration, rentals). "Do they offer emergency or same-day service? What hours?" | Leave it off the page |

The person's answers in chat count as a source. Don't guess and don't treat silence as a yes.

## Business owners vs. agency owners

- **Business owner:** say "your business", "your customers". They know the facts, so ask them directly instead of hunting online. They may not know what GHL is. If they don't use GoHighLevel, note it in `lander-notes.md` so deploy-lander-laa handles the form another way.
- **Agency owner:** say "your client". They may have notes and a survey. Use those first.

## Handoff block

Write this at the end of `lander-notes.md` once the pages are approved. deploy-lander-laa reads it so it doesn't ask again. Leave a line blank if unknown. **Never put a password here.**

```
## Handoff to deploy-lander-laa
built_by: build-lander-laa
folder: [full path to this lander folder]
business_name: [exact name]
service: [the one service]
city: [primary city, state]
suggested_slug: [lowercase-hyphen name, e.g. smith-septic-pumping]
phone: [number used on the page]
variant_a: [one-line description]
variant_b: [one-line description of the one change]
ghl_form_in_pages: [yes / no]
for: [own business / client]
```
