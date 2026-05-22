import os
import re
import shutil
from datetime import datetime, timezone
from xml.sax.saxutils import escape as xml_escape

import yaml
import markdown
from jinja2 import Environment, FileSystemLoader

ROOT = os.path.dirname(os.path.abspath(__file__))


def load_config():
    with open(os.path.join(ROOT, "build.conf")) as f:
        return yaml.safe_load(f)


def parse_metadata(text):
    """Parse Nikola-style metadata from markdown text.
    Supports both plain `.. key: value` and `<!-- .. key: value -->` wrapped formats.
    Returns (metadata, body_text).
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
                if key in metadata:
                    existing = metadata[key]
                    if isinstance(existing, list):
                        existing.append(val)
                    else:
                        metadata[key] = [existing, val]
                else:
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
                if key in metadata:
                    existing = metadata[key]
                    if isinstance(existing, list):
                        existing.append(val)
                    else:
                        metadata[key] = [existing, val]
                else:
                    metadata[key] = val
        body_text = "\n".join(lines[body_line:]).strip()
        return metadata, body_text

    return metadata, text.strip()


def parse_date(datestr):
    datestr = datestr.strip()
    if not datestr:
        return None
    try:
        datestr = re.sub(r'\s+UTC([+-]\d{2}:\d{2})', r' \1', datestr)
        return datetime.fromisoformat(datestr)
    except ValueError:
        try:
            return datetime.fromisoformat(datestr)
        except ValueError:
            return None


def parse_tags(tagstr):
    if not tagstr:
        return []
    return [t.strip() for t in tagstr.split(",") if t.strip()]


def parse_markdown(text, extensions, extension_configs):
    html = markdown.markdown(text, extensions=extensions, extension_configs=extension_configs)
    html = html.replace('<div class="code"><pre>', '<div class="code"><pre class="code">')
    return html


def adjust_rel_paths(html, src_depth, display_depth):
    """Rewrite relative image/href paths in HTML to work from a different page depth.
    
    src_depth: how many path segments deep the content was authored for
               (e.g. 3 for posts/cat/slug/)
    display_depth: how many path segments deep we're displaying it
               (e.g. 0 for index.html, 2 for categories/cat_foo/)
    """
    def fix(m):
        attr = m.group(1)
        path = m.group(2)
        if not path.startswith("../"):
            return m.group(0)
        levels = 0
        while path.startswith("../"):
            levels += 1
            path = path[3:]
        resolved = src_depth - levels
        need = display_depth - resolved
        if need > 0:
            prefix = "../" * need
        elif need == 0:
            prefix = "./"
        else:
            prefix = ""
        return f'{attr}="{prefix}{path}"'
    return re.sub(r'(src|href)="([^"]*)"', fix, html)


def get_slug_from_filename(filename):
    return os.path.splitext(filename)[0].replace("_", "-")


def get_title_from_body(text):
    m = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


def split_teaser(content):
    parts = content.split("<!-- TEASER_END -->", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return None, content.strip()


def relroot(depth):
    return "../" * depth if depth > 0 else "./"


def scan_files():
    config = load_config()
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

            with open(filepath) as f:
                raw = f.read()

            meta, body_text = parse_metadata(raw)
            body_html = parse_markdown(body_text, md_extensions, md_extension_configs)

            slug = meta.get("slug", get_slug_from_filename(fn))
            title = meta.get("title", get_title_from_body(body_text) or slug)
            description = meta.get("description", "")
            author = meta.get("author", config["site"]["author"])
            date = parse_date(meta.get("date", "")) if meta.get("date") else None
            tags = parse_tags(meta.get("tags", ""))
            status = meta.get("status", "")

            if status == "draft":
                continue

            if rel_dir == ".":
                output_path = f"pages/{slug}/index.html"
                canonical = f"/pages/{slug}/"
            else:
                output_path = f"pages/{rel_dir}/{slug}/index.html"
                canonical = f"/pages/{rel_dir}/{slug}/"

            page = {
                "title": title,
                "slug": slug,
                "author": author,
                "description": description,
                "date": date,
                "tags": tags,
                "content": body_html,
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

            with open(filepath) as f:
                raw = f.read()

            meta, body_text = parse_metadata(raw)
            body_html = parse_markdown(body_text, md_extensions, md_extension_configs)

            slug = meta.get("slug", get_slug_from_filename(fn))
            title = meta.get("title", get_title_from_body(body_text) or slug)
            description = meta.get("description", "")
            author = meta.get("author", config["site"]["author"])
            date = parse_date(meta.get("date", ""))
            tags = parse_tags(meta.get("tags", ""))
            category = meta.get("category", rel_path if rel_path != "." else "uncategorized")
            post_type = meta.get("type", "text")
            status = meta.get("status", "")

            if status == "draft":
                continue

            teaser, rest_content = split_teaser(body_html)

            output_path = f"posts/{category}/{slug}/index.html"
            canonical = f"/posts/{category}/{slug}/"

            post = {
                "title": title,
                "slug": slug,
                "author": author,
                "description": description,
                "date": date,
                "tags": tags,
                "category": category,
                "type": post_type,
                "content": body_html,
                "teaser": teaser,
                "output_path": output_path,
                "canonical": canonical,
                "url": f"posts/{category}/{slug}/",
            }
            posts.append(post)

    posts.sort(key=lambda p: p["date"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return pages, posts


def build():
    config = load_config()
    site = config["site"]

    env = Environment(
        loader=FileSystemLoader(os.path.join(ROOT, "templates")),
        autoescape=False,
    )

    out_dir = os.path.join(ROOT, config["output"])
    assets_css_src = os.path.join(ROOT, "assets", "css")
    assets_css_dst = os.path.join(out_dir, "assets", "css")
    files_src = os.path.join(ROOT, "files")
    images_src = os.path.join(ROOT, "images")
    images_dst = os.path.join(out_dir, config["image_folders"]["images"])

    # Clean output
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
        os.makedirs(images_dst, exist_ok=True)
        for fn in os.listdir(images_src):
            shutil.copy2(os.path.join(images_src, fn), os.path.join(images_dst, fn))

    # Scan source files
    print("Scanning pages and posts...")
    pages, posts = scan_files()

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

    def get_nav(active_label=None):
        return [
            {"url": item["url"], "label": item["label"], "active": item["label"] == active_label}
            for item in config["nav"]
        ]

    # --- Generate index page ---
    print("Generating index page...")
    index_posts = []
    for p in posts:
        out_depth = len(p["url"].split("/")) - 1
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

    tmpl = env.get_template("index.html")
    html = tmpl.render(base_vars, nav=get_nav(), relroot="./", canonical_path="/", posts=index_posts)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(html)

    # --- Generate post pages ---
    print("Generating posts...")
    for i, post in enumerate(posts):
        depth = len(post["url"].split("/")) - 1
        rr = relroot(depth)

        prev_post = posts[i + 1] if i + 1 < len(posts) else None
        next_post = posts[i - 1] if i - 1 >= 0 else None

        out_depth = len(post["url"].split("/")) - 1
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

        # Check if a nav item matches this post's category
        active_label = None
        for item in config["nav"]:
            nav_cat = item["label"]
            # Map nav labels to category names: "data" -> "data-eng", "reading" -> "reading" etc.
            # We check if the post's canonical path contains the nav item's URL path segment
            if nav_cat in post["canonical"]:
                active_label = nav_cat

        desc = post.get("description") or base_vars["description"]
        tmpl = env.get_template("post.html")
        html = tmpl.render(
            base_vars, nav=get_nav(active_label),
            relroot=rr, canonical_path=post["canonical"],
            title=post["title"], description=desc, post=post_data,
        )

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
        tmpl = env.get_template("page.html")
        html = tmpl.render(
            base_vars, nav=get_nav(),
            relroot=rr, canonical_path=page["canonical"],
            title=page["title"], description=desc, page=page_data,
        )

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
        tmpl = env.get_template("page.html")
        html = tmpl.render(
            base_vars, nav=get_nav(),
            relroot="./", canonical_path="/404.html",
            title=page_404["title"], description=desc, page=page_data,
        )
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

        tmpl = env.get_template("category.html")
        html = tmpl.render(
            base_vars, nav=get_nav(cat_name),
            relroot=rr, canonical_path=f"/categories/cat_{cat_name}/",
            title=f"Posts about {cat_name}", category=cat_name, posts=cat_post_list,
        )

        cat_out = os.path.join(out_dir, cat_dir_path)
        os.makedirs(cat_out, exist_ok=True)
        with open(os.path.join(cat_out, "index.html"), "w") as f:
            f.write(html)

    # --- Generate RSS feed ---
    print("Generating RSS feed...")
    rss_items = []
    for post in posts[:20]:
        out_depth = len(post["url"].split("/")) - 1
        raw_content = post["teaser"] if post["teaser"] else post["content"]
        content = adjust_rel_paths(raw_content, out_depth - 1, 0)
        rss_items.append(f"""  <item>
    <title>{xml_escape(post['title'])}</title>
    <link>{site['url']}/{post['url']}</link>
    <dc:creator>{xml_escape(post['author'])}</dc:creator>
    <description>{xml_escape(content)}</description>
    <guid>{site['url']}/{post['url']}</guid>
    <pubDate>{post['date'].strftime('%a, %d %b %Y %H:%M:%S %z') if post['date'] else ''}</pubDate>
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
