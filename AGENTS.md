# AGENTS.md

## Overview

Personal website ("notas.") built with a custom Python static site generator.
Outputs to `docs/` for GitHub Pages deployment.

## Build

```bash
./.venv/bin/python build.py
```

- No CLI arguments — always does a full clean + rebuild
- Wipes `docs/` (preserving `.git` and `.nojekyll`) then regenerates everything
- Requires: Python 3, `pyyaml`, `markdown`, `jinja2`

## Project Structure

```
build.py          # Static site generator (single script)
build.conf        # Site config (YAML)
posts/            # Blog posts, organized by category subdirectory
pages/            # Static pages (about, cv, 404)
templates/        # Jinja2 templates (base, post, page, index, category)
assets/css/       # Stylesheets
images/           # Image assets
files/            # Static files copied to output root
docs/             # Generated output (GitHub Pages source)
```

## Content Conventions

### Frontmatter Format

Uses reST-style HTML comments:

```html
<!--
.. title: My Post Title
.. slug: my-post-title
.. date: 2025-01-15 10:00:00 UTC-03:00
.. tags: python, data
.. category: data-eng
.. description: A short summary.
-->
```

### Required Frontmatter Keys

| Key | Posts | Pages | Notes |
|-----|-------|-------|-------|
| `title` | ✓ | ✓ | |
| `slug` | ✓ | ✓ | URL-friendly identifier |
| `date` | ✓ | ✓ | Format: `YYYY-MM-DD HH:MM:SS UTC±HH:MM` |
| `tags` | ✓ | ✓ | Comma-separated (can be empty) |
| `description` | ✓ | ✓ | Can be empty |
| `category` | ✓ | ✗ | Must match parent directory name |

Optional: `link`, `author`, `status` (`draft`), `type` (`text`)

### File Naming

- Lowercase, hyphen-separated: `my-post-title.md`
- Posts live in `posts/<category>/` (e.g., `posts/data-eng/my-post.md`)
- Pages live in `pages/` (e.g., `pages/about.md`)

### Categories

Current categories: `data-eng`, `game-dev`, `linux`, `meta`, `music`, `photo-journal`, `reading`

Category is determined by the subdirectory under `posts/`.

## Templates

Jinja2 templates in `templates/`:

| Template | Purpose |
|----------|---------|
| `base.html` | Shell layout (header, nav, footer) |
| `post.html` | Single post (extends base) |
| `page.html` | Single page (extends base) |
| `index.html` | Home page / post listing |
| `category.html` | Category listing page |

### Key Template Variables

- `{{ title }}`, `{{ description }}`, `{{ site_title }}`
- `{{ post.title }}`, `{{ post.content }}`, `{{ post.date_formatted }}`
- `{{ post.tags }}`, `{{ post.prev }}`, `{{ post.next }}`
- `{{ nav }}` — list of `{url, label, active}`
- `{{ comments_repo }}` — utterances GitHub repo

## Styling

- CSS framework: hack.css (terminal aesthetic)
- Fonts: Share Tech Mono (body), Maple Mono (theme), Space Mono (code)
- Dark variant: `hack dark` class on body
- Color scheme: dark background, orange text, cyan code blocks
