#!/usr/bin/env python3
"""Turn a Claude Design bundled HTML file into plain HTML.

Claude Design exports (and some templates) wrap the real page in
<script type="__bundler/template"> with images in <script type="__bundler/manifest">.
Those files only render with JavaScript and can't be deployed as-is.

Usage:
    python3 unbundle.py PAGE.html [PAGE2.html ...]

Each file is rewritten in place as plain HTML. Images are written to an
`assets/` folder next to the file and referenced as `assets/<name>`.
Files that aren't bundled are left alone.
"""
import base64
import json
import os
import re
import sys
import zlib

EXT = {
    "image/png": "png", "image/jpeg": "jpg", "image/jpg": "jpg", "image/svg+xml": "svg",
    "image/webp": "webp", "image/gif": "gif", "image/x-icon": "ico",
    "font/woff2": "woff2", "font/woff": "woff", "font/ttf": "ttf", "application/font-woff2": "woff2",
}


def unbundle(path):
    html = open(path, encoding="utf-8").read()
    tpl = re.search(r'<script type="__bundler/template">([\s\S]*?)</script>', html)
    if not tpl:
        # Plain HTML, but Claude Design sometimes leaves a thumbnail <template> behind.
        # deploy-lander-laa's bundle check trips on it, so remove it.
        cleaned, n = re.subn(r'<template id="__bundler_thumbnail"[\s\S]*?</template>\s*', "", html)
        if n:
            with open(path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            print(f"{path}: plain HTML, removed {n} leftover Claude Design thumbnail block(s)")
        else:
            print(f"{path}: plain HTML, nothing to do")
        return "__bundler" not in cleaned
    man = re.search(r'<script type="__bundler/manifest">([\s\S]*?)</script>', html)
    try:
        page = json.loads(tpl.group(1).strip())
        manifest = json.loads(man.group(1).strip()) if man else {}
    except json.JSONDecodeError as e:
        print(f"{path}: could not read the bundle ({e})")
        return False

    assets_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    for uuid, entry in manifest.items():
        data = base64.b64decode(entry.get("data", ""))
        if entry.get("compressed"):
            try:
                data = zlib.decompress(data, 16 + zlib.MAX_WBITS)
            except zlib.error:
                pass
        name = f"{uuid}.{EXT.get(entry.get('mime', ''), 'bin')}"
        with open(os.path.join(assets_dir, name), "wb") as f:
            f.write(data)
        page = page.replace(uuid, f"assets/{name}")

    # If a uuid was already prefixed with a slash or path, normalise to relative
    page = re.sub(r'(["\'(])/+assets/', r'\1assets/', page)
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    left = re.findall(r"__bundler", page)
    print(f"{path}: unbundled, {len(manifest)} asset(s) extracted" + (" (WARNING: bundler text still present)" if left else ""))
    return not left


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    ok = all(unbundle(p) for p in sys.argv[1:])
    sys.exit(0 if ok else 1)
