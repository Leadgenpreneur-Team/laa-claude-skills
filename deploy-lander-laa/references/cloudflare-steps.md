# Cloudflare Steps

---

## Verifying the Split Test

Use this for Phase 7 after the first deployment. This check only confirms the split test cookie — form and UTM testing happens in Phase 11.

Tell the user:

> 1. Open a **new incognito/private window** in Chrome (Cmd+Shift+N on Mac)
> 2. Go to `https://lander-[SLUG].pages.dev`
> 3. Open **DevTools** (F12 or right-click → Inspect)
> 4. Click the **Network** tab
> 5. Reload the page (Cmd+R)
> 6. In the Network list, click the first request — it should be the domain (e.g. `lander-[SLUG].pages.dev`)
> 7. Click the **Cookies** tab in the right panel
> 8. Look for a cookie named `ab_variant` — it should show `a` or `b`
> 9. Close the incognito window, open a fresh one, and go to the same URL — confirm the variant alternates

If no cookie appears: check that `wrangler pages deploy` completed without errors and the `_worker.js` file is in the repo root.

If the reports page is blank or shows an error: confirm the D1 binding name in `wrangler.toml` is exactly `DB` (case-sensitive) and that the schema was run successfully.

---

## Purchasing and Connecting a Domain

Use this for Phase 11. The team member must do this in the Cloudflare dashboard — there is no CLI for domain registration.

### Step 1: Register the Domain

> 1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) and log into your Cloudflare account
> 2. In the left sidebar, click **Domain Registration** → **Register Domains**
> 3. Type the domain name and click **Search**
> 4. If available, click **Purchase** and complete checkout
> 5. Wait for the domain to be active (usually instant, but can take a few minutes)

### Step 2: Connect the Domain to Cloudflare Pages

> 1. In the Cloudflare dashboard, go to **Workers & Pages**
> 2. Click on the `lander-[SLUG]` project
> 3. Go to the **Custom Domains** tab
> 4. Click **Set up a Custom Domain**
> 5. Type the domain (e.g. `naturescallsiteservices.net`) and click **Continue**
> 6. Cloudflare will show a DNS record to add — since the domain is registered in the same Cloudflare account, click **Activate Domain**
> 7. Wait for the status to show **Active** (usually takes 1-5 minutes)

### Step 3: Add www (apex domains only)

If the domain is an **apex domain** (e.g. `clientdomain.com` with no subdomain prefix), you must also add `www.clientdomain.com` as a second custom domain — otherwise `www.clientdomain.com` returns a Cloudflare error.

> 1. In the same **Custom Domains** tab, click **Set up a Custom Domain** again
> 2. Enter `www.[DOMAIN]` and click **Continue**
> 3. Click **Activate Domain** and wait for it to show **Active**

If the domain is a **subdomain** (e.g. `landers.clientdomain.com`), skip this step entirely.

### Step 4: Verify

> Open a new browser tab and go to `https://[DOMAIN]`. The lander should load. If you see a Cloudflare error, wait another minute and try again — DNS propagation is almost instant within Cloudflare but can take a moment to fully activate.
>
> If it's an apex domain, also confirm `https://www.[DOMAIN]` loads correctly.

Once the domain is live, proceed with setting the GHL form redirect URL in Phase 11.

---

## Manual DNS Fallback

Use this only if the automated DNS record creation in Phase 10 Step 4 returns a permission error (your wrangler OAuth token may only have `zone:read` scope).

> 1. Go to [dash.cloudflare.com](https://dash.cloudflare.com) and log into your Cloudflare account
> 2. In the left sidebar, click your domain under **Websites**, then go to **DNS** → **Records**
> 3. Check if a CNAME record for the **apex** (`[DOMAIN]`) already exists pointing to `lander-[SLUG].pages.dev`. If not, click **Add Record**:
>    - Type: CNAME
>    - Name: `@`
>    - Target: `lander-[SLUG].pages.dev`
>    - Proxy: On (orange cloud)
>    - Click Save
> 4. Now check for a **www** CNAME record. This one is almost never auto-created. Click **Add Record**:
>    - Type: CNAME
>    - Name: `www`
>    - Target: `lander-[SLUG].pages.dev`
>    - Proxy: On (orange cloud)
>    - Click Save
>
> **You need BOTH records** — apex AND www. If only one exists, the other domain will stay in Pending status and won't resolve.

After adding both records, return to the polling step in Phase 10 Step 4 to verify both domains show Active.
