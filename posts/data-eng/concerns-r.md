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

we have some legacy r code at work that handles etl. while migrating it to airflow, i found a bug in the `arrow` package: it silently corrupts `Float16` columns read from parquet files. numeric values were off by more than 10x in production dashboards, and it took hours to trace back to the source.

<!-- TEASER_END -->

this is part rant about r, part rant about technical debt. i do think r succeeds at its intended purpose: an analysis language for those with stats background, but little to no previous knowledge of programming. it does not excel at much else.

the legacy r scripts were created a while ago and don't really follow any software engineering best-practices.
some r scripts have over a fifteen hundred lines of code, featuring:

- comments with random numbers
- comments with dates
- dead code and imports
- 100-line sql scripts inside a string

it is not a pleasant base to work with, and i believe r was not intended for data engineering, it is fundamentally a language meant for analysis.

## the arrow package

i have been incrementally migrating one of our r codebases to airflow dags, slowly chipping at a thousand-line script that uses `arrow` for reading parquet files.

while doing that, i found the bug mentioned in the intro. some numeric values were increasing more than 10 fold in the final dashboard. i eventually traced it to `arrow` not properly reading `Float16` columns created by `polars` in python.

below is a minimal reproduction.

## the r package manager

`arrow` is not part of core r packages and needs to be installed separately. on my laptop, the install produced 70 kilobytes of logs, pulled in a dozen dependencies, then hung for 10+ minutes before i killed it. the error message was `there is no package called 'arrow'`, no warning that the install had failed.

## a minimal example

create a polars dataframe with a `Float16` column:

```py
import polars as pl

df = pl.DataFrame(
    {"name": "john", "height": 1.78},
    schema={"name": pl.String, "height": pl.Float16},
)
df.write_parquet("./data.parquet")
print(df)
```

attempting to read the same file from r:

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

`Float32` and `Float64` work fine. the issue is just with `Float16`.

the workaround is to cast to `Float64` in polars before writing:

```py
df = df.with_columns(pl.col("height").cast(pl.Float64))
df.write_parquet("./data.parquet")
```

## reporting the issue

the r `arrow` package is an r binding for the apache arrow c++ library. its source lives on github, so i opened an issue there: https://github.com/apache/arrow/issues/50378.

still waiting on updates. if i am missing something obvious, i would like to know.
