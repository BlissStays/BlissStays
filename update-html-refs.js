/**
 * update-html-refs.js
 * Rewrites all HTML files to reference .webp instead of .jpg/.jpeg/.png
 * where a corresponding .webp file exists.
 * Handles paths with spaces (e.g. "prop icon/1.png", "WEB 1.jpg").
 * Skips: external URLs, favicon link tags.
 */

const fs   = require('fs');
const path = require('path');

const BASE = __dirname;

function getHtmlFiles(dir, results = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, e.name);
    if (e.isDirectory() && e.name !== 'node_modules') getHtmlFiles(full, results);
    else if (e.name.endsWith('.html')) results.push(full);
  }
  return results;
}

function webpExists(imgSrc, htmlPath) {
  if (/^https?:\/\/|^\/\/|^data:/.test(imgSrc)) return false;
  const abs  = path.resolve(path.dirname(htmlPath), imgSrc);
  const dest = abs.replace(/\.(jpg|jpeg|png)$/i, '.webp');
  return fs.existsSync(dest);
}

function toWebp(imgSrc) {
  return imgSrc.replace(/\.(jpg|jpeg|png)$/i, '.webp');
}

function processFile(htmlPath) {
  let html = fs.readFileSync(htmlPath, 'utf8');
  const original = html;

  const lines = html.split('\n');
  const updated = lines.map(line => {
    // Skip favicon <link> tags
    if (/<link[^>]+rel=["']?(shortcut\s+)?icon["']?/i.test(line)) return line;

    // Match double-quoted values containing a .jpg/.jpeg/.png path
    line = line.replace(/="([^"]+\.(jpg|jpeg|png))"/gi, (m, src) => {
      if (/^https?:\/\/|^\/\/|^data:/.test(src)) return m;
      return webpExists(src, htmlPath) ? `="${toWebp(src)}"` : m;
    });

    // Match single-quoted values
    line = line.replace(/='([^']+\.(jpg|jpeg|png))'/gi, (m, src) => {
      if (/^https?:\/\/|^\/\/|^data:/.test(src)) return m;
      return webpExists(src, htmlPath) ? `='${toWebp(src)}'` : m;
    });

    // Match CSS url() — with or without quotes
    line = line.replace(/url\(["']?([^"')]+\.(jpg|jpeg|png))["']?\)/gi, (m, src) => {
      if (/^https?:\/\/|^\/\/|^data:/.test(src)) return m;
      return webpExists(src, htmlPath) ? `url('${toWebp(src)}')` : m;
    });

    return line;
  });

  html = updated.join('\n');

  if (html !== original) {
    fs.writeFileSync(htmlPath, html, 'utf8');

    // Count how many .jpg/.jpeg/.png refs remain (excluding .webp)
    const before = (original.match(/\.(jpg|jpeg|png)['")\s>]/gi) || []).length;
    const after  = (html.match(/\.(jpg|jpeg|png)['")\s>]/gi) || []).length;
    const count  = before - after;
    const rel    = path.relative(BASE, htmlPath);
    console.log(`  ✓ ${rel} — ${count} reference${count !== 1 ? 's' : ''} updated`);
    return count;
  }
  return 0;
}

const htmlFiles = getHtmlFiles(BASE);
console.log(`📄 Updating ${htmlFiles.length} HTML files...\n`);

let totalRefs = 0, filesChanged = 0;
for (const f of htmlFiles) {
  const count = processFile(f);
  if (count > 0) { totalRefs += count; filesChanged++; }
}

console.log(`\n✅ Done — ${totalRefs} references updated across ${filesChanged} files`);

// Sanity check: how many .jpg/.png refs remain?
let remaining = 0;
for (const f of htmlFiles) {
  const content = fs.readFileSync(f, 'utf8');
  const lines = content.split('\n').filter(l => !/<link[^>]+rel=["']?(shortcut\s+)?icon/i.test(l));
  const text = lines.join('\n');
  const m = text.match(/\.(jpg|jpeg|png)['")\s>]/gi) || [];
  remaining += m.length;
}
console.log(`\n📊 Remaining .jpg/.png refs in HTML (excluding favicons): ${remaining}`);
