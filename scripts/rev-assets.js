#!/usr/bin/env node
/**
 * Asset revisioning script for VandanaGeetlyrics
 * Hashes CSS/JS files and updates HTML references for cache busting
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const SITE_DIR = '_site';

/**
 * Generate a short MD5 hash from file contents
 */
function getContentHash(filePath) {
  const content = fs.readFileSync(filePath);
  return crypto.createHash('md5').update(content).digest('hex').slice(0, 8);
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
            renameMap.set(`/${path.relative(SITE_DIR, fullPath).replace(/\\/g, '/')}`,
                          `/${path.relative(SITE_DIR, newPath).replace(/\\/g, '/')}`);
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

// Run if executed directly
if (require.main === module) {
  revAssets();
}

module.exports = { revAssets, getContentHash };