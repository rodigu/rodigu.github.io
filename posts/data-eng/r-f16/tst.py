import polars as pl
import pyarrow
import pyarrow.parquet as pq

if __name__ == "__main__":
    pl.DataFrame(
        {"name": "john", "height": 1.78},
        schema={"name": pl.String, "height": pl.Float16},
    ).write_parquet("./posts/data-eng/r-f16/data.parquet")
    df = pl.read_parquet("./posts/data-eng/r-f16/data.parquet")
    print(df)

    # Read with pyarrow and print
    table = pq.read_table("./posts/data-eng/r-f16/data.parquet")
    print(table)
