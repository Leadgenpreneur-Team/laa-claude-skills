#!/usr/bin/env python3
"""Make a single-file copy of a lander page that can be published as a Claude artifact.

Artifacts are one self-contained page and can't load files from other sites,
so this copy:
  - inlines every image from assets/ as a data URI (photos are shrunk if Pillow is installed)
  - swaps the GHL form iframe for a labelled placeholder box
  - removes outside scripts (tracking, form_embed.js) that wouldn't load anyway
  - keeps Google Fonts stylesheets, which artifacts allow

The original page is never changed. The preview is a throwaway copy:
always edit the real page, then run this again and republish.

Usage:
    python3 make_preview.py FOLDER/index-a.html OUT.html
"""
import base64
import io
import mimetypes
import os
import re
import sys

ALLOWED_SCRIPT_HOSTS = ("cdnjs.cloudflare.com", "cdn.jsdelivr.net", "unpkg.com", "cdn.tailwindcss.com", "code.jquery.com")
MAX_BYTES = 15 * 1024 * 1024

FORM_PLACEHOLDER = (
    '<div style="border:2px dashed #9aa3ad;border-radius:10px;padding:28px 18px;text-align:center;'
    'font:600 15px/1.4 system-ui,sans-serif;color:#4a5560;background:#f6f8fa;min-height:{h}px;'
    'display:flex;align-items:center;justify-content:center;flex-direction:column;gap:6px">'
    '<span>Your GHL form shows here on the live page</span>'
    '<span style="font-weight:400;font-size:13px">(previews can\'t load outside forms)</span></div>'
)


def shrink(path, raw):
    """Re-encode big photos so the artifact stays small. Falls back to the original bytes."""
    if len(raw) < 250_000 or path.lower().endswith((".svg", ".gif", ".ico")):
        return raw, None
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw))
        im.thumbnail((1600, 1600))
        out = io.BytesIO()
        if im.mode in ("RGBA", "LA", "P"):
            im.save(out, "WEBP", quality=80)
            return out.getvalue(), "image/webp"
        im.convert("RGB").save(out, "JPEG", quality=78, optimize=True)
        return out.getvalue(), "image/jpeg"
    except Exception:
        return raw, None


def main(page, out):
    folder = os.path.dirname(os.path.abspath(page))
    src = open(page, encoding="utf-8").read()
    cache, missing = {}, []

    def data_uri(ref):
        rel = ref.split("?")[0].split("#")[0].lstrip("/")
        if ref.startswith(("http", "data:", "//")) or not rel:
            return None
        if rel not in cache:
            p = os.path.join(folder, rel)
            if not os.path.exists(p):
                missing.append(ref)
                cache[rel] = None
            else:
                raw = open(p, "rb").read()
                raw, mime = shrink(p, raw)
                mime = mime or mimetypes.guess_type(p)[0] or "application/octet-stream"
                cache[rel] = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
        return cache[rel]

    def sub_attr(m):
        uri = data_uri(m.group(2))
        return f'{m.group(1)}="{uri}"' if uri else m.group(0)

    def sub_url(m):
        uri = data_uri(m.group(1))
        return f'url("{uri}")' if uri else m.group(0)

    # Local stylesheets (e.g. assets/styles.css) -> inline <style>, since the artifact is one file
    def sub_css(m):
        href = m.group(1)
        if href.startswith(("http", "//")):
            return m.group(0)
        p = os.path.join(folder, href.lstrip("/"))
        if not os.path.exists(p):
            missing.append(href)
            return m.group(0)
        css = open(p, encoding="utf-8").read()
        css_dir = os.path.dirname(href.lstrip("/"))
        # make url() refs inside the stylesheet relative to the page, so they inline below
        css = re.sub(r"url\(['\"]?(?!data:|https?:|//|/)([^)'\"]+)['\"]?\)",
                     lambda u: f'url("{os.path.normpath(os.path.join(css_dir, u.group(1)))}")', css)
        return f"<style>\n{css}\n</style>"

    src = re.sub(r'<link[^>]+rel="stylesheet"[^>]*href="([^"]+\.css)"[^>]*>', sub_css, src, flags=re.I)
    src = re.sub(r'<link[^>]+href="([^"]+\.css)"[^>]*rel="stylesheet"[^>]*>', sub_css, src, flags=re.I)

    # GHL form iframe (+ its embed script) -> placeholder
    def sub_form(m):
        h = re.search(r'height:\s*(\d+)', m.group(0)) or re.search(r'data-height="(\d+)"', m.group(0))
        return FORM_PLACEHOLDER.format(h=min(int(h.group(1)) if h else 420, 700))

    src = re.sub(r'<iframe[^>]+(?:leadconnectorhq|msgsndr)[^>]*>[\s\S]*?</iframe>', sub_form, src, flags=re.I)

    # External scripts that won't load in an artifact
    def sub_script(m):
        tag = m.group(0)
        host = re.search(r'src="(?:https?:)?//([^/"]+)', tag)
        if host and host.group(1) in ALLOWED_SCRIPT_HOSTS:
            return tag
        return "<!-- removed for preview: outside script -->" if host else tag

    src = re.sub(r'<script[^>]*\bsrc="[^"]*"[^>]*>\s*</script>', sub_script, src, flags=re.I)
    # Inline tracking snippets (gtag / fbq) do nothing in a preview
    src = re.sub(r'<script[^>]*>(?:(?!</script>)[\s\S])*?(?:gtag\(|fbq\(|googletagmanager)(?:(?!</script>)[\s\S])*?</script>',
                 "<!-- removed for preview: tracking -->", src, flags=re.I)
    src = re.sub(r"<noscript>[\s\S]*?</noscript>", "", src, flags=re.I)

    # Images
    src = re.sub(r'\b(src|href|poster)="([^"]+\.(?:jpe?g|png|webp|gif|svg|ico|avif))"', sub_attr, src, flags=re.I)
    src = re.sub(r'\bsrcset="[^"]*"', "", src, flags=re.I)
    src = re.sub(r"url\(['\"]?([^)'\"]+\.(?:jpe?g|png|webp|gif|svg|avif))['\"]?\)", sub_url, src, flags=re.I)

    with open(out, "w", encoding="utf-8") as f:
        f.write(src)
    size = os.path.getsize(out)
    print(f"preview written: {out} ({size/1024/1024:.1f} MB)")
    for m in sorted(set(missing)):
        print("WARN  image not found, will show broken in preview:", m)
    if size > MAX_BYTES:
        print("FAIL  preview is over the artifact size limit; use fewer or smaller photos")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
