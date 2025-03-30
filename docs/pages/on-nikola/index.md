.. title: on nikola
.. slug: on-nikola
.. date: 2025-03-30 17:47:00 UTC-03:00
.. tags: meta, technical
.. link: on-nikola
.. description: some useful writing and references on the nikola static website builder

i tried using the auto builder, but either i did something wrong, or there is a bug with it.
nikola depends on the python package `watchdog` for the continuous auto-build.
i might try it again some other time.

for now, build is done with the following sequence of commands:

```bash
nikola check --clean-files
nikola build
nikola serve -b
```

the first line cleans up any files that no longer exist from the output directory (`docs`, [because github pages is unloved](https://rodigu.github.io/posts/setting-up/)).

new "tabs" can be added with through the `NAVIGATION_LINKS` variable in `conf.py` [^1].
here is what that variable looks like attow:

[^1]: as documented in [the nikola handbook on *customizing your site*](https://getnikola.com/handbook.html#customizing-your-site)

```py
NAVIGATION_LINKS = {
    DEFAULT_LANG: (
        ("/archive.html", "archive"),
        ("/categories/", "tags"),
        ("/rss.xml", "rss feed"),
        ("/pages/about/index.html", "about")
    ),
}
```
