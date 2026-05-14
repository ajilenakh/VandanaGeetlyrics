# Search & Navigation

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task.

**Goal:** Add a search box to language list pages (users come with a song number) and add a visible language switcher in the header so users can navigate between Bengali/Hindi/English without scrolling.

---

## Task 1: Add search to Bengali language page

**Files:**
- Modify: `src/bengali.njk`

- [ ] **Step 1: Add search input above song grid**

```njk
---
layout: base.njk
title: বাংলা গান
---

<div class="language-page">
  <h1 class="page-title">বাংলা গান</h1>

  <div class="search-box">
    <input
      type="search"
      id="song-search"
      class="search-input"
      placeholder="Search by number or title..."
      aria-label="Search songs"
    />
  </div>

  <div class="song-grid" id="song-grid">
    {% for song in collections.bengali %}
      <a href="/bengali/{{ song.fileSlug }}/" class="song-card" data-number="{{ song.data.number }}" data-title="{{ song.data.title | lower }}">
        <div class="song-card-content">
          <span class="song-card-number">{{ song.data.number }}</span>
          <h2 class="song-card-title">{{ song.data.title }}</h2>
          <svg class="song-card-arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </div>
      </a>
    {% endfor %}
  </div>

  <div id="no-results" class="no-results" style="display: none;">
    <p>We couldn't find that song. Try a different number.</p>
  </div>
</div>

<script src="/js/search.js" defer></script>
```

- [ ] **Step 2: Commit**

```bash
git add src/bengali.njk && git commit -m "feat: add search box to Bengali page"
```

---

## Task 2: Add search to Hindi language page

**Files:**
- Modify: `src/hindi.njk`

- [ ] **Step 1: Add search input above song grid**

Same structure as Bengali, using `collections.hindi`.

- [ ] **Step 2: Commit**

```bash
git add src/hindi.njk && git commit -m "feat: add search box to Hindi page"
```

---

## Task 3: Add search to English language page

**Files:**
- Modify: `src/english.njk`

- [ ] **Step 1: Add search input above song grid**

Same structure as Bengali, using `collections.english`.

- [ ] **Step 2: Commit**

```bash
git add src/english.njk && git commit -m "feat: add search box to English page"
```

---

## Task 4: Create search.js

**Files:**
- Create: `src/js/search.js`

- [ ] **Step 1: Write search functionality**

```js
// Search songs by number or title
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('song-search');
  const songGrid = document.getElementById('song-grid');
  const noResults = document.getElementById('no-results');
  const songCards = songGrid.querySelectorAll('.song-card');

  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    let visibleCount = 0;

    songCards.forEach((card) => {
      const number = card.getAttribute('data-number') || '';
      const title = card.getAttribute('data-title') || '';

      if (number.includes(query) || title.includes(query)) {
        card.style.display = '';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    noResults.style.display = visibleCount === 0 ? 'block' : 'none';
  });
});
```

- [ ] **Step 2: Commit**

```bash
git add src/js/search.js && git commit -m "feat: add client-side search for song list"
```

---

## Task 5: Add CSS for search box

**Files:**
- Modify: `src/css/styles.css`

- [ ] **Step 1: Add search styles**

```css
/* Search Box */
.search-box {
  margin-bottom: 1.5rem;
}

.search-input {
  width: 100%;
  padding: 1rem 1.25rem;
  font-size: 1.125rem;
  border: 2px solid var(--border);
  border-radius: 0.75rem;
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  outline: none;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  border-color: var(--accent);
}

.search-input::placeholder {
  color: var(--text-muted);
}

/* No results message */
.no-results {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
  font-size: 1.125rem;
}
```

- [ ] **Step 2: Commit**

```bash
git add src/css/styles.css && git commit -m "feat: add search box styles"
```

---

## Task 6: Add language switcher to header

**Files:**
- Modify: `src/_includes/components/header.njk`

- [ ] **Step 1: Add language navigation to header**

The AGENTS.md says "Visible, persistent navigation. The language switcher... must be visible on every page without scrolling."

```njk
<header class="header">
  <div class="header-content">
    <div class="header-left">
      <a href="/" class="home-link" aria-label="Home">
        <svg class="home-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 10.5L12 3l9 7.5"></path>
          <path d="M5 10v10h5v-6h4v6h5V10"></path>
        </svg>
      </a>
      <nav class="language-switcher" aria-label="Language navigation">
        <a href="/bengali/" class="lang-link">বাংলা</a>
        <a href="/hindi/" class="lang-link">हिंदी</a>
        <a href="/english/" class="lang-link">English</a>
      </nav>
    </div>
    <div class="header-controls">
      <button id="theme-toggle" class="control-button" aria-label="Toggle theme">
        <span class="icon-sun">☀️</span>
        <span class="icon-moon">🌙</span>
      </button>
      <button id="font-decrease" class="control-button" aria-label="Decrease font size">A-</button>
      <button id="font-increase" class="control-button" aria-label="Increase font size">A+</button>
      <button id="font-reset" class="control-button" aria-label="Reset font size">Reset</button>
    </div>
  </div>
</header>
```

- [ ] **Step 2: Commit**

```bash
git add src/_includes/components/header.njk && git commit -m "feat: add language switcher to header"
```

---

## Task 7: Add CSS for language switcher

**Files:**
- Modify: `src/css/styles.css`

- [ ] **Step 1: Add language switcher styles**

```css
.language-switcher {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.lang-link {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 0.375rem;
  transition: color 0.2s ease, background-color 0.2s ease;
}

.lang-link:hover {
  color: var(--text-primary);
  background-color: var(--bg-secondary);
}

/* Highlight current language */
.lang-link[aria-current="page"] {
  color: var(--accent);
  font-weight: 600;
}
```

- [ ] **Step 2: Commit**

```bash
git add src/css/styles.css && git commit -m "feat: add language switcher styles"
```

---

## Task 8: Highlight current language in switcher

**Files:**
- Modify: `src/bengali.njk`, `src/hindi.njk`, `src/english.njk`
- Or: Modify: `src/_includes/layouts/base.njk` to pass current language to header

- [ ] **Step 1: Set current language in frontmatter**

In each language page's frontmatter, add `currentLang: bengali` (or `hindi`, `english`).

Then in `header.njk`, add `aria-current="page"` to the link matching the current language.

**In header.njk:**
```njk
<nav class="language-switcher" aria-label="Language navigation">
  <a href="/bengali/" class="lang-link" {% if currentLang == "bengali" %}aria-current="page"{% endif %}>বাংলা</a>
  <a href="/hindi/" class="lang-link" {% if currentLang == "hindi" %}aria-current="page"{% endif %}>हिंदी</a>
  <a href="/english/" class="lang-link" {% if currentLang == "english" %}aria-current="page"{% endif %}>English</a>
</nav>
```

- [ ] **Step 2: Commit**

```bash
git add src/bengali.njk src/hindi.njk src/english.njk src/_includes/components/header.njk && git commit -m "feat: highlight current language in switcher"
```

---

## Task 9: Verify build

- [ ] **Step 1: Run build**

```bash
pnpm build
```

- [ ] **Step 2: Check output**

- Bengali page has search box, Hindi page has search box, English page has search box
- Header shows language switcher on all pages
- Language switcher highlights current language

- [ ] **Step 3: Commit**

```bash
git add -A && git commit -m "verify: search and language navigation complete"
```

---

## Self-Review

- [ ] Search box appears on Bengali, Hindi, English list pages
- [ ] Search works by song number or title
- [ ] "We couldn't find that song" message shows when no results
- [ ] Language switcher (বাংলা | हिंदी | English) appears in header
- [ ] Current language is highlighted with `aria-current="page"`
- [ ] Language switcher visible without scrolling (in sticky header)
- [ ] Build completes without errors