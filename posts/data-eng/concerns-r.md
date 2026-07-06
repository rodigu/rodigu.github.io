<!--
.. title: some concerns with r
.. slug: concerns-with-r
.. date: 2026-07-05 19:53-03:00 UTC-03:00
.. tags: python, parquet, r
.. status: draft
.. category: data-eng
.. author: rodigu
.. link: https://rodigu.github.io/
.. description: r does not feel good to use
-->

there is some legacy code at work that uses r for etl.

i am having to work with r again, it has been a couple of years since i did that.
this is somewhere between a rant on technical debt and r (and its packages), and (yet another) warning on depencency hell.

<!-- TEASER_END -->

i do think r succeeds at its intended purpose: an analysis language for those with stats background, but little to no previous knowledge of programming.
it does not excel at much else, in my experience.

the legacy r scripts were created a while ago and don't really follow any software engineering best-practices.
some r scripts have over a fifteen hundred lines of code, featuring:

- comments with random numbers
- comments with dates
- dead code and imports
- 100-line sql scripts inside a string

it is not a pleasant base to work with, and i believe r was not intended for data engineering, it is fundamentally a language meant for analysis.

## the arrow package

arrow is a package used used in the aforementioned legacy code.
i have been incrementally transfering one of our r bases to airflow dags, slowly chipping at a thousand-line script.

while doing that, i found a bug that stumpped me by for a couple of hours. some numeric values were increasing more than 10 fold in the final dashboard consuming the data.

i eventually found out that arrow could not properly read any of the `Float16` columns i had been creating in `polars` with python.

this is the situation that initially drove me to write this post. and now i am recreating the bug to provide a minimal example of the problem.

## the r package manager

i did not have r installed in my personal laptop.
so i had to install it, along with arrow.

after 5 minutes of running the command to install arrow, it produced 70 kilobytes of logs, installed maybe a dozen different libraries, then got stuck at installing `arrow`. after 10 or so minutes, i figured it had crashed. i force-quit the script, and it yielded `there is no package called ‘arrow’`.

*why* did it not warn me before i force quit? no idea.

in any case, i will admit it was partially my own fault. as it turns out, `arrow` is not a part of the core r packages, and needs to be installed as not cran.

r builds the packages at install, and arrow was installed from a prebuilt binary. still, it took a while, longer than i have ever seen any package manager take.

it seems to me r is pretty slow from a development standpoint. i imagine having c-based packages make actual processing fast, but the dev experience has been a slog.

## a minimal example

create a polars dataframe with a `Float16` column:

```py
import polars as pl

df = pl.DataFrame(
    {"name": "john", "height": 1.78},
    schema={"name": pl.String, "height": pl.Float64},
).write_parquet("./data.parquet")

print(df)
```

attempting to read the same dataframe from r:

```r
library(arrow)

df <- read_parquet("./data.parquet")
print(df)
```

yields:

```
name height
1 john  16159
```

i tested with `Float32` and `Float64`, and both work fine. the issue is just with `Float16`.

## reporting the issue

right after finding this, i went on to try and report the issue. interestingly, r has a built-in function for listing the maintainer. using gave me a gmail for one jonathan keane, whom i am not sure i feel comfortable contacting directly.

fortunately, there is a github mirror for the package distribution. the r arrow package is actually an implementation of apache arrow for r.

i have opened the issue and am waiting on updates.
but this feels like such an oversight for a project of this dimension that i am led to believe i am doing something wrong.
