.. title: setting up
.. slug: setting-up
.. date: 2025-03-30 16:20:00 UTC-03:00
.. tags: meta, blog
.. author: rodigu
.. link: https://rodigu.github.io/
.. description: setting up the blog
.. category: technical

looking at the [commit history](https://github.com/rodigu/rodigu.github.io/commits/master/) for the repository
containing the source for this blog, you may notice that this was originally my personal website/cv.

my initial intention was to setup the present blog on a separate branch,
but i forgot to switch branches before deleting everything.

in any case, i suppose i'll have to commit to this now so here is a test post.

![a photo i took while biking in chicago](../../images/2025-03-30_16-37_chicago-skyline-biking.png)

originally, i attempted to use jekyll [^1], at it is already integrated into github.
however, after some frustration (as had happened years ago when i tried it),
i decided to look for a different blog building tool.

[^1]: [the jekyll website](https://jekyllrb.com/)

one of my main points of contention with jekyll is that is uses ruby, which i am entirelly unfamiliar with.
therefore, i went searching for a tool that allowed me to stay within what i alredy know (namely, python),
and had built-in markdown support.

i also want it to be doing most of the work.
i am not too interested in messing with templates and such at the moment.
all i want is to get started on throwing stuff out there.

so i landed on nikola [^2] for static site generation.
it even has built'in support for extended markdown seeing that the footnotes are working nicely.


[^2]: [the nikola website](https://getnikola.com/)
