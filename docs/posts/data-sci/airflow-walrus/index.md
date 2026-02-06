.. title: walrus for airflow
.. slug: airflow-walrus
.. date: 2025-03-30 16:20:00 UTC-03:00
.. tags: python, airflow, snippet
.. author: rodigu
.. category: data-sci
.. link: https://rodigu.github.io/
.. description: walrus operator and airflow task dependency

```py
[
    (
        a_data := get_users.partial(
            connection_meta=connection_meta
        ).expand(code=code_a)
    ),
    (
        b_data := get_users.partial(
            connection_meta=connection_meta
        ).expand(code=code_b)
    ),
] >> (fetch_content := content_fetch())
```
