# Performance Cleanup

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task.

**Goal:** Clean up performance violations: remove Google Fonts CDN, remove page-load animation, prepare for inline critical CSS, and add content hashing for assets.

---

## Task 1: Remove Google Fonts external CDN

**Files:**
- Modify: `src/_includes/layouts/base.njk`

- [ ] **Step 1: Remove Google Fonts links**

Remove lines 15-17 from `base.njk`:
```njk
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap" rel="stylesheet">
```

The AGENTS.md explicitly says: "No web fonts from external CDNs. Use the system font stack only."

- [ ] **Step 2: Commit**

```bash
git add src/_includes/layouts/base.njk && git commit -m "perf: remove Google Fonts CDN (system font stack only)"
```

---

## Task 2: Remove page-load fade animation

**Files:**
- Modify: `src/css/styles.css`

- [ ] **Step 1: Remove animation from body**

The `body` has `opacity: 0; animation: pageFadeIn 0.3s ease forwards;` which violates the rule "No animations or transitions that delay seeing content."

Remove the `opacity: 0` and `animation` from body. The body should just render normally.

**Find in styles.css:**
```css
body {
  ...
  opacity: 0;
  animation: pageFadeIn 0.3s ease forwards;
}
```

**Change to:**
```css
body {
  ...
  opacity: 1;
}
```

Also remove the `@keyframes pageFadeIn` block (lines 124-134 approximately):
```css
/* Page Transitions */
@keyframes pageFadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add src/css/styles.css && git commit -m "perf: remove page-load animation that delays content"
```

---

## Task 3: Inline critical CSS in `<head>`

**Files:**
- Modify: `src/_includes/layouts/base.njk`
- Modify: `src/css/styles.css`

- [ ] **Step 1: Extract critical CSS**

The critical CSS includes:
- CSS variables (theme colors, fonts)
- Base reset (box-sizing, margin 0)
- Header styles (sticky header is above the fold)
- Container layout
- Body basic styles

Extract these into a `<style>` block in `<head>` of `base.njk`, then load the rest via `styles.css` with `preload`.

**Add in `<head>` after line 8:**
```njk
  <style>
    :root {
      --bg-primary: #f8f4ee;
      --bg-secondary: #fffaf3;
      --bg-tertiary: #f1e7d8;
      --text-primary: #1f1b16;
      --text-secondary: #6b6258;
      --accent: #e89a1c;
      --accent-hover: #d17f00;
      --border: #e4d7c4;
      --base-font-size: 18px;
    }
    [data-theme="dark"] {
      --bg-primary: #080808;
      --bg-secondary: #111111;
      --bg-tertiary: #1a1a1a;
      --text-primary: #f5f1ea;
      --text-secondary: #b8aa98;
      --accent: #f0a020;
      --accent-hover: #ffb43b;
      --border: #2a2118;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { font-size: var(--base-font-size); }
    body { font-family: system-ui, sans-serif; background-color: var(--bg-primary); color: var(--text-primary); min-height: 100vh; display: flex; flex-direction: column; }
    .header { position: sticky; top: 0; background-color: var(--bg-primary); border-bottom: 1px solid var(--border); padding: 0.75rem 1rem; z-index: 100; }
    .header-content { max-width: 800px; margin: 0 auto; display: flex; justify-content: space-between; }
    .container { max-width: 800px; margin: 0 auto; padding: 1rem; flex: 1; }
  </style>
```

- [ ] **Step 2: Commit**

```bash
git add src/_includes/layouts/base.njk && git commit -m "perf: inline critical CSS in head"
```

---

## Task 4: Add content hash to versioned assets

**Files:**
- Modify: `.eleventy.js`

- [ ] **Step 1: Add Eleventy transform for content hashing**

Add a transform that appends a content hash to CSS, JS, and asset filenames at build time. This enables long-lived cache headers.

```js
const crypto = require('crypto');
const path = require('path');
const fs = require('fs');

module.exports = function(eleventyConfig) {
  // ... existing config ...

  // Add content hash to versioned assets
  eleventyConfig.addTransform('cache-bust', function(content, outputPath) {
    if (!outputPath) return content;
    const ext = path.extname(outputPath);
    if (['.css', '.js', '.ico', '.png', '.jpg'].includes(ext)) {
      const fullPath = path.join(__dirname, '_site', outputPath);
      if (fs.existsSync(fullPath)) {
        const data = fs.readFileSync(fullPath);
        const hash = crypto.createHash('md5').update(data).digest('hex').slice(0, 8);
        const dir = path.dirname(outputPath);
        const base = path.basename(outputPath, ext);
        const newName = `${base}.${hash}${ext}`;
        const newPath = path.join(dir, newName);
        // Rename the file
        fs.renameSync(fullPath, path.join(__dirname, '_site', newPath));
        // Update the reference in HTML
        return content.replace(outputPath, newPath);
      }
    }
    return content;
  });

  return { /* existing config */ };
};
```

**Note:** This transform runs during build. After building, verify that `styles.css` references like `href="/css/styles.css"` are updated to include the hash (e.g., `href="/css/styles.a1b2c3d4.css"`).

- [ ] **Step 2: Commit**

```bash
git add .eleventy.js && git commit -m "perf: add content hash transform for versioned assets"
```

---

## Task 5: Verify build

- [ ] **Step 1: Run build and check**

```bash
pnpm build
```

Expected: Build completes, CSS/JS files have content hash in filename.

- [ ] **Step 2: Verify no Google Fonts references**

```bash
grep -r "fonts.googleapis.com\|fonts.gstatic.com" _site/
```

Expected: No results.

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "verify: performance cleanup complete"
```

---

## Self-Review

- [ ] No Google Fonts CDN links in HTML source
- [ ] No page-load animation delay (content visible immediately)
- [ ] Critical CSS inlined in `<head>`
- [ ] Asset filenames include content hash
- [ ] Build completes without errors