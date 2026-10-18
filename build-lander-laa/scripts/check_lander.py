#!/usr/bin/env python3
"""Check a finished lander folder before preview or deploy.

Usage:
    python3 check_lander.py FOLDER --phone 5551234567 [--service septic] [--rating "4.9" --reviews 318]

FOLDER holds index-a.html, index-b.html (optional until Variant B exists),
thank-you.html, and assets/. Prints PASS / FAIL lines and exits 1 on any FAIL.
"""
import argparse
import html as htmllib
import os
import re
import sys

PLACEHOLDERS = [
    r"\[[A-Z][A-Z0-9 _/\-]*\]", r"\[N\]", r"\[XX\]", r"Goes Here", r"Lorem", r"ipsum",
    r"123-456-7890", r"1234567890", r"\(555\) ?555-5555", r"Your [A-Z][a-z]+(?: [A-Z][a-z]+)? Co\b",
    r"City, ST\b", r"ghl-embed-slot", r"your company", r"Paste your form", r"logo-ph",
    r"__bundler",
]

AVOID = {
    "dumpster": ["assessment", "technician", "estimate visit"],
    "porta-potty": ["assessment", "technician", "repair"],
    "home-services": ["delivery", "units"],
    "septic": ["delivery", "units", "remodel"],
    "plumbing": ["delivery", "units"],
    "law": ["quote", "estimate", "crew", "service visit"],
}

PAGES = ["index-a.html", "index-b.html", "thank-you.html"]


def visible_text(src):
    src = re.sub(r"<(script|style|noscript)[\s\S]*?</\1>", " ", src, flags=re.I)
    src = re.sub(r"<!--[\s\S]*?-->", " ", src)
    src = re.sub(r"<[^>]+>", " ", src)
    return htmllib.unescape(re.sub(r"\s+", " ", src))


def digits(s):
    d = re.sub(r"\D", "", s)
    return d[-10:] if len(d) >= 10 else d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--phone", required=True, help="the number calls should go to")
    ap.add_argument("--service", choices=sorted(AVOID), help="for the wrong-service word check")
    ap.add_argument("--rating")
    ap.add_argument("--reviews")
    a = ap.parse_args()

    fails, warns = [], []
    want = digits(a.phone)
    found = [p for p in PAGES if os.path.exists(os.path.join(a.folder, p))]
    for req in ("index-a.html", "thank-you.html"):
        if req not in found:
            fails.append(f"missing {req}")

    for page in found:
        path = os.path.join(a.folder, page)
        src = open(path, encoding="utf-8").read()
        text = visible_text(src)

        for pat in PLACEHOLDERS:
            for m in set(re.findall(pat, src if pat in (r"ghl-embed-slot", r"__bundler", r"logo-ph") else text, flags=re.I)):
                m = m if isinstance(m, str) else m[0]
                fails.append(f"{page}: leftover placeholder text matching {pat!r}: {m!r}")

        if "—" in text:
            fails.append(f"{page}: em dash in visible text ({text.count(chr(0x2014))}x)")

        # Phone numbers: every tel: link goes to the right number
        for href in re.findall(r'href="tel:([^"]*)"', src):
            if digits(href) != want:
                fails.append(f"{page}: tel link goes to {href}, expected {a.phone}")
        tel_count = len(re.findall(r'href="tel:', src))
        if tel_count == 0:
            fails.append(f"{page}: no tel: links at all")

        # Visible phone numbers that aren't links
        linked = set(htmllib.unescape(t).strip() for t in re.findall(r'<a[^>]+href="tel:[^"]*"[^>]*>([^<]*)</a>', src))
        for num in set(re.findall(r"\(?\b\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}\b", text)):
            if digits(num) != want:
                fails.append(f"{page}: visible phone number {num} doesn't match {a.phone}")
            elif num.strip() not in linked:
                warns.append(f"{page}: {num} appears as text; make sure every instance is inside a tel: link")

        # Images / CSS urls must resolve inside assets/
        refs = re.findall(r'(?:src|href)="([^"]+\.(?:jpe?g|png|webp|gif|svg|ico))"', src, flags=re.I)
        refs += re.findall(r"url\(['\"]?([^)'\"]+\.(?:jpe?g|png|webp|gif|svg))['\"]?\)", src, flags=re.I)
        for ref in set(refs):
            if ref.startswith(("http://", "https://", "data:", "//")):
                if "leadconnectorhq" not in ref and "msgsndr" not in ref:
                    warns.append(f"{page}: image loads from another site ({ref[:80]}); copy it into assets/ instead")
                continue
            rel = ref.lstrip("/")
            if not rel.startswith("assets/"):
                fails.append(f"{page}: image {ref} is not inside assets/")
            elif not os.path.exists(os.path.join(a.folder, rel)):
                fails.append(f"{page}: image {ref} is missing from the folder")

        if page.startswith("index"):
            if not re.search(r'leadconnectorhq\.com/widget/form/', src):
                warns.append(f"{page}: no GHL form embed yet (fine for preview, required before deploy)")
            if '<meta name="robots" content="noindex' not in src:
                warns.append(f"{page}: no noindex tag (deploy adds it)")

        if a.service:
            for w in AVOID[a.service]:
                n = len(re.findall(rf"\b{re.escape(w)}\b", text, flags=re.I))
                if n:
                    fails.append(f"{page}: uses '{w}' {n}x, which doesn't fit a {a.service} page")

        if a.rating and a.reviews:
            if a.rating not in text or a.reviews not in text:
                fails.append(f"{page}: rating {a.rating} / {a.reviews}+ reviews not shown as expected")

        h1 = re.findall(r"<h1[^>]*>([\s\S]*?)</h1>", src, flags=re.I)
        if len(h1) != 1:
            warns.append(f"{page}: {len(h1)} <h1> tags (expected 1)")

        print(f"checked {page}: {tel_count} phone link(s)")

    for w in sorted(set(warns)):
        print("WARN ", w)
    for f in sorted(set(fails)):
        print("FAIL ", f)
    print("RESULT:", "PASS" if not fails else f"{len(set(fails))} problem(s) to fix")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
