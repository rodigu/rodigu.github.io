## building

this site is built with a custom python script:

```bash
conda activate blog
python build.py
```

the script reads markdown files from `pages/` and `posts/`, renders them to html using
python-markdown with code highlighting, wraps them in jinja2 templates, and outputs
to the `docs/` directory (github pages deployment target).

### requirements

- python 3
- `markdown`, `jinja2`, `pyyaml`, `pygments` (available in the `blog` conda env)
