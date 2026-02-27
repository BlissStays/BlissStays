#!/usr/bin/env python3
"""
cleanup2.py – second-pass cleanup:
  • Remove stale HEADER/MOBILE SHEET HTML comments left after migrate.py
  • Remove <style> blocks that ONLY contain .mnav-* rules
    (these are now fully covered by navbar.js)
"""

import os, re

PAGES = [
    'property.html', 'property2.html', 'property3.html', 'property4.html',
    'propertyex.html', 'index.html', 'booknow.html', 'contactus.html',
    'faq.html', 'terms.html', 'privacy.html',
    'maidavale-details.html', 'F1-paddington-details.html',
    'F2-paddington-details.html', 'kennigngton-detail.html',
    'nine1-detail.html', 'nine2-detail.html',
    'wimbleton1-details.html', 'wimbleton2-details.html',
    'wimbleton3-details.html',
]

MNAV_ONLY_KEYS = ['.mnav-body', '.mnav-cta', '.mnav-book']


def is_mnav_only_style(block_text):
    """True when block contains .mnav-body/.mnav-cta but nothing else
    that isn't covered by navbar.js (menu-open rule IS in navbar.js now)."""
    has_mnav = any(k in block_text for k in MNAV_ONLY_KEYS)
    if not has_mnav:
        return False
    # Allowed co-passengers (covered by navbar.js):
    # body.menu-open  → covered
    # @media          → fine
    # Allow-list: nothing else page-specific should be in this block
    FORBIDDEN = ['.hero', '.gallery', '.mv-', '.wa-widget', '#wa-',
                 '.section', '.card', '.property', '.brand']
    return not any(k in block_text for k in FORBIDDEN)


def process(src):
    # 1. Remove stale header HTML comments
    src = re.sub(r'<!--\s*={3,}.*?HEADER.*?=+\s*-->\s*', '', src)
    src = re.sub(r'<!--\s*MOBILE SHEET\s*-->\s*', '', src)

    # 2. Remove <style> blocks in <body> that are purely .mnav-* overrides
    #    (the body-only check: only after </head>)
    head_end = src.find('</head>')
    if head_end == -1:
        return src

    head_part = src[:head_end + len('</head>')]
    body_part = src[head_end + len('</head>'):]

    def strip_mnav_styles(text):
        result = []
        i = 0
        while i < len(text):
            m = re.search(r'<style[^>]*>', text[i:], re.I)
            if not m:
                result.append(text[i:])
                break
            result.append(text[i: i + m.start()])
            tag_start = i + m.start()
            end_m = re.search(r'</style\s*>', text[tag_start:], re.I)
            if not end_m:
                result.append(text[tag_start:])
                break
            tag_end = tag_start + end_m.end()
            block = text[tag_start:tag_end]
            if is_mnav_only_style(block):
                pass  # drop it
            else:
                result.append(block)
            i = tag_end
        return ''.join(result)

    body_cleaned = strip_mnav_styles(body_part)

    # 3. Collapse runs of 3+ blank lines → 2 blank lines
    body_cleaned = re.sub(r'\n{3,}', '\n\n', body_cleaned)

    return head_part + body_cleaned


base = os.path.dirname(os.path.abspath(__file__))
print('Second-pass cleanup...')
for page in PAGES:
    full = os.path.join(base, page)
    if not os.path.exists(full):
        print(f'  –  {page} (not found)')
        continue
    with open(full, 'r', encoding='utf-8') as f:
        src = f.read()
    cleaned = process(src)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    print(f'  ✓  {page}')
print('Done.')
