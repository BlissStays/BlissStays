/**
 * optimize-images.js
 * Converts all JPG/PNG images to WebP, resizes, and updates HTML references.
 * - Property photos (Property*, assets/): max 1200px wide, quality 82
 * - Icons/logos (icons/, prop icon/, flags/, logos/, root logos): max 150px wide, quality 85
 * - Root hero/content images: max 1200px wide, quality 82
 */

const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const BASE = __dirname;

// Folders where images are small icons → cap at 150px
const ICON_DIRS = new Set(['icons', 'prop icon', 'flags', 'logos']);

// Root-level filenames that are logos/icons → cap at 150px
const ROOT_ICON_FILES = new Set([
  'Bliss_Living.png', 'favicon.png', 'logo.png', 'logo123.png',
  'logowhite.png', 'wapp.png', 'Footnote_Logo.png',
]);

const PHOTO_MAX  = 1200;
const ICON_MAX   = 150;
const PHOTO_Q    = 82;
const ICON_Q     = 85;

function walkDir(dir, results = []) {
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); }
  catch { return results; }
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      // Skip node_modules
      if (e.name === 'node_modules') continue;
      walkDir(full, results);
    } else if (/\.(jpg|jpeg|png)$/i.test(e.name)) {
      results.push(full);
    }
  }
  return results;
}

function isIconPath(fullPath) {
  const rel  = path.relative(BASE, fullPath);
  const parts = rel.split(path.sep);
  // In an icon directory?
  if (ICON_DIRS.has(parts[0])) return true;
  // Root-level logo/icon file?
  if (parts.length === 1 && ROOT_ICON_FILES.has(parts[0])) return true;
  return false;
}

async function convertOne(srcPath) {
  const destPath = srcPath.replace(/\.(jpg|jpeg|png)$/i, '.webp');
  const icon = isIconPath(srcPath);
  const maxW  = icon ? ICON_MAX  : PHOTO_MAX;
  const qual  = icon ? ICON_Q    : PHOTO_Q;

  try {
    await sharp(srcPath)
      .resize(maxW, null, { withoutEnlargement: true, fit: 'inside' })
      .webp({ quality: qual, effort: 5 })
      .toFile(destPath);
    return destPath;
  } catch (err) {
    console.error(`  ✗ ${path.relative(BASE, srcPath)}: ${err.message}`);
    return null;
  }
}

async function main() {
  console.log('🔍 Scanning for images...');
  const all = walkDir(BASE);
  console.log(`   Found ${all.length} source images\n`);

  let done = 0, skipped = 0;
  for (const src of all) {
    const dest = src.replace(/\.(jpg|jpeg|png)$/i, '.webp');
    const rel  = path.relative(BASE, src);

    // Skip if webp already newer than source (already processed)
    if (fs.existsSync(dest)) {
      const srcMtime  = fs.statSync(src).mtimeMs;
      const destMtime = fs.statSync(dest).mtimeMs;
      if (destMtime >= srcMtime) {
        skipped++;
        continue;
      }
    }

    const result = await convertOne(src);
    if (result) {
      const srcSize  = fs.statSync(src).size;
      const destSize = fs.statSync(result).size;
      const saving   = Math.round((1 - destSize / srcSize) * 100);
      console.log(`  ✓ ${rel} → .webp  (${saving > 0 ? '-'+saving+'%' : '+'+Math.abs(saving)+'%'})`);
      done++;
    }
  }

  console.log(`\n✅ Converted ${done} images (${skipped} already up-to-date)\n`);
}

main().catch(console.error);
