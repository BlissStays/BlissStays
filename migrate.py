#!/usr/bin/env python3
"""
migrate.py – strip inline navbars & footers from every HTML page,
replacing them with <script src="navbar.js"> and <script src="footer.js">.

Run from the repo root:
    python3 migrate.py
"""

import os
import re

# ── pages to migrate ──────────────────────────────────────────────────────────
PAGES = [
    'property.html',
    'property2.html',
    'property3.html',
    'property4.html',
    'propertyex.html',
    'index.html',
    'booknow.html',
    'contactus.html',
    'faq.html',
    'terms.html',
    'privacy.html',
    'maidavale-details.html',
    'F1-paddington-details.html',
    'F2-paddington-details.html',
    'kennigngton-detail.html',
    'nine1-detail.html',
    'nine2-detail.html',
    'wimbleton1-details.html',
    'wimbleton2-details.html',
    'wimbleton3-details.html',
]

# ── CSS/JS fingerprints that mark a block as "navbar only" ────────────────────
NAVBAR_STYLE_KEYS = [
    '.mnav-', '.header-inner', '.main-nav', '.drop-panel',
    '.has-dropdown', '.mnav-sheet', '.mnav-btn', '.mnav-panel',
    'header{', 'header {', '.mnav-cta', '.mnav-book',
    '.mnav-label', '.mnav-item', '.mnav-group',
]

NAVBAR_SCRIPT_KEYS = [
    'mnavBtn', 'mnavClose', 'openSheet', 'closeSheet',
    'menuToggle', 'mnav-sheet', "classList.add('scrolled')",
    "classList.toggle('scrolled')", "classList.remove('scrolled')",
    "body.classList.add('menu-open')",
]

FOOTER_STYLE_KEYS = [
    '.footer-container', '.footer-column', '.footer-logo',
    '.footer-bottom', '.footer-links-group', '.footer-logo-section',
    '.social-icons',
]

# ─────────────────────────────────────────────────────────────────────────────


def contains_any(text, keys):
    return any(k in text for k in keys)


def is_only_navbar_style(block_text):
    """True when the style block ONLY contains navbar-related rules."""
    if not contains_any(block_text, NAVBAR_STYLE_KEYS):
        return False
    # Make sure it doesn't also contain page-specific selectors we'd lose
    SAFE_TO_KEEP_KEYS = [
        '.hero', '.property', '.gallery', '.brand-card',
        '.mv-', '.wa-widget', '#wa-', '.section', '.grid',
        '.card', '.btn', '.contact', '.form', '.faq',
        '.terms', '.privacy', 'animate', '@keyframes clickBounce',
        '.loc-list', '.menu-list', '.loc-title',   # these ARE navbar-only
    ]
    # loc-list / menu-list / loc-title appear in navbar so ignore them
    NOISE = {'.loc-list', '.menu-list', '.loc-title'}
    non_navbar = [k for k in SAFE_TO_KEEP_KEYS if k not in NOISE and k in block_text]
    return len(non_navbar) == 0


def is_only_footer_style(block_text):
    """True when the style block ONLY contains footer-related rules."""
    if not contains_any(block_text, FOOTER_STYLE_KEYS):
        return False
    NON_FOOTER = ['.hero', '.mv-', '.wa-widget', '.main-nav', '.header']
    return not contains_any(block_text, NON_FOOTER)


def is_navbar_script(block_text):
    return contains_any(block_text, NAVBAR_SCRIPT_KEYS)


def process(src):
    """Parse src line-by-line and return cleaned version."""
    lines = src.split('\n')
    out = []
    i = 0
    in_head = True        # track whether we're inside <head>
    navbar_added = False  # did we already insert navbar.js?
    footer_added = False  # did we already insert footer.js?

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── track head/body boundary ─────────────────────────────────────
        if re.match(r'</head\s*>', stripped, re.I):
            in_head = False

        # ── <body> tag → insert navbar.js immediately after ──────────────
        if re.match(r'<body[^>]*>', stripped, re.I) and not navbar_added:
            out.append(line)
            out.append('<script src="navbar.js"></script>')
            navbar_added = True
            i += 1
            continue

        # ── skip <header>…</header> (the nav bar HTML) ───────────────────
        if re.match(r'<header[\s>]', stripped, re.I) and not in_head:
            depth = 0
            while i < len(lines):
                if re.search(r'<header[\s>]', lines[i], re.I):
                    depth += 1
                if re.search(r'</header\s*>', lines[i], re.I):
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                i += 1
            continue

        # ── skip <aside id="mnav"…</aside> (mobile nav sheet) ────────────
        if re.match(r'<aside\s[^>]*id=["\']mnav["\']', stripped, re.I):
            while i < len(lines):
                if re.search(r'</aside\s*>', lines[i], re.I):
                    i += 1
                    break
                i += 1
            continue

        # ── skip <footer…</footer> and insert footer.js instead ──────────
        if re.match(r'<footer[\s>]', stripped, re.I) and not in_head and not footer_added:
            while i < len(lines):
                if re.search(r'</footer\s*>', lines[i], re.I):
                    i += 1
                    break
                i += 1
            out.append('<script src="footer.js"></script>')
            footer_added = True
            continue

        # ── skip inline <style> blocks (body only) that are navbar/footer ─
        if (not in_head
                and re.match(r'<style[\s>]', stripped, re.I)
                and '</style>' not in stripped):
            # collect the whole block
            block_lines = [lines[i]]
            j = i + 1
            while j < len(lines):
                block_lines.append(lines[j])
                if '</style>' in lines[j]:
                    j += 1
                    break
                j += 1
            block_text = '\n'.join(block_lines)
            if is_only_navbar_style(block_text) or is_only_footer_style(block_text):
                i = j
                continue  # drop it
            else:
                out.extend(block_lines)
                i = j
                continue

        # ── skip inline <script> blocks that are navbar-specific ──────────
        if (not in_head
                and re.match(r'<script[^>]*>', stripped, re.I)
                and 'src=' not in stripped
                and '</script>' not in stripped):
            block_lines = [lines[i]]
            j = i + 1
            while j < len(lines):
                block_lines.append(lines[j])
                if '</script>' in lines[j]:
                    j += 1
                    break
                j += 1
            block_text = '\n'.join(block_lines)
            if is_navbar_script(block_text):
                i = j
                continue  # drop it
            else:
                out.extend(block_lines)
                i = j
                continue

        # ── strip stale end-of-header HTML comments ───────────────────────
        if '<!-- =====' in stripped and '/HEADER' in stripped:
            i += 1
            continue

        out.append(line)
        i += 1

    # ── ensure footer.js is added if not already (fallback) ──────────────
    if not footer_added:
        # insert before </body>
        result = '\n'.join(out)
        result = result.replace('</body>', '<script src="footer.js"></script>\n</body>', 1)
        return result

    return '\n'.join(out)


def migrate_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    cleaned = process(src)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    print(f'  ✓  {path}')


if __name__ == '__main__':
    base = os.path.dirname(os.path.abspath(__file__))
    print('Migrating pages...')
    for page in PAGES:
        full = os.path.join(base, page)
        if os.path.exists(full):
            migrate_file(full)
        else:
            print(f'  –  {page} (not found, skipping)')
    print('Done.')
