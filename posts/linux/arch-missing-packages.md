.. title: missing packages on arch
.. slug: arch-missing-packages
.. date: 2026-02-05 22:41:00 UTC-03:00
.. tags: arch, linux
.. category: linux
.. author: rodigu
.. link: https://rodigu.github.io/
.. description:

i was trying to use pandoc with arch, but was getting an error when trying to convert a markdown to pdf.

conversion snippet:

```bash
pandoc document.md -o document.pdf
```

resulted in:

```text
Error producing PDF.
! LaTeX Error: File `xcolor.sty' not found.

Type X to quit or <RETURN> to proceed,
or enter new name. (Default extension: sty)

Enter file name: 
! Emergency stop.
<read *> 
         
l.7 \usepackage
```

to use pandoc you first need a tex engine, like texlive:

```bash
sudo pacman -S texlive
```

i installed only the ones that seemed relevant, as all packages amount to over 1 GB (??).

turns out, i was missing something.
[this reddit comment](https://www.reddit.com/r/archlinux/comments/n8vbyz/latex_packages_problem/){:target="_blank"} helped me out:

>If you want to figure out which one you need to install to get a certain LaTeX package, use for example `pacman -F bbm.sty`. You will need to run `pacman -Fy` once if you have never used `pacman -F` at all.

very good to know.
running it:

```bash
sudo pacman -F soul.sty
```

gave me:

```text
extra/texlive-plaingeneric 2025.2-3 (texlive)
    usr/share/texmf-dist/tex/generic/soul/soul.sty
```

which i just had to install with pacman.
