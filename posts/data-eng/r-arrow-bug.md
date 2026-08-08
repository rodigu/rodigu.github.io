<!--
.. title: finding a bug with the r arrow package
.. date: 2026-08-07 22:08-03:00 UTC-03:00
.. tags: python, parquet, r, etl, polars
.. status: draft
.. category: data-eng
.. author: rodigu
.. link: https://rodigu.github.io/
.. description: the process of finding a bug in a public package
-->

i have been working with some legacy r code at work that handles etl. while migrating it to airflow, i found a bug in the `arrow` package: it silently corrupts `Float16` columns read from parquet files. numeric values were off by more than 10x in production dashboards, and it took hours to trace back to the source.

<!-- TEASER_END -->

## the bug

at work, i have been incrementally migrating one of our r codebases to airflow dags.
still, there are some transformations still done by r scripts that use arrow as a dependency.

one of our etl pipelines which uses one such script broke.
we found this issue because some numeric values were unreasonably large in the dashboards that consumed the data from the etl pipeline (we had people who were kilometers high).

at first, i figured there was an improper transformation on airflow.
i debugged the transformations there, which is quite easy with the airflow logging system.
however, everything was fine, and the final parquet files produced were correct.
so i moved on to the r script.

it is a complex, thousand-lines legacy script.
it is challenging to debug, and i spent a while looking through the code.
it does break every now and then, so i went in assuming there was a bug with the implementation.

i made the mistake of working backwards, starting at the transformations before checking if the data was correct when it was first read.
then, when i finally realized that all of the transformations were already working with bad data.

the bug was that `arrow` not properly reading `Float16` columns created by `polars` in python.

below is a minimal reproduction of the bug.

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

the workaround for me ended up just casting to `Float64` in polars before writing:

```py
df = df.with_columns(pl.col("height").cast(pl.Float64))
df.write_parquet("./data.parquet")
```

## reporting the issue

the r `arrow` package is an r binding for the apache arrow c++ library. the library documentation does reference [float 16 support](https://arrow.apache.org/java/main/reference/org.apache.arrow.memory.core/org/apache/arrow/memory/util/Float16.html).

its source lives on github, so i opened an issue there: https://github.com/apache/arrow/issues/50378.

maintainers identified the source of the bug:

> The root cause of the issue here is that the value you are returned is the raw value, but not the float value, so the fix here is to make sure it properly gets converted into a float instead of returning the raw bytes.
>
> Or in other words, you're being returned the correct value, but the issue occurs when it's converted from C++ to R.
>
> [thisisnic](https://github.com/thisisnic)

## for the future

one of the weakest points in our current pipeline, as we transition from r to airflow with python, is the point where these two separate languages interact.
though the dataframe abstraction is the same for both, the particular ways in which they work with data is not necessarily equivalent.
