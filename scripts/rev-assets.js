#!/usr/bin/env node
/**
 * Asset revisioning script for VandanaGeetlyrics
 * Hashes CSS/JS files and updates HTML references for cache busting
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const cheerio = require('cheerio');

const SITE_DIR = '_site';
const PATH_PREFIX = (process.env.BASE_URL || '/').replace(/\/$/, '');

/**
 * Generate a short MD5 hash from file contents
 */
function getContentHash(filePath) {
  const content = fs.readFileSync(filePath);
  return crypto.createHash('sha256').update(content).digest('hex').slice(0, 8);
}

/**
 * Find all HTML files in the site directory
 */
function findHtmlFiles(dir, files = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      findHtmlFiles(fullPath, files);
    } else if (entry.name.endsWith('.html')) {
      files.push(fullPath);
    }
  }
  return files;
}

/**
 * Main revisioning logic
 */
function revAssets() {
  console.log('Starting asset revisioning...');

  // Directories to hash (CSS and JS only)
  const dirsToHash = [
    path.join(SITE_DIR, 'css'),
    path.join(SITE_DIR, 'js')
  ];

  // Track renamed files for HTML rewriting
  const renameMap = new Map();

  // Hash and rename files
  for (const dir of dirsToHash) {
    if (!fs.existsSync(dir)) {
      console.log(`Skipping ${dir} (does not exist)`);
      continue;
    }

    const files = fs.readdirSync(dir);
    for (const file of files) {
      const ext = path.extname(file);
      if (['.css', '.js'].includes(ext)) {
        // Skip service worker (must stay at original path for registration)
        if (file === 'sw.js') {
          console.log(`Skipping service worker: ${file}`);
          continue;
        }
        // Skip files that are already hashed (e.g., styles.abc12345.css)
        const hashPattern = /\.[a-f0-9]{8}\.(css|js)$/;
        if (hashPattern.test(file)) {
          console.log(`Skipping already-hashed: ${file}`);
          continue;
        }
        const fullPath = path.join(dir, file);
        const hash = getContentHash(fullPath);
        const baseName = path.basename(file, ext);
        const newName = `${baseName}.${hash}${ext}`;
        const newPath = path.join(dir, newName);

        if (file !== newName) {
          try {
            fs.renameSync(fullPath, newPath);
            // Map old path to new path for HTML rewriting
            const oldRelPath = '/' + path.relative(SITE_DIR, fullPath).replace(/\\/g, '/');
            const newRelPath = '/' + path.relative(SITE_DIR, newPath).replace(/\\/g, '/');
            renameMap.set(PATH_PREFIX + oldRelPath, PATH_PREFIX + newRelPath);
            console.log(`Renamed: ${file} -> ${newName}`);
          } catch (err) {
            console.error(`Failed to rename ${file}: ${err.message}`);
          }
        }
      }
    }
  }

  // Update HTML references
  const htmlFiles = findHtmlFiles(SITE_DIR);
  let htmlUpdated = 0;

  for (const htmlFile of htmlFiles) {
    let content = fs.readFileSync(htmlFile, 'utf-8');
    let modified = false;

    for (const [oldPath, newPath] of renameMap) {
      // Replace in href and src attributes
      const patterns = [
        new RegExp(`href=["']${escapeRegex(oldPath)}["']`, 'g'),
        new RegExp(`src=["']${escapeRegex(oldPath)}["']`, 'g')
      ];

      for (const pattern of patterns) {
        if (pattern.test(content)) {
          content = content.replace(pattern, (match) => {
            return match.replace(oldPath, newPath);
          });
          modified = true;
        }
      }
    }

    if (modified) {
      try {
        fs.writeFileSync(htmlFile, content, 'utf-8');
        htmlUpdated++;
        console.log(`Updated references in: ${htmlFile}`);
      } catch (err) {
        console.error(`Failed to update ${htmlFile}: ${err.message}`);
      }
    }
  }

  console.log(`\nAsset revisioning complete!`);
  console.log(`  - Renamed ${renameMap.size} asset(s)`);
  console.log(`  - Updated ${htmlUpdated} HTML file(s)`);

  // Verify CSP hashes match actual inline scripts
  verifyCspHashes();

  // Print summary of renamed assets for service worker update
  if (renameMap.size > 0) {
    console.log('\nRenamed assets:');
    for (const [oldPath, newPath] of renameMap) {
      console.log(`  ${oldPath} -> ${newPath}`);
    }
  }
}

/**
 * Escape special regex characters in a string
 */
function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Verify that CSP script-src hashes match the actual inline scripts in the built HTML.
 * Exit with error if mismatch detected (prevents silent CSP breakage).
 */
function verifyCspHashes() {
  const htmlFiles = findHtmlFiles(SITE_DIR);

  for (const file of htmlFiles) {
    const content = fs.readFileSync(file, 'utf-8');

    // Find CSP meta tag
    const cspMatch = content.match(
      /<meta\s+http-equiv="Content-Security-Policy"\s+content="([^"]+)">/
    );
    if (!cspMatch) continue;

    const cspContent = cspMatch[1];
    // Extract all sha256- hashes from script-src
    const hashRegex = /'sha256-([A-Za-z0-9+/=]+)'/g;
    let hashMatch;
    const expectedHashes = [];
    while ((hashMatch = hashRegex.exec(cspContent)) !== null) {
      expectedHashes.push(hashMatch[1]);
    }

    if (expectedHashes.length === 0) continue;

    // Find all inline <script> blocks (not external src) using an HTML parser
    const $ = cheerio.load(content, { decodeEntities: false });
    const scriptBlocks = [];
    $('script').each((_, el) => {
      if ($(el).attr('src') != null) return;
      scriptBlocks.push({ 1: $(el).html() || '' });
    });

    const actualHashes = scriptBlocks.map((m) => {
      const normalized = m[1].replace(/\r\n/g, '\n').replace(/\r/g, '\n');
      return crypto.createHash('sha256').update(normalized, 'utf-8').digest('base64');
    });

    // Check: every expected hash must match an actual script block and vice versa
    const expectedStr = expectedHashes.sort().join(',');
    const actualStr = actualHashes.sort().join(',');

    if (expectedStr !== actualStr) {
      console.error('\n❌ CSP HASH MISMATCH!');
      console.error(`  File: ${file}`);
      console.error(`  Expected (${expectedHashes.length}): ${expectedHashes.join(', ')}`);
      console.error(`  Actual (${actualHashes.length}): ${actualHashes.join(', ')}`);
      console.error(
        '  Update the CSP meta tag in base.njk with the corrected hashes.'
      );
      process.exit(1);
    }
  }

  console.log('  ✓ CSP script-src hashes verified');
}

// Run if executed directly
if (require.main === module) {
  revAssets();
}

module.exports = { revAssets, getContentHash };