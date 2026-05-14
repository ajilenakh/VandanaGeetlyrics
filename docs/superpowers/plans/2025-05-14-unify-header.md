# Replace Song Header with Universal Header

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the song-specific header and use the universal header on all pages, including song detail pages.

**Architecture:** The site currently uses a conditional header system in `base.njk` that switches between `header.njk` (universal) and `song-header.njk` (song-only) based on `headerType` frontmatter. We will remove this conditional and always use the universal header. The song-specific header file will be deleted.

**Tech Stack:** Eleventy 3.x, Nunjucks templates, vanilla CSS/JS

---

## Task 1: Update song.njk — Remove headerType frontmatter

**Files:**
- Modify: `src/_includes/layouts/song.njk`

- [ ] **Step 1: Update song.njk frontmatter**

```njk
---
layout: base.njk
---
```

The current `song.njk` has frontmatter with `layout: base.njk` and `headerType: song`. Remove the `headerType` line so it only has `layout: base.njk`.

**Before:**
```njk
---
layout: base.njk
headerType: song
---
```

**After:**
```njk
---
layout: base.njk
---
```

- [ ] **Step 2: Commit**

```bash
git add src/_includes/layouts/song.njk
git commit -m "refactor: remove headerType from song layout"
```

---

## Task 2: Update base.njk — Remove conditional header logic

**Files:**
- Modify: `src/_includes/layouts/base.njk`

- [ ] **Step 1: Remove conditional header include**

Find and remove the `{% if headerType == "song" %}` conditional block in `base.njk`.

**Before (lines 20-24):**
```njk
  {% if headerType == "song" %}
    {% include "components/song-header.njk" %}
  {% else %}
    {% include "components/header.njk" %}
  {% endif %}
```

**After:**
```njk
  {% include "components/header.njk" %}
```

- [ ] **Step 2: Commit**

```bash
git add src/_includes/layouts/base.njk
git commit -m "refactor: always use universal header on all pages"
```

---

## Task 3: Delete song-header.njk

**Files:**
- Delete: `src/_includes/components/song-header.njk`

- [ ] **Step 1: Delete the file**

```bash
rm src/_includes/components/song-header.njk
git add src/_includes/components/song-header.njk
git commit -m "refactor: delete song-header component, replaced by universal header"
```

---

## Task 4: Update CSS — Remove song-header styles

**Files:**
- Modify: `src/css/styles.css`

- [ ] **Step 1: Remove `.song-header` and related styles**

Remove the following CSS rules from `styles.css` (lines 277-301 approximately):

```css
/* Song Header */
.song-header {
  position: sticky;
  top: 0;
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border);
  padding: 0.75rem 1rem;
  z-index: 100;
  box-shadow: 0 2px 4px var(--shadow-sm);
}

.song-header-content {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.song-header-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
```

- [ ] **Step 2: Commit**

```bash
git add src/css/styles.css
git commit -m "refactor: remove .song-header CSS, no longer needed"
```

---

## Task 5: Verify the build

- [ ] **Step 1: Run build and check for errors**

```bash
pnpm build
```

Expected: Build completes without errors.

- [ ] **Step 2: Verify song pages load correctly**

Check that song detail pages (e.g., `/bengali/1/`) render with the universal header (same header as homepage and language list pages). The song page should show the home link and controls (theme toggle, A+/A-/Reset) in the header.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "verify: song pages use universal header"
```

---

## Self-Review Checklist

- [ ] `song.njk` no longer has `headerType: song` frontmatter
- [ ] `base.njk` always includes `components/header.njk`, no conditional
- [ ] `song-header.njk` deleted
- [ ] CSS `.song-header`, `.song-header-content`, `.song-header-controls` removed
- [ ] `pnpm build` completes without errors
- [ ] Song pages show the universal header (home link + controls)