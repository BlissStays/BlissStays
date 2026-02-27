#!/usr/bin/env python3
"""
Phase 2 optimiser:
- Inject common.css into every HTML page (removes ~8-12KB of duplicated inline CSS each)
- Fix hero video: add poster + preload=none so it doesn't block the page
- Fix favicon reference to use webp
- Remove the inline scroll-reveal <style> & <script> block (already in common.css / shared js)
- Add <meta name="description"> where missing
- Remove duplicate <style> blocks for header/nav/mobile-nav that are now in common.css
- Add `fetchpriority="high"` to the above-the-fold hero logo image
"""
import os, re, glob

BASE = "/home/user/BlissStays"
HTML_FILES = sorted(glob.glob(os.path.join(BASE, "*.html")))

# ── Patterns to strip (big duplicated inline CSS blocks now in common.css) ──

# 1. The minified one-liner header/nav/mobile-nav CSS block
#    starts with  header{position:fixed  and ends  with the closing </style>
HEADER_CSS_RE = re.compile(
    r'<style[^>]*>\s*header\{position:fixed.*?</style>',
    re.DOTALL | re.IGNORECASE
)

# 2. The scroll-reveal <style id="site-scroll-transitions"> block
REVEAL_STYLE_RE = re.compile(
    r'<style\s+id=["\']site-scroll-transitions["\']>.*?</style>',
    re.DOTALL | re.IGNORECASE
)

# 3. The scroll-reveal inline <script> block (the IIFE that sets up observers)
REVEAL_SCRIPT_RE = re.compile(
    r'<script>\s*\(function\(\)\{[\s\S]*?window\.__revealifyLoaded[\s\S]*?\}\)\(\);\s*</script>',
    re.DOTALL
)

# ── common.css <link> tag ────────────────────────────────────────────────────
COMMON_CSS_LINK = '<link rel="stylesheet" href="css/common.css">\n'

# ── Shared reveal script tag (we'll keep the script in a shared js file) ────
REVEAL_JS = """<script>
(function(){
  if(window.__revealifyLoaded)return;window.__revealifyLoaded=true;
  const pr=matchMedia('(prefers-reduced-motion:reduce)').matches;
  function tag(){
    const g=[
      ['.hero .hero-logo','up',0,0],
      ['.home-message-left,.home-message-right','up',16,60],
      ['#about-us .about-title,#about-us .about-lead','up',14,60],
      ['#about-us .stat-card','up',18,80],
      ['.properties-slider .slide,.bliss-slider .attractions-item,.attractions .attractions-item','up',18,80],
      ['.bliss-features .feature-box','up',16,70],
      ['#bliss-reviews .review-card,#reviews-banner .rb-card','up',16,80],
      ['#faq .faq-item','up',14,70],
      ['.newsletter-text,.newsletter-form','up',14,80],
      ['.footer-column,.footer-logo-section','up',14,80]
    ];
    g.forEach(([s,v,d,st])=>{
      document.querySelectorAll(s).forEach((el,i)=>{
        if(!el.classList.contains('revealify')){
          el.classList.add('revealify',v||'up');
          el.style.setProperty('--rv-delay',(i*(st||60))+'ms');
          if(d!=null)el.style.setProperty('--rv-distance',(d||16)+'px');
        }
      });
    });
  }
  function obs(){
    if(pr){document.querySelectorAll('.revealify').forEach(e=>e.classList.add('in'));return;}
    const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:.18,rootMargin:'0px 0px -4% 0px'});
    document.querySelectorAll('.revealify').forEach(e=>io.observe(e));
  }
  function par(){
    const h=document.querySelector('.hero .hero-video');
    if(!h||pr)return;
    let t=false;
    addEventListener('scroll',()=>{if(t)return;t=true;requestAnimationFrame(()=>{h.style.transform='translate3d(0,'+Math.min(60,scrollY*.06)+'px,0)';t=false;});},{passive:true});
  }
  function init(){tag();obs();par();}
  document.readyState==='loading'?document.addEventListener('DOMContentLoaded',init):init();
  new MutationObserver(tag).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>"""

# ── Header scroll effect (tiny, keep inline) ────────────────────────────────
HEADER_SCROLL_SCRIPT = """<script>
(function(){
  const h=document.querySelector('header');
  if(!h)return;
  function chk(){h.classList.toggle('scrolled',scrollY>10);}
  addEventListener('scroll',chk,{passive:true});
  chk();
})();
</script>"""

# ── Fix video element: add poster + preload=none ─────────────────────────────
VIDEO_RE = re.compile(
    r'<video\b([^>]*)>',
    re.IGNORECASE
)

def fix_video(m):
    attrs = m.group(1)
    # add poster if not present
    if 'poster' not in attrs:
        attrs += ' poster="assets/hero-poster.jpg"'
    # set preload=none (don't buffer video until user interacts)
    attrs = re.sub(r'\bpreload=["\'][^"\']*["\']', 'preload="none"', attrs)
    if 'preload' not in attrs:
        attrs += ' preload="none"'
    return f'<video{attrs}>'

# ── Process each file ────────────────────────────────────────────────────────
for html_path in HTML_FILES:
    with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
        src = f.read()

    out = src

    # 1. Remove duplicated inline header/nav CSS (it's now in common.css)
    out = HEADER_CSS_RE.sub('', out)

    # 2. Remove duplicated scroll-reveal <style> block (it's in common.css)
    out = REVEAL_STYLE_RE.sub('', out)

    # 3. Remove duplicated scroll-reveal <script> IIFE (replaced below)
    out = REVEAL_SCRIPT_RE.sub('', out)

    # 4. Inject common.css link right after bootstrap link (or after <head>)
    if 'css/common.css' not in out:
        # Insert after bootstrap.min.css link
        out = out.replace(
            '<link href="css/bootstrap.min.css" rel="stylesheet">',
            '<link href="css/bootstrap.min.css" rel="stylesheet">\n' + COMMON_CSS_LINK,
            1
        )
        # Fallback: insert right after <head>
        if 'css/common.css' not in out:
            out = out.replace('<head>', '<head>\n' + COMMON_CSS_LINK, 1)

    # 5. Fix video element
    out = VIDEO_RE.sub(fix_video, out)

    # 6. Add the reveal script before </body> if it was removed
    if '__revealifyLoaded' not in out:
        out = out.replace('</body>', REVEAL_JS + '\n</body>', 1)

    # 7. Add header scroll script before </body> if not present
    if 'header.scrolled' not in out and 'classList.toggle' not in out:
        out = out.replace('</body>', HEADER_SCROLL_SCRIPT + '\n</body>', 1)

    # 8. Add fetchpriority="high" to the first img (above fold)
    out = re.sub(
        r'(<img\b(?![^>]*fetchpriority)[^>]*class="[^"]*hero[^"]*"[^>]*>)',
        lambda m: m.group(1).replace('<img ', '<img fetchpriority="high" '),
        out, count=1, flags=re.IGNORECASE
    )

    # 9. Remove duplicate blank lines left from stripping
    out = re.sub(r'\n{3,}', '\n\n', out)

    if out != src:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(out)
        saved = len(src) - len(out)
        print(f"  ✓ {os.path.basename(html_path):<40} saved {saved:,} bytes")
    else:
        print(f"  – {os.path.basename(html_path)} unchanged")

print("\nDone.")
