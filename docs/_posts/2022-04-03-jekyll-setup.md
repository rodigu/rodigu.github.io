---
layout: post
title: "Setting up Jekyll"
date: 2022-04-03 15:32:14 -0700
categories: jekyll update
---

Jekyll was not fun to setup.
Even after going through the motions, there is still an [issue](https://github.com/jekyll/jekyll/issues/8523) that has gone unsolved for
more than a year now, despite it seemingly affecting hundreds of users.

The bundle building command `bundle exec jekyll serve` gives out an error: ``require': cannot load such file -- webrick (LoadError)`.
Still, the solution is a one liner: `bundle add webrick`.

After trying for a couple of hours to setup a remote theme, it seems anything other than the default is out of the question.
