---
name: build-lander-laa
description: "Builds a finished, ready-to-deploy landing page for a local service business: Variant A, Variant B, and a thank-you page, written from the business's real website and its reviews (Google, Yelp, Angi, HomeAdvisor, Facebook). Works for agency owners building for a client and for business owners building their own page, with or without kickoff notes. Lets the person preview and request changes (in the browser, as a shareable Claude artifact, or hands-on in Claude Design) before handing off to deploy-lander-laa. Triggers: build lander, build a landing page, make a lander, make my landing page, new lander for client, /build-lander-laa, /build-lander."
version: 1.0.0
---

# build-lander-laa

Builds the three pages a lander needs (`index-a.html`, `index-b.html`, `thank-you.html`, plus `assets/`), lets the person preview and change them, then hands the folder to **deploy-lander-laa**.

Who runs this: Local Agency Accelerator members. Some are agency owners building for a client. Some are business owners building their own page. Don't assume they have kickoff notes, an onboarding survey, a brand kit, or any technical background. Ask plain questions, find what you can yourself, and explain what you're doing in one line at a time.

In this skill, "the person" is whoever is running it. "The business" is the company the page is for (a client, or the person's own business).

**House style for everything you write on the page and in chat:** no em dashes. Use commas, periods, or "and".

---

## Phase 0: Check the setup (silent unless something's missing)

```bash
python3 --version          # needed for the checks
ls ~/.claude/skills/build-lander-laa/scripts/   # the helper scripts ship with this skill
```

If `python3` is missing, on Mac run `xcode-select --install` (installs it), on Windows tell the person to install Python from python.org and tick "Add to PATH". Nothing else is required to build and preview. GitHub and Cloudflare logins are only needed later, by deploy-lander-laa.

Set these for the rest of the skill:
```bash
SKILL_DIR=~/.claude/skills/build-lander-laa
```
If the skill lives somewhere else (e.g. a project's `.claude/skills/`), use that path.

---

## Phase 1: Interview

Load `references/intake.md` and follow it. Short version:

1. Ask **who it's for**: their own business, or a client's.
2. Ask for the **business name, website, and the one service** this page sells. One service per page.
3. Ask for the **Google Business Profile** link, or find it yourself from the name and city.
4. Ask for **anything they already have** (kickoff notes, survey, old lander, brand colors, logo, photos folder). All optional.
5. Ask for the **phone number calls should go to**, the **offer**, and the **service area**.
6. Ask for the **GHL form embed** if they have it. If not, the page gets a marked form slot and deploy-lander-laa adds the form later.

Ask everything you can't find yourself in **one grouped message**. Then research (Phase 3) before asking anything else.

---

## Phase 2: Pick the starting design

Load `references/templates.md`. In order:

1. **A matching template** from the LAA template pack (Skool classroom, M1.5 "LAA Landing Page Templates"), if the person has it. Look in `$SKILL_DIR/templates/` first, then ask: "Do you have the LAA Landing Page Templates folder from the Skool classroom (M1.5)? If so, tell me where it is (usually Downloads)." Unzip it into `$SKILL_DIR/templates/` once so it's there next time.
2. **A page the person likes** (their old lander, a competitor's page, or a design they made in Claude Design). Use its layout, not its words or photos.
3. **Build from the standard layout** in `references/page-layout.md`. This always works, so never stop because there's no template.

If the starting file is a Claude Design bundle (contains `<script type="__bundler/template">`), run:
```bash
python3 "$SKILL_DIR/scripts/unbundle.py" "<file>.html"
```

Tell the person which starting point you used in one line.

---

## Phase 3: Research the business

Use web search and web fetch. Never invent facts.

**Order of trust (highest first):**
1. What the person told you in this chat, plus any notes or survey they gave you.
2. The business's own website.
3. The Google Business Profile.
4. Anything else online (old lander, directories). Only to fill gaps, and flag every fact that came from here.

Collect: business name as customers know it, phone, city and service area, years in business, licensing and insurance, warranties or guarantees, what's special about how they do **this service**, hours, and emergency or same-day availability.

- Years in business, job counts, licensing, warranties, financing, "family owned", "24/7": **only if a source states it.** If not, leave it out. Don't approximate.
- If sources disagree, use the higher one and note the conflict for the report.
- Ignore the business's other services. Every line on the page is about this one service.

**Reviews:** load `references/copy-rules.md` → "Reviews" and follow it. Check Google plus Yelp, Angi, HomeAdvisor, and Facebook. Each platform's rating is shown separately (never combined), and six real reviews are quoted word for word with the correct source on each card. If a profile can't be read, ask the person to paste that platform's reviews, rating, and count.

**Service area map:** this skill doesn't make map images. If the person has one, put it in `assets/` and use it. If they don't, point them to the **M2.3.1 Service Area Map Image Prompt** lesson in the Claude Code Landing Pages course (https://www.skool.com/local-google-ads/classroom/5d541fd8?md=c763cd605e824e3a8ccfec4d8c8887af), which has the prompt to make one in ChatGPT or Gemini. They can give it to you now or add it later with edit-lander-laa. Otherwise keep the town list and remove the map slot cleanly, with no empty box left behind.

**Photos:** use the person's own photos first (ask for a folder). Then photos from the business's website (download them into `assets/`, never hotlink). Only use stock photos if the person says that's OK, and say which ones are stock.

---

## Phase 4: Write the pages

Load `references/copy-rules.md` and follow it exactly. It covers headlines, the phone links, wording by service, reviews, the thank-you page, and what to delete.

Output folder (create it, ask if the person wants it somewhere else):
```
~/Landers/[Business Name] [Service]/
  index-a.html
  thank-you.html
  assets/            every image, logo, and map
  lander-notes.md    sources, rating, phone, open questions (never deployed)
```

- Never overwrite an existing lander folder. If the name is taken, ask, or add a suffix.
- Every image goes in `assets/` and is referenced as `assets/filename.jpg`.
- If there's no GHL form yet, keep the template's form slot and add the comment `<!-- GHL FORM EMBED -->` inside it.
- Put the comment blocks `<!-- TRACKING SCRIPTS (HEAD) -->` (in `<head>`), `<!-- TRACKING SCRIPTS (BODY) -->` (right after `<body>`), and on the thank-you page `<!-- CONVERSION TRACKING -->` (in `<head>`) on every page if the starting design doesn't already have them. deploy-lander-laa pastes tracking code there.

Then run the checks and fix everything they flag:
```bash
python3 "$SKILL_DIR/scripts/check_lander.py" "<folder>" --phone "<phone>" [--service <type>]
python3 "$SKILL_DIR/scripts/render_check.py" "<folder>"     # skips itself if Playwright isn't installed
```
`--service` is one of `dumpster`, `porta-potty`, `septic`, `plumbing`, `home-services`, `law` (leave it off for anything else, and check the wording yourself against the table in copy-rules.md).

---

## Phase 5: Make Variant B

A split test changes **one thing**. Offer three ideas that fit this page, for example:
- A different headline angle (speed vs. price vs. trust)
- A different hero photo
- A different offer or button wording

Recommend one and let the person pick. Copy `index-a.html` to `index-b.html` and make only that change. Record both one-line descriptions in `lander-notes.md` (deploy-lander-laa shows them on the reports page). Re-run `check_lander.py`.

---

## Phase 6: Preview and change

Load `references/preview.md` and follow it. In short, offer these, in this order:

1. **Look at it now (always).** Open `index-a.html`, `index-b.html`, and `thank-you.html` in the person's browser. This is the most accurate preview, because the real form, photos, and phone links all work.
2. **Share it as a link (optional).** Publish a preview copy as a Claude artifact so the person (or their client) can open it on any device and leave comments. The form shows as a placeholder there. Skip this if the Artifact tool isn't available in this session.
3. **Edit it by hand (optional).** For people who want to drag things around: open it in Claude Design, edit, export, and give Claude the folder back.

The files in the lander folder are always the master copy. Every change, wherever it was asked for, gets made to those files, then checks re-run, then the preview refreshes.

Loop until the person says it's good. Don't move on without a clear "looks good" or "deploy it".

---

## Phase 7: Report and hand off

Tell the person, briefly:
1. Which starting design you used.
2. Any fact you couldn't confirm, and every section you removed for lack of a source.
3. Source conflicts and which one won.
4. The ratings and counts you used for each review site, where and when you read them.
5. What Variant B tests.
6. Anything still missing (GHL form, logo, photos, map).

Make sure `lander-notes.md` ends with the handoff block from `references/intake.md` → "Handoff block", filled in.

Then offer: "Ready to put it live? I'll run deploy-lander-laa with this folder, and most of the setup questions are already answered." If they say yes, load the deploy-lander-laa skill and start it with the folder path. It reads the handoff block and skips the questions already answered.
