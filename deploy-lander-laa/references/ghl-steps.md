# GHL Steps

---

## Getting the Form Embed Code

Use this for Phase 4 of the deployment.

Tell the team member:

> Go into GoHighLevel (Automation Pilot) and follow these steps:
>
> 1. Log into the **client's sub-account** (not the agency account)
> 2. In the left sidebar, go to **Sites**
> 3. Click **Forms** in the top navigation
> 4. Find the form for this client
> 5. Click the **three-dot menu** on the form → click **Integrate**
> 6. Under "Embed Form", click **Copy Code**
> 7. Paste the full code (it includes an `<iframe>` and a `<script>` tag) back here

The code will look like this (yours will have a different form ID):
```html
<iframe
    src="https://api.leadconnectorhq.com/widget/form/FORM_ID_HERE"
    style="width:100%;height:100%;border:none;border-radius:3px"
    id="inline-FORM_ID_HERE"
    ...
    title="Form Name Here"
>
</iframe>
<script src="https://link.msgsndr.com/js/form_embed.js"></script>
```

Paste the full block including the `<script>` tag at the end.

---

## Setting the Form Redirect URL

Use this for Phase 8 (temp `.pages.dev` URL) and again in Phase 11 (final custom domain URL).

Tell the team member:

> In GHL, go to the client's sub-account and follow these steps:
>
> 1. Go to **Sites** → **Forms**
> 2. Click **Edit** on the form
> 3. In the form editor, click the **Options** tab (or the gear/settings icon)
> 4. Find the **Redirect URL** or **Thank You Page** field
> 5. Clear the existing value and paste in **the exact URL below** — copy it character for character, including everything after the `?`
> 6. Save the form

**URL to use (Phase 11)** — always set this to the custom domain, not the `.pages.dev` URL:
```
https://[DOMAIN]/thank-you?name={{contact.name}}&email={{contact.email}}&phone={{contact.phone}}
```

**CRITICAL — do not drop the query string.** The `?name={{contact.name}}&email={{contact.email}}&phone={{contact.phone}}` part is required. These are GHL merge fields that pass the lead's info into the URL so the reports dashboard can capture the lead event. If the URL is saved without them, lead data will not be recorded.

Double-check the saved URL in GHL and confirm the full string including `?name=...&email=...&phone=...` is present before moving on.
