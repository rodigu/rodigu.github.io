<!--
.. title: doing the lord's work with python and the walrus operator
.. slug: airflow-walrus
.. date: 2026-02-14 11:54:00 UTC-03:00
.. tags: python, airflow, snippet
.. author: rodigu
.. type: micro
.. category: data-eng
.. link: https://rodigu.github.io/
.. description: walrus operator and airflow task dependency
-->

*(actual prod code for airflow)*

```python
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
] >> (fetch_content := content_fetch(a_data, b_data))
```
