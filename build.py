import logging
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from typing import Any
from xml.sax.saxutils import escape as xml_escape

import yaml
import markdown
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s: %(message)s",
)
log = logging.getLogger("build")

ROOT = os.path.dirname(os.path.abspath(__file__))

REQUIRED_CONFIG_KEYS = {
    "site": ["title", "author", "email", "url", "description", "theme_color", "font", "variant", "footer"],
    "output": None,
    "image_folders": ["images"],
    "nav": None,
}


def load_config() -> dict[str, Any]:
    """Load and return the site configuration from build.conf.

    Returns:
        Parsed YAML configuration as a nested dict.
    """
    with open(os.path.join(ROOT, "build.conf")) as f:
        return yaml.safe_load(f)


def validate_config(config: dict[str, Any]) -> bool:
    """Validate that all required keys exist in config.

    Checks top-level keys and their expected subkeys against
    ``REQUIRED_CONFIG_KEYS``. Logs each missing key as an error
    and calls ``sys.exit(1)`` if any are missing.

    Args:
        config: Parsed YAML configuration dict.

    Returns:
        True if all required keys are present.

    Raises:
        SystemExit: If any required keys are missing.
    """
    errors = []
    for key, subkeys in REQUIRED_CONFIG_KEYS.items():
        if key not in config:
            errors.append(f"Missing required key: '{key}'")
            continue
        if subkeys is not None and isinstance(config[key], dict):
            for sub in subkeys:
                if sub not in config[key]:
                    errors.append(f"Missing required key: '{key}.{sub}'")
    if errors:
        for e in errors:
            log.error(e)
        sys.exit(1)
    return True


def parse_metadata(text: str) -> tuple[dict[str, str], str]:
    """Parse Nikola-style metadata from markdown text.

    Supports both plain ``.. key: value`` and
    ``<!-- .. key: value -->`` wrapped formats.

    Args:
        text: Raw markdown file content.

    Returns:
        A 2-tuple of (metadata, body_text) where metadata is a dict
        mapping lowercase keys to their string values, and body_text
        is the remaining content after the metadata block.
    """
    metadata = {}

    # Try HTML comment wrapped format: <!-- .. key: value -->
    m = re.match(r'^<!--\s*\n(.*?)\n-->', text, re.DOTALL)
    if m:
        block = m.group(1)
        body_text = text[m.end():].strip()
        for line in block.splitlines():
            line = line.strip()
            m2 = re.match(r'^\.\.\s+(\w+)\s*:\s*(.*)', line)
            if m2:
                key = m2.group(1).lower()
                val = m2.group(2).strip()
                metadata[key] = val
        return metadata, body_text

    # Try plain reST comment format: .. key: value
    lines = text.splitlines()
    meta_lines = []
    body_line = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^\.\.\s+\w+\s*:', stripped):
            meta_lines.append(stripped)
        else:
            body_line = i
            break

    if meta_lines:
        for line in meta_lines:
            m = re.match(r'^\.\.\s+(\w+)\s*:\s*(.*)', line)
            if m:
                key = m.group(1).lower()
                val = m.group(2).strip()
                metadata[key] = val
        body_text = "\n".join(lines[body_line:]).strip()
        return metadata, body_text

    return metadata, text.strip()


def parse_date(datestr: str) -> datetime | None:
    """Parse an ISO-format date string into a timezone-aware datetime.

    Handles ``UTC+HH:MM`` suffixes by converting them to standard
    ISO offset format. Naive datetimes are assigned UTC.

    Args:
        datestr: Date string in ISO 8601 format.

    Returns:
        A timezone-aware datetime, or None if the string is empty
        or cannot be parsed.
    """
    datestr = datestr.strip()
    if not datestr:
        return None
    try:
        datestr = re.sub(r'\s+UTC([+-]\d{2}:\d{2})', r' \1', datestr)
        dt = datetime.fromisoformat(datestr)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def parse_tags(tagstr: str) -> list[str]:
    """Split a comma-separated tag string into a list.

    Args:
        tagstr: Comma-separated tag string.

    Returns:
        List of stripped, non-empty tag strings.
    """
    if not tagstr:
        return []
    return [t.strip() for t in tagstr.split(",") if t.strip()]


def parse_markdown(text: str, extensions: list[str], extension_configs: dict[str, Any]) -> str:
    """Render markdown text to HTML with the configured extensions.

    Applies a post-processing fix to inject ``class="code"`` into
    codehilite output ``<pre>`` tags.

    Args:
        text: Raw markdown text.
        extensions: List of markdown extension names.
        extension_configs: Configuration dicts keyed by extension name.

    Returns:
        Rendered HTML string.
    """
    html = markdown.markdown(text, extensions=extensions, extension_configs=extension_configs)
    html = html.replace('<div class="code"><pre>', '<div class="code"><pre class="code">')
    return html


def adjust_rel_paths(html: str, src_depth: int, display_depth: int) -> str:
    """Rewrite relative image/href paths in HTML for a different page depth.

    Only paths starting with ``../`` are adjusted. All other paths
    are left untouched:

    - Absolute URLs (http://, https://, //)
    - Non-web schemes (mailto:, javascript:, tel:, data:)
    - Fragment-only links (#anchor)
    - Already-relative paths (images/foo.png)

    The depth convention counts directory segments, not filename
    segments. A URL like ``posts/cat/slug/`` has depth 3. The
    trailing slash is significant: ``posts/cat/slug`` would parse
    as depth 2, which is wrong. Callers must ensure the URL path
    ends with ``/`` before splitting.

    Args:
        html: HTML content containing src/href attributes.
        src_depth: Number of path segments deep the content was
            authored for (e.g. 3 for ``posts/cat/slug/``).
        display_depth: Number of path segments deep the content
            is being displayed (e.g. 0 for ``index.html``,
            2 for ``categories/cat_foo/``).

    Returns:
        HTML with adjusted relative paths.
    """
    # Schemes/protocols to skip (non-path href/src values)
    _SKIP_RE = re.compile(r'^(https?://|//|mailto:|javascript:|tel:|data:|#)', re.IGNORECASE)

    def fix(m: re.Match[str]) -> str:
        """Adjust a single src/href attribute value for the target depth.

        Args:
            m: Regex match with group(1) = attribute name and
               group(2) = the path value.

        Returns:
            The adjusted attribute string, or the original match
            if the path is not relative.
        """
        attr = m.group(1)
        path = m.group(2)

        # Skip non-relative paths: absolute URLs, scheme URIs, fragment-only
        if _SKIP_RE.match(path):
            return m.group(0)

        # Only adjust paths that start with ../ (the authored-relative-to-root convention)
        if not path.startswith("../"):
            return m.group(0)

        # Count how many ../ levels are in the path
        levels = 0
        while path.startswith("../"):
            levels += 1
            path = path[3:]

        # resolved = how many segments from root the original ../ pointed to
        # e.g. src_depth=3, levels=1 -> resolved=2 -> path was "../2segments/file"
        resolved = src_depth - levels

        # need = how many ../ to prepend so the path works from display_depth
        need = display_depth - resolved
        if need > 0:
            prefix = relroot(need)
        elif need == 0:
            prefix = relroot(0)
        else:
            prefix = ""
        return f'{attr}="{prefix}{path}"'

    return re.sub(r'(src|href)="([^"]*)"', fix, html)


def get_slug_from_filename(filename: str) -> str:
    """Derive a URL slug from a source filename.

    Convention: underscores in the filename stem are converted to hyphens.
    For example, ``my_cool_post.md`` becomes slug ``my-cool-post``.

    This keeps URLs readable and consistent with common web conventions.
    If a file already has an explicit ``slug`` metadata field, that value
    takes precedence (see ``parse_source_file``).
    """
    return os.path.splitext(filename)[0].replace("_", "-")


def get_title_from_body(text: str) -> str | None:
    """Extract a heading title from the first ``# Heading`` in markdown text.

    Args:
        text: Raw markdown text.

    Returns:
        The heading text without the ``#`` prefix, or None if no
        top-level heading is found.
    """
    m = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def split_teaser(content: str) -> tuple[str | None, str]:
    """Split rendered HTML at a ``<!-- TEASER_END -->`` marker.

    Args:
        content: Rendered HTML content.

    Returns:
        A 2-tuple of (teaser, rest). If the marker is present, teaser
        is the HTML before it and rest is the HTML after. If absent,
        teaser is None and rest is the full content.
    """
    parts = content.split("<!-- TEASER_END -->", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return None, content.strip()


def relroot(depth: int) -> str:
    """Return a relative path prefix that navigates up *depth* directories.

    Args:
        depth: Number of directory levels to go up.

    Returns:
        ``"../"`` repeated *depth* times, or ``"./"`` if depth is 0.
    """
    return "../" * depth if depth > 0 else "./"


def parse_source_file(
    filepath: str,
    config: dict[str, Any],
    md_extensions: list[str],
    md_extension_configs: dict[str, Any],
) -> dict[str, Any] | None:
    """Parse a markdown source file and extract common metadata.

    Reads the file, parses its metadata block, renders the body to
    HTML, and returns a dict of extracted fields. Skips files with
    ``status: draft``.

    Args:
        filepath: Absolute path to the markdown file.
        config: Site configuration dict (used for default author).
        md_extensions: List of markdown extension names.
        md_extension_configs: Configuration for markdown extensions.

    Returns:
        A dict with keys ``meta``, ``body_text``, ``body_html``,
        ``slug``, ``title``, ``description``, ``author``, ``date",
        and ``tags``, or None if the file is a draft or cannot
        be read/parsed.
    """
    try:
        with open(filepath) as f:
            raw = f.read()

        meta, body_text = parse_metadata(raw)
        body_html = parse_markdown(body_text, md_extensions, md_extension_configs)
    except Exception as e:
        log.error(f"Error reading/parsing '{filepath}': {e}")
        return None

    status = meta.get("status", "")
    if status == "draft":
        return None

    slug = meta.get("slug", get_slug_from_filename(os.path.basename(filepath)))
    title = meta.get("title", get_title_from_body(body_text) or slug)
    description = meta.get("description", "")
    author = meta.get("author", config["site"]["author"])
    date = parse_date(meta.get("date", ""))
    tags = parse_tags(meta.get("tags", ""))

    return {
        "meta": meta,
        "body_text": body_text,
        "body_html": body_html,
        "slug": slug,
        "title": title,
        "description": description,
        "author": author,
        "date": date,
        "tags": tags,
    }


def scan_files(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Scan pages/ and posts/ directories for markdown source files.

    Walks the directory tree, parses each markdown file via
    ``parse_source_file``, and builds page/post dicts. Posts are
    sorted by date (newest first).

    Args:
        config: Site configuration dict.

    Returns:
        A 2-tuple of (pages, posts) where each is a list of dicts
        containing the parsed content and metadata.
    """
    md_ext = [".md", ".mdown", ".markdown"]
    md_extensions = [
        "markdown.extensions.fenced_code",
        "markdown.extensions.codehilite",
        "markdown.extensions.extra",
    ]
    md_extension_configs = {
        "markdown.extensions.codehilite": {"css_class": "code"},
    }

    pages = []
    posts = []

    # Scan pages/
    pages_dir = os.path.join(ROOT, "pages")
    for dirpath, dirnames, filenames in os.walk(pages_dir):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() not in md_ext:
                continue
            filepath = os.path.join(dirpath, fn)
            rel_dir = os.path.relpath(dirpath, pages_dir)

            parsed = parse_source_file(filepath, config, md_extensions, md_extension_configs)
            if parsed is None:
                continue

            slug = parsed["slug"]
            if rel_dir == ".":
                output_path = f"pages/{slug}/index.html"
                canonical = f"/pages/{slug}/"
            else:
                output_path = f"pages/{rel_dir}/{slug}/index.html"
                canonical = f"/pages/{rel_dir}/{slug}/"

            page = {
                "title": parsed["title"],
                "slug": slug,
                "author": parsed["author"],
                "description": parsed["description"],
                "date": parsed["date"],
                "tags": parsed["tags"],
                "content": parsed["body_html"],
                "output_path": output_path,
                "canonical": canonical,
            }
            pages.append(page)

    # Scan posts/
    posts_dir = os.path.join(ROOT, "posts")
    for dirpath, dirnames, filenames in os.walk(posts_dir):
        if os.path.basename(dirpath) == "images":
            continue
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() not in md_ext:
                continue
            filepath = os.path.join(dirpath, fn)
            rel_path = os.path.relpath(dirpath, posts_dir)

            parsed = parse_source_file(filepath, config, md_extensions, md_extension_configs)
            if parsed is None:
                continue

            meta = parsed["meta"]
            slug = parsed["slug"]
            category = meta.get("category", rel_path if rel_path != "." else "uncategorized")
            post_type = meta.get("type", "text")

            teaser, rest_content = split_teaser(parsed["body_html"])

            output_path = f"posts/{category}/{slug}/index.html"
            canonical = f"/posts/{category}/{slug}/"

            post = {
                "title": parsed["title"],
                "slug": slug,
                "author": parsed["author"],
                "description": parsed["description"],
                "date": parsed["date"],
                "tags": parsed["tags"],
                "category": category,
                "type": post_type,
                "content": parsed["body_html"],
                "teaser": teaser,
                "output_path": output_path,
                "canonical": canonical,
                "url": f"posts/{category}/{slug}/",
            }
            posts.append(post)

    posts.sort(key=lambda p: p["date"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return pages, posts


def build() -> None:
    """Build the static site from markdown sources.

    Orchestrates the full build pipeline:

    1. Load and validate configuration.
    2. Clean the output directory and copy static assets.
    3. Scan and parse all pages and posts.
    4. Render index, post, page, 404, and category templates.
    5. Generate the RSS feed.

    Raises:
        SystemExit: If configuration is invalid or the index
            template fails to render.
    """
    config = load_config()
    site = config["site"]

    env = Environment(
        loader=FileSystemLoader(os.path.join(ROOT, "templates")),
        autoescape=False,
    )

    validate_config(config)

    out_dir = os.path.join(ROOT, config["output"])
    assets_css_src = os.path.join(ROOT, "assets", "css")
    assets_css_dst = os.path.join(out_dir, "assets", "css")
    files_src = os.path.join(ROOT, "files")
    images_src = os.path.join(ROOT, "images")
    images_dst = os.path.join(out_dir, config["image_folders"]["images"])

    # Clean output (with safety guard)
    out_dir_real = os.path.realpath(out_dir)
    root_real = os.path.realpath(ROOT)
    if not out_dir_real.startswith(root_real + os.sep) and out_dir_real != root_real:
        log.error(f"Output directory '{out_dir}' is not inside project root '{ROOT}'. Aborting.")
        sys.exit(1)
    if out_dir_real in ("/", os.path.expanduser("~")):
        log.error(f"Output directory '{out_dir}' resolves to a dangerous path '{out_dir_real}'. Aborting.")
        sys.exit(1)

    print("Cleaning output directory...")
    for entry in os.listdir(out_dir):
        path = os.path.join(out_dir, entry)
        if entry in (".git", ".nojekyll"):
            continue
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    # Copy static assets
    print("Copying static assets...")
    os.makedirs(assets_css_dst, exist_ok=True)
    for fn in os.listdir(assets_css_src):
        shutil.copy2(os.path.join(assets_css_src, fn), os.path.join(assets_css_dst, fn))

    if os.path.isdir(files_src):
        for fn in os.listdir(files_src):
            fp = os.path.join(files_src, fn)
            if os.path.isfile(fp):
                shutil.copy2(fp, os.path.join(out_dir, fn))
            elif os.path.isdir(fp):
                shutil.copytree(fp, os.path.join(out_dir, fn), dirs_exist_ok=True)

    if os.path.isdir(images_src):
        shutil.copytree(images_src, images_dst, dirs_exist_ok=True)

    # Scan source files
    print("Scanning pages and posts...")
    pages, posts = scan_files(config)

    # Build category index
    categories = {}
    for post in posts:
        cat = post["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(post)

    # Shared template vars
    footer_text = site["footer"].format(
        year=datetime.now().year, email=site["email"], author=site["author"]
    )

    base_vars = {
        "site_title": site["title"],
        "description": site["description"],
        "theme_color": site["theme_color"],
        "font": site["font"],
        "variant": site["variant"],
        "footer": footer_text,
        "site_url": site["url"],
        "site_author": site["author"],
        "comments_repo": config.get("comments", {}).get("repo", ""),
    }

    # Build explicit mapping from category names to nav labels
    # Extract category from nav URLs like "categories/cat_data-eng/" -> "data-eng"
    category_to_nav_label = {}
    for item in config["nav"]:
        url = item["url"]
        m = re.match(r'^categories/cat_([^/]+)/?$', url)
        if m:
            cat_name = m.group(1)
            category_to_nav_label[cat_name] = item["label"]

    # Snapshot nav list to avoid closing over mutable config state
    nav_snapshot = list(config["nav"])

    def get_nav(active_label: str | None = None) -> list[dict[str, Any]]:
        """Build the nav items list with an optional active highlight.

        Args:
            active_label: Nav label to mark as active, or None.

        Returns:
            List of dicts with keys ``url``, ``label``, and ``active``.
        """
        return [
            {"url": item["url"], "label": item["label"], "active": item["label"] == active_label}
            for item in nav_snapshot
        ]

    # --- Generate index page ---
    print("Generating index page...")
    index_posts = []
    for p in posts:
        # Ensure trailing slash so split counts directory segments correctly
        url = p["url"].rstrip('/') + '/'
        out_depth = len(url.split('/')) - 1
        src_depth = out_depth - 1
        content = adjust_rel_paths(p["content"], src_depth, 0)
        teaser = adjust_rel_paths(p["teaser"], src_depth, 0) if p["teaser"] else None
        index_posts.append({
            "title": p["title"],
            "author": p["author"],
            "date_iso": p["date"].isoformat() if p["date"] else "",
            "date_formatted": p["date"].strftime("%Y-%m-%d %H:%M") if p["date"] else "",
            "url": p["url"],
            "type": p["type"],
            "content": content,
            "teaser": teaser,
        })

    try:
        tmpl = env.get_template("index.html")
        html = tmpl.render(base_vars, nav=get_nav(), relroot=relroot(0), canonical_path="/", posts=index_posts)
    except Exception as e:
        log.error(f"Error rendering index template: {e}")
        sys.exit(1)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(html)

    # --- Generate post pages ---
    print("Generating posts...")
    for i, post in enumerate(posts):
        # Ensure trailing slash so split counts directory segments correctly
        url = post["url"].rstrip('/') + '/'
        depth = len(url.split('/')) - 1
        rr = relroot(depth)

        prev_post = posts[i + 1] if i + 1 < len(posts) else None
        next_post = posts[i - 1] if i - 1 >= 0 else None

        out_depth = depth
        src_depth = out_depth - 1
        adjusted_content = adjust_rel_paths(post["content"], src_depth, out_depth)

        post_data = {
            "title": post["title"],
            "author": post["author"],
            "content": adjusted_content,
            "date_iso": post["date"].isoformat() if post["date"] else "",
            "date_formatted": post["date"].strftime("%Y-%m-%d %H:%M") if post["date"] else "",
            "tags": post["tags"],
            "description": post["description"],
            "type": post["type"],
            "prev": {"url": prev_post["url"], "title": prev_post["title"]} if prev_post else None,
            "next": {"url": next_post["url"], "title": next_post["title"]} if next_post else None,
        }

        # Check if a nav item matches this post's category exactly
        active_label = category_to_nav_label.get(post["category"])

        desc = post.get("description") or base_vars["description"]
        try:
            tmpl = env.get_template("post.html")
            html = tmpl.render(
                base_vars, nav=get_nav(active_label),
                relroot=rr, canonical_path=post["canonical"],
                title=post["title"], description=desc, post=post_data,
            )
        except Exception as e:
            log.error(f"Error rendering post '{post.get('title', post.get('slug', '?'))}': {e}")
            continue

        out_path = os.path.join(out_dir, post["output_path"])
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            f.write(html)

    # --- Generate page files ---
    print("Generating pages...")
    for page in pages:
        if page["slug"] == "404":
            continue

        depth = page["canonical"].count("/") - 1
        rr = relroot(depth)

        page_data = {
            "title": page["title"],
            "author": page["author"],
            "content": page["content"],
            "description": page["description"],
            "date_iso": page["date"].isoformat() if page["date"] else "",
            "tags": page["tags"],
        }

        desc = page.get("description") or base_vars["description"]
        try:
            tmpl = env.get_template("page.html")
            html = tmpl.render(
                base_vars, nav=get_nav(),
                relroot=rr, canonical_path=page["canonical"],
                title=page["title"], description=desc, page=page_data,
            )
        except Exception as e:
            log.error(f"Error rendering page '{page.get('title', page.get('slug', '?'))}': {e}")
            continue

        out_path = os.path.join(out_dir, page["output_path"])
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            f.write(html)

    # --- Generate 404 page ---
    page_404 = next((p for p in pages if p["slug"] == "404"), None)
    if page_404:
        page_data = {
            "title": page_404["title"],
            "author": page_404["author"],
            "content": page_404["content"],
            "description": page_404["description"],
            "date_iso": page_404["date"].isoformat() if page_404["date"] else "",
            "tags": page_404["tags"],
        }
        desc = page_404.get("description") or base_vars["description"]
        try:
            tmpl = env.get_template("page.html")
            html = tmpl.render(
                base_vars, nav=get_nav(),
                relroot=relroot(0), canonical_path="/404.html",
                title=page_404["title"], description=desc, page=page_data,
            )
        except Exception as e:
            log.error(f"Error rendering 404 page: {e}")
        else:
            out_path = os.path.join(out_dir, "404.html")
            with open(out_path, "w") as f:
                f.write(html)

    # --- Generate category pages ---
    print("Generating category pages...")
    for cat_name, cat_posts in categories.items():
        cat_posts_sorted = sorted(
            cat_posts,
            key=lambda p: p["date"] or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )

        cat_dir_path = f"categories/cat_{cat_name}/"
        depth = len(cat_dir_path.split("/")) - 1
        rr = relroot(depth)

        cat_post_list = [
            {
                "title": p["title"],
                "date_iso": p["date"].isoformat() if p["date"] else "",
                "date_formatted": p["date"].strftime("%Y-%m-%d %H:%M") if p["date"] else "",
                "url": p["url"],
            }
            for p in cat_posts_sorted
        ]

        try:
            tmpl = env.get_template("category.html")
            html = tmpl.render(
                base_vars, nav=get_nav(category_to_nav_label.get(cat_name, cat_name)),
                relroot=rr, canonical_path=f"/categories/cat_{cat_name}/",
                title=f"Posts about {cat_name}", category=cat_name, posts=cat_post_list,
            )
        except Exception as e:
            log.error(f"Error rendering category page '{cat_name}': {e}")
            continue

        cat_out = os.path.join(out_dir, cat_dir_path)
        os.makedirs(cat_out, exist_ok=True)
        with open(os.path.join(cat_out, "index.html"), "w") as f:
            f.write(html)

    # --- Generate RSS feed ---
    print("Generating RSS feed...")
    rss_items = []
    dated_posts = [p for p in posts if p['date'] is not None]
    for post in dated_posts[:20]:
        # Ensure trailing slash so split counts directory segments correctly
        url = post["url"].rstrip('/') + '/'
        out_depth = len(url.split('/')) - 1
        raw_content = post["teaser"] if post["teaser"] else post["content"]
        content = adjust_rel_paths(raw_content, out_depth - 1, 0)
        safe_content = content.replace(']]>', ']]]]><![CDATA[>')
        rss_items.append(f"""  <item>
    <title>{xml_escape(post['title'])}</title>
    <link>{site['url']}/{post['url']}</link>
    <dc:creator>{xml_escape(post['author'])}</dc:creator>
    <description><![CDATA[{safe_content}]]></description>
    <guid>{site['url']}/{post['url']}</guid>
    <pubDate>{post['date'].strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>
  </item>""")

    rss_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{xml_escape(site['title'])}</title>
    <link>{site['url']}/</link>
    <description>{xml_escape(site['description'])}</description>
    <atom:link href="{site['url']}/rss.xml" rel="self" type="application/rss+xml"/>
    <language>en</language>
    <lastBuildDate>{datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')}</lastBuildDate>
{chr(10).join(rss_items)}
  </channel>
</rss>"""

    with open(os.path.join(out_dir, "rss.xml"), "w") as f:
        f.write(rss_xml)

    print(f"\nBuild complete! Output in '{config['output']}/'")


if __name__ == "__main__":
    build()
