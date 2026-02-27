/* ============================================================
   navbar.js  –  Bliss Living shared navigation component
   Include once at the very start of <body> on every page:
     <script src="navbar.js"></script>
   ============================================================ */
(function () {

  /* ── 1. Inject CSS into <head> ─────────────────────────────────── */
  var css = [
    /* Reset bits that every nav needs */
    'a{text-decoration:none;color:inherit}',

    /* ── Floating header bar ── */
    'header{',
      'position:fixed;top:0;left:0;width:100%;z-index:1000;',
      'background:transparent;padding:10px 16px;',
      'transition:padding .25s cubic-bezier(.2,.7,.3,1);',
    '}',
    '.header-inner{',
      'max-width:1200px;margin:0 auto;padding:14px 28px;',
      'display:flex;align-items:center;gap:20px;',
      'background:rgba(255,255,255,.97);',
      'border:1px solid rgba(0,0,0,.06);border-radius:12px;',
      'box-shadow:0 14px 30px rgba(0,0,0,.12),0 4px 10px rgba(0,0,0,.08);',
      'backdrop-filter:saturate(140%) blur(6px);',
      'transition:box-shadow .25s cubic-bezier(.2,.7,.3,1);',
    '}',
    'header.scrolled{padding-top:6px;padding-bottom:6px}',
    'header.scrolled .header-inner{',
      'background:#fff;border-radius:10px;',
      'box-shadow:0 10px 24px rgba(0,0,0,.10),0 3px 8px rgba(0,0,0,.08);',
    '}',

    /* ── Logo ── */
    '.logo-block{',
      'font-family:"Times New Roman",Times,serif;font-size:20px;',
      'font-weight:700;color:#2d2c24;white-space:nowrap;',
    '}',
    '.logo-block a{text-decoration:none;color:inherit}',
    '.spacer{flex:1}',

    /* ── Desktop nav ── */
    '.main-nav ul{display:flex;list-style:none;gap:40px;margin:0;padding:0}',
    '.main-nav a{',
      'font-size:15px;font-weight:500;color:#363633;',
      'text-decoration:none;position:relative;padding-bottom:3px;',
    '}',
    '.main-nav a:hover{color:#6b6b50}',
    '.main-nav a:hover::after{',
      'content:"";position:absolute;left:0;bottom:0;',
      'width:100%;height:2px;background:#363633;',
    '}',

    /* ── Dropdowns ── */
    '.main-nav .has-dropdown{position:relative}',
    '.main-nav .has-dropdown .drop-panel{',
      'position:absolute;top:calc(100% + 10px);left:0;z-index:1002;',
      'display:none;min-width:210px;padding:14px 16px;',
      'background:#fff;border:1px solid rgba(0,0,0,.06);',
      'border-radius:12px;',
      'box-shadow:0 10px 24px rgba(0,0,0,.10),0 3px 8px rgba(0,0,0,.06);',
    '}',
    '.main-nav .has-dropdown:hover .drop-panel{display:block}',
    '.main-nav .loc-title{',
      'display:inline-block;font-weight:800;font-size:15px;',
      'margin:0 0 8px;padding-bottom:5px;border-bottom:3px solid #363633;color:#363633;',
    '}',
    '.main-nav .loc-list,.main-nav .menu-list{',
      'list-style:disc;padding-left:1.1rem;margin:0;',
    '}',
    '.main-nav .loc-list li,.main-nav .menu-list li{margin:6px 0;display:list-item}',
    '.main-nav .loc-list a,.main-nav .menu-list a{',
      'display:inline;font-weight:600;font-size:14px;color:#363633;white-space:nowrap;',
    '}',
    '.main-nav .loc-list a:hover,.main-nav .menu-list a:hover{color:#6b6b50}',
    '.main-nav .loc-list a:hover::after,.main-nav .menu-list a:hover::after{display:none}',

    /* ── Book Now button ── */
    '.book-now{margin-left:12px}',
    '.book-now a{',
      'background:#4b4b38;color:#fff;font-weight:600;font-size:15px;',
      'padding:10px 22px;border-radius:6px;display:inline-block;',
      'box-shadow:0 2px 6px rgba(0,0,0,.12);',
      'transition:transform .2s,box-shadow .2s,background .2s;',
    '}',
    '.book-now a:hover{background:#363626;transform:translateY(-1px);box-shadow:0 4px 10px rgba(0,0,0,.16)}',
    '.book-now a:hover::after{display:none}',

    /* ── Mobile hamburger button ── */
    '.mnav-btn{display:none}',
    '@media(max-width:768px){',
      '.main-nav,.book-now{display:none!important}',
      '.mnav-btn{',
        'display:grid;place-items:center;width:44px;height:44px;',
        'border:none;background:transparent;cursor:pointer;border-radius:0;box-shadow:none;',
      '}',
      '.mnav-btn span{display:block;width:22px;height:2px;background:#222;margin:4px 0;border-radius:2px}',
      '.mnav-btn:active{transform:scale(.98)}',
    '}',

    /* ── Mobile slide-in sheet ── */
    '.mnav-sheet{display:none;pointer-events:none;position:fixed;inset:0;z-index:1500}',
    '@media(max-width:768px){.mnav-sheet{display:block}}',
    '.mnav-backdrop{position:absolute;inset:0;background:rgba(0,0,0,.45);opacity:0;transition:opacity .25s}',
    '.mnav-panel{',
      'position:absolute;top:0;right:0;height:100%;width:min(92vw,420px);',
      'background:#fff;border-top-left-radius:16px;border-bottom-left-radius:16px;',
      'transform:translateX(100%);transition:transform .25s cubic-bezier(.4,0,.2,1);',
      'box-shadow:-10px 0 30px rgba(0,0,0,.25);',
      'display:flex;flex-direction:column;',
    '}',
    '.mnav-sheet.open{pointer-events:auto}',
    '.mnav-sheet.open .mnav-backdrop{opacity:1}',
    '.mnav-sheet.open .mnav-panel{transform:translateX(0)}',
    '.mnav-head{',
      'display:flex;align-items:center;justify-content:space-between;',
      'padding:18px 20px;border-bottom:1px solid #eee;',
      'position:sticky;top:0;background:#fff;z-index:1;',
    '}',
    '.mnav-brand{font-size:18px;font-weight:800;color:#2d2c24}',
    '.mnav-close{all:unset;font-size:28px;line-height:1;cursor:pointer;padding:4px 8px;border-radius:8px}',
    '.mnav-close:active{background:#f3f3f3}',
    '.mnav-body{',
      'flex:1 1 auto;overflow-y:auto;-webkit-overflow-scrolling:touch;',
      'overscroll-behavior:contain;',
      'padding:20px 20px calc(96px + env(safe-area-inset-bottom,0px));',
      'display:grid;gap:28px;',
    '}',
    '.mnav-group{display:grid;gap:4px}',
    '.mnav-label{font-size:12px;font-weight:800;color:#6b6b6b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}',
    '.mnav-item{display:block;padding:14px 0;font-size:16px;color:#111;text-decoration:none;border-bottom:1px solid #eee}',
    '.mnav-item:active{background:#f7f7f7}',
    '.mnav-cta{',
      'position:sticky;bottom:0;',
      'padding:12px 16px calc(12px + env(safe-area-inset-bottom,0px));',
      'background:#fff;border-top:1px solid rgba(0,0,0,.06);',
    '}',
    '.mnav-book{',
      'display:block;width:100%;text-align:center;',
      'background:#4b4b38;color:#fff!important;font-weight:800;font-size:16px;',
      'line-height:1;padding:16px 18px;border-radius:12px;border:0;',
      'box-shadow:0 10px 24px rgba(0,0,0,.12),0 2px 6px rgba(0,0,0,.08);',
      'text-decoration:none!important;transition:transform .06s ease,box-shadow .2s;',
    '}',
    '.mnav-book:hover{box-shadow:0 14px 30px rgba(0,0,0,.16)}',
    '.mnav-book:active{transform:translateY(1px)}',
    /* Hide WhatsApp FAB while the mobile sheet is open */
    '@media(max-width:768px){body.menu-open #wa-widget{display:none!important}}'
  ].join('');

  var styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  /* ── 2. Inject HTML before this <script> tag ───────────────────── */
  var html = [
    '<header>',
      '<div class="header-inner">',
        '<div class="logo-block"><a href="index.html">BLISS LIVING</a></div>',
        '<div class="spacer"></div>',
        '<nav class="main-nav" aria-label="Primary">',
          '<ul>',
            '<li class="has-dropdown">',
              '<a href="#">Locations <span>\u25be</span></a>',
              '<div class="drop-panel">',
                '<div class="loc-title">London</div>',
                '<ul class="loc-list">',
                  '<li><a href="property.html">Maida Vale</a></li>',
                  '<li><a href="property1.html">Paddington</a></li>',
                  '<li><a href="property2.html">Nine Elms</a></li>',
                  '<li><a href="property3.html">Kennington</a></li>',
                  '<li><a href="property4.html">Wimbledon</a></li>',
                '</ul>',
              '</div>',
            '</li>',
            '<li class="has-dropdown">',
              '<a href="#">Menu <span>\u25be</span></a>',
              '<div class="drop-panel">',
                '<ul class="menu-list">',
                  '<li><a href="faq.html">FAQs</a></li>',
                  '<li><a href="terms.html">Terms &amp; Conditions</a></li>',
                  '<li><a href="privacy.html">Privacy Policy</a></li>',
                '</ul>',
              '</div>',
            '</li>',
          '</ul>',
        '</nav>',
        '<div class="book-now"><a href="booknow.html">Book now</a></div>',
        '<button id="mnavBtn" class="mnav-btn" aria-label="Open menu" aria-expanded="false">',
          '<span></span><span></span><span></span>',
        '</button>',
      '</div>',
    '</header>',

    '<aside id="mnav" class="mnav-sheet" aria-hidden="true">',
      '<div class="mnav-backdrop"></div>',
      '<div class="mnav-panel" role="dialog" aria-modal="true">',
        '<div class="mnav-head">',
          '<div class="mnav-brand">BLISS LIVING</div>',
          '<button class="mnav-close" aria-label="Close menu">\u00d7</button>',
        '</div>',
        '<div class="mnav-body">',
          '<div class="mnav-group">',
            '<div class="mnav-label">Locations</div>',
            '<a class="mnav-item" href="property.html">Maida Vale</a>',
            '<a class="mnav-item" href="property1.html">Paddington</a>',
            '<a class="mnav-item" href="property2.html">Nine Elms</a>',
            '<a class="mnav-item" href="property3.html">Kennington</a>',
            '<a class="mnav-item" href="property4.html">Wimbledon</a>',
          '</div>',
          '<div class="mnav-group">',
            '<div class="mnav-label">Menu</div>',
            '<a class="mnav-item" href="faq.html">FAQs</a>',
            '<a class="mnav-item" href="terms.html">Terms &amp; Conditions</a>',
            '<a class="mnav-item" href="privacy.html">Privacy Policy</a>',
          '</div>',
        '</div>',
        '<div class="mnav-cta">',
          '<a class="mnav-book" href="booknow.html">Book now</a>',
        '</div>',
      '</div>',
    '</aside>'
  ].join('');

  document.currentScript.insertAdjacentHTML('beforebegin', html);

  /* ── 3. Wire up behaviour ───────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    /* Scroll → compact header */
    var header = document.querySelector('header');
    window.addEventListener('scroll', function () {
      if (header) header.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true });

    /* Mobile sheet open/close */
    var btn      = document.getElementById('mnavBtn');
    var sheet    = document.getElementById('mnav');
    if (!btn || !sheet) return;

    var closeBtn = sheet.querySelector('.mnav-close');
    var backdrop = sheet.querySelector('.mnav-backdrop');

    function openSheet() {
      sheet.classList.add('open');
      sheet.setAttribute('aria-hidden', 'false');
      btn.setAttribute('aria-expanded', 'true');
      document.body.classList.add('menu-open');
      document.body.style.overflow = 'hidden';
    }
    function closeSheet() {
      sheet.classList.remove('open');
      sheet.setAttribute('aria-hidden', 'true');
      btn.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('menu-open');
      document.body.style.overflow = '';
    }

    btn.addEventListener('click', openSheet);
    if (closeBtn) closeBtn.addEventListener('click', closeSheet);
    if (backdrop) backdrop.addEventListener('click', closeSheet);
    sheet.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', closeSheet);
    });
  });

}());
