#!/usr/bin/env python3
"""Render the lander pages at phone and desktop width and check what code can't see.

Needs Playwright (optional). If it's missing, the skill falls back to the visual
preview in the browser. To install it once:
    pip3 install playwright && python3 -m playwright install chromium

Usage:
    python3 render_check.py FOLDER [--shots OUTDIR]

Checks, for each page at 390px and 1280px:
  - hero H1 is 3 lines or fewer
  - no broken images
  - every inline tel: link (not a button) is underlined
Saves full-page screenshots to OUTDIR (default FOLDER/../lander-screenshots).
"""
import argparse
import os
import sys

JS = r"""
() => {
  const out = {};
  const h1 = document.querySelector('h1');
  if (h1) {
    const cs = getComputedStyle(h1);
    let lh = parseFloat(cs.lineHeight);
    if (isNaN(lh)) lh = parseFloat(cs.fontSize) * 1.2;
    out.h1Lines = Math.round(h1.getBoundingClientRect().height / lh);
    out.h1Text = h1.innerText.trim().slice(0, 90);
  }
  out.broken = [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.offsetParent !== null)
                 .map(i => i.getAttribute('src').slice(0, 80));
  out.plainTel = [...document.querySelectorAll('a[href^="tel:"]')]
     .filter(a => !String(a.className).match(/btn|cta|button|tel-plain/i) && !a.closest('.mobile-call-bar') && a.offsetParent !== null)
     .filter(a => !getComputedStyle(a).textDecorationLine.includes('underline'))
     .map(a => a.innerText.trim().slice(0, 40));
  out.overflowX = document.documentElement.scrollWidth > window.innerWidth + 1;
  return out;
}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--shots")
    a = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("SKIP  Playwright not installed; check the pages by eye in the browser preview instead.")
        sys.exit(0)

    folder = os.path.abspath(a.folder)
    shots = a.shots or os.path.join(os.path.dirname(folder), "lander-screenshots")
    os.makedirs(shots, exist_ok=True)
    fails = []
    pages = [p for p in ("index-a.html", "index-b.html", "thank-you.html") if os.path.exists(os.path.join(folder, p))]
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for width in (390, 1280):
            ctx = browser.new_context(viewport={"width": width, "height": 900})
            pg = ctx.new_page()
            for name in pages:
                pg.goto("file://" + os.path.join(folder, name))
                pg.wait_for_timeout(600)
                r = pg.evaluate(JS)
                shot = os.path.join(shots, f"{name[:-5]}-{width}.png")
                pg.screenshot(path=shot, full_page=True)
                tag = f"{name} @{width}px"
                print(f"{tag}: H1 {r.get('h1Lines')} line(s): {r.get('h1Text')!r}")
                if (r.get("h1Lines") or 0) > 3:
                    fails.append(f"{tag}: hero headline wraps to {r['h1Lines']} lines (max 3). Shorten the wording.")
                for b in r["broken"]:
                    fails.append(f"{tag}: broken image {b}")
                for t in r["plainTel"]:
                    fails.append(f"{tag}: phone link '{t}' isn't underlined")
                if r["overflowX"]:
                    fails.append(f"{tag}: page scrolls sideways")
            ctx.close()
        browser.close()
    print("screenshots:", shots)
    for f in fails:
        print("FAIL ", f)
    print("RESULT:", "PASS" if not fails else f"{len(fails)} problem(s) to fix")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
