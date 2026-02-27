#!/usr/bin/env python3
"""
BlissStays full site optimiser
- Converts all JPG/PNG images to WebP (max 1920px, quality 82)
- Updates all HTML files to reference .webp files
- Adds loading="lazy" to below-fold images
- Defers non-critical JS
- Adds preconnect hints
- Optimises favicon reference
"""
import os, re, glob
from PIL import Image

BASE = "/home/user/BlissStays"
MAX_DIM = 1920
QUALITY = 82

# ── 1. Convert images ────────────────────────────────────────────────────────

def convert_image(src_path):
    """Resize + convert to WebP, return (webp_path, saved_bytes)."""
    webp_path = re.sub(r'\.(jpe?g|png)$', '.webp', src_path, flags=re.IGNORECASE)
    if os.path.exists(webp_path):
        orig = os.path.getsize(src_path)
        new  = os.path.getsize(webp_path)
        return webp_path, orig - new

    try:
        img = Image.open(src_path).convert("RGB")
        w, h = img.size
        if w > MAX_DIM or h > MAX_DIM:
            ratio = min(MAX_DIM / w, MAX_DIM / h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
        img.save(webp_path, "WEBP", quality=QUALITY, method=6)
        orig = os.path.getsize(src_path)
        new  = os.path.getsize(webp_path)
        return webp_path, orig - new
    except Exception as e:
        print(f"  SKIP {src_path}: {e}")
        return None, 0

print("=== Phase 1: Converting images to WebP ===")
total_saved = 0
converted = 0
skipped_icons = set()

for ext in ("jpg", "jpeg", "png", "JPG", "JPEG", "PNG"):
    for src in glob.glob(os.path.join(BASE, "**", f"*.{ext}"), recursive=True):
        if ".git" in src:
            continue
        # Skip tiny icons/logos (< 20KB) – not worth converting
        if os.path.getsize(src) < 20_000:
            skipped_icons.add(src)
            continue
        webp, saved = convert_image(src)
        if webp:
            converted += 1
            total_saved += saved
            mb_saved = saved / 1_048_576
            mb_new = os.path.getsize(webp) / 1_048_576
            print(f"  ✓ {os.path.relpath(src, BASE)!s:<55} → {mb_new:.1f}MB  (saved {mb_saved:.1f}MB)")

print(f"\nConverted {converted} images, freed ~{total_saved/1_048_576:.0f}MB\n")

# ── 2. Update HTML files ──────────────────────────────────────────────────────

print("=== Phase 2: Updating HTML files ===")

HTML_FILES = glob.glob(os.path.join(BASE, "*.html"))

# Regex: replace .jpg / .jpeg / .png inside quotes with .webp
# BUT only if a .webp counterpart actually exists
IMG_EXT_RE = re.compile(r'(["\'`])([^"\'`]+?)\.(jpe?g|png)\1', re.IGNORECASE)

def ext_replacer(m):
    quote  = m.group(1)
    path   = m.group(2)
    ext    = m.group(3)
    full   = os.path.join(BASE, path + "." + ext)
    webp   = re.sub(r'\.(jpe?g|png)$', '.webp', full, flags=re.IGNORECASE)
    if os.path.exists(webp):
        return f'{quote}{path}.webp{quote}'
    return m.group(0)   # leave unchanged if no webp exists

# Regex: add loading="lazy" to img tags that don't already have it
# Skip the first img (hero/logo) – it's above the fold
LAZY_RE = re.compile(r'(<img\b(?![^>]*\bloading=)[^>]*)(>)', re.IGNORECASE)

def add_lazy(m):
    return m.group(1) + ' loading="lazy"' + m.group(2)

# Preconnect hints to add after <head>
PRECONNECT = (
    '<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>\n'
    '<link rel="preconnect" href="https://code.jquery.com" crossorigin>\n'
)

# Defer jQuery and Owl scripts (move to before </body> or add defer)
SCRIPT_RE = re.compile(
    r'<script\b([^>]*?)\bsrc=("[^"]+(?:jquery|owl\.carousel)[^"]*")([^>]*)>(.*?)</script>',
    re.IGNORECASE | re.DOTALL
)

def defer_script(m):
    attrs  = m.group(1) + m.group(3)
    src    = m.group(2)
    # already deferred?
    if 'defer' in attrs or 'async' in attrs:
        return m.group(0)
    return f'<script{attrs} src={src} defer></script>'

for html_path in HTML_FILES:
    with open(html_path, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()

    out = src

    # 2a. Swap image extensions to .webp
    out = IMG_EXT_RE.sub(ext_replacer, out)

    # 2b. Add lazy loading to all img tags
    # We want the FIRST img to NOT be lazy (hero / logo above fold)
    parts = LAZY_RE.split(out)
    # split returns alternating: text, group1, group2, text, group1, group2 ...
    # Easier approach: find all img tags and skip the first one
    first_done = [False]
    def maybe_lazy(m):
        if not first_done[0]:
            first_done[0] = True
            return m.group(0)          # leave first img alone
        return add_lazy(m)
    out = LAZY_RE.sub(maybe_lazy, out)

    # 2c. Add preconnect hints after <head> (only if not already present)
    if 'rel="preconnect"' not in out:
        out = out.replace('<head>', '<head>\n' + PRECONNECT, 1)

    # 2d. Defer jQuery & Owl carousel scripts
    out = SCRIPT_RE.sub(defer_script, out)

    # 2e. Fix oversized favicon: replace "favicon.png" with "favicon.webp" if it exists
    favicon_webp = os.path.join(BASE, "favicon.webp")
    if os.path.exists(favicon_webp):
        out = out.replace('"favicon.png"', '"favicon.webp"')

    if out != src:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"  ✓ Updated {os.path.basename(html_path)}")
    else:
        print(f"  – No changes: {os.path.basename(html_path)}")

print("\n=== Phase 3: Summary ===")
print(f"Images freed: ~{total_saved/1_048_576:.0f}MB")
print(f"Icons skipped (already small): {len(skipped_icons)}")
print("Done.")
