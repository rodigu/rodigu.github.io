<!--
.. title: nikola post previews (teasers)
.. slug: post-teasers
.. date: 2026-02-14 13:00:09 UTC-03:00
.. tags: nikola
.. category: meta
.. link: 
.. description: creating post teasers on nikola
.. type: text
-->

took me a while, but i managed to figure out how to show a preview of a post instead of the whole post.

<!-- TEASER_END -->

you can do it with a markdown comment as such:

```md
<!-- TEASER_END -->
```

[this reference](https://adriaanrol.com/posts/2020/building-a-site-using-nikola/) by adriaanrol gave me the initial idea that i had to change the nikola `conf.py` file.

```py
# Show teasers (instead of full posts) in indexes? Defaults to False.
INDEX_TEASERS = True
```

but it was [this post](https://dev.to/mattioo/create-a-blog-using-nikola-static-website-generator-l71) by mattioo that showed me how to do it for markdown.
