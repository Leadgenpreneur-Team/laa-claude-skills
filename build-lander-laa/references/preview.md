# Preview and change

**The lander folder is the master copy.** Previews are views of it. Whatever way a change is asked for (chat, an artifact comment, a Claude Design export), the change gets made to the files in the lander folder, then:

```bash
python3 "$SKILL_DIR/scripts/check_lander.py" "<folder>" --phone "<phone>" [--service <type>]
```
then the preview is refreshed. Keep a quick backup before big changes: `cp -r "<folder>" "<folder>-backup-$(date +%H%M)"`, and delete old backups once the person approves.

Offer the options like this, in one message:

> "Your pages are ready to look at. I've opened them in your browser.
> - Tell me anything you want changed and I'll update it.
> - Want a **link** you can open on your phone or send to [your client / someone else] for comments? I can publish a preview as a Claude artifact.
> - Prefer to **move things around yourself**? You can open it in Claude Design and edit it by hand."

---

## 1. Browser preview (always)

Open all three pages:
```bash
# Mac
open "<folder>/index-a.html" "<folder>/index-b.html" "<folder>/thank-you.html"
# Windows (Git Bash or PowerShell)
start "" "<folder>/index-a.html"; start "" "<folder>/index-b.html"; start "" "<folder>/thank-you.html"
```
This shows the real GHL form, photos, and phone links. To check the phone layout, tell the person: "Right-click the page, choose Inspect, then click the phone icon at the top of the panel" (or just open it on their phone later with the artifact link).

After each round of changes, tell them to refresh the tab.

## 2. Shareable artifact (optional)

Only if the Artifact tool is available in this session (Claude desktop app, Pro plan or higher). If it isn't, skip this option without mentioning tool names; just don't offer it.

Artifacts are a single page that can't load anything from other sites. So build a preview copy:
```bash
mkdir -p "<folder>/../.lander-previews"
python3 "$SKILL_DIR/scripts/make_preview.py" "<folder>/index-a.html" "<folder>/../.lander-previews/<slug>-a.html"
```
The script puts the photos inside the page, swaps the GHL form for a "form shows here on the live page" box, and removes tracking scripts. Publish that file with the Artifact tool (title like "[Business] Lander Preview A", icon "page"). Do the same for B and the thank-you page only if the person wants them.

Tell the person in one line: "Here's a link you can open anywhere or share. The form shows as a gray box in the preview; the real form is on your live page."

**Changes:** when the person (or anyone they share it with) leaves comments on the artifact, or asks in chat:
1. Make the change in the master file in the lander folder.
2. Re-run `check_lander.py`.
3. Re-run `make_preview.py` to the **same output path**, and republish the same file so the link stays the same.

Never edit the preview copy directly; it gets overwritten each time.

The artifact is private until the person shares it. Don't put anything private in it (it never contains tracking codes or form IDs, because the script strips them).

## 3. Hands-on editing in Claude Design (optional)

For people who want to drag, resize, and restyle things themselves.

1. Tell them: "Open Claude, start a new **Design**, and attach the files from this folder: `index-a.html` plus everything in `assets/` (or attach a zip of the whole folder). Ask it to show the page so you can edit it." If they prefer, they can start from the artifact link instead.
2. They edit on the canvas.
3. When done: **Export → Download as .zip** (or **standalone HTML**). Then tell Claude where the download is (usually Downloads).
4. Bring it back:
   - Unzip into a new folder next to the lander folder (never over it).
   - Run `scripts/unbundle.py` on the exported HTML if it's bundled.
   - Copy the edited page over the master (`index-a.html`, or whichever page they edited) and any new images into `assets/`. Rename bundle images (`<uuid>.jpg`) to descriptive names and update the references.
   - **Put back anything the export lost:** the GHL form embed, `data-tel-link` on every phone link, the tracking comment blocks, the phone CSS rule, and the `noindex` tag if it was there. Compare against the backup.
   - Run `check_lander.py` and `render_check.py`, fix anything flagged, and re-open the browser preview so they can confirm it's what they made.
5. If they edited Variant A after Variant B was made, ask whether B should get the same edits (usually yes, so the test still changes only one thing).

## When they're happy

Get a clear "looks good" / "deploy it". Then delete the backups and `.lander-previews` folder (the artifact link keeps working), and go to Phase 7.
