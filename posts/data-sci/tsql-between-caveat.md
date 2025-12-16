.. title: is tsql's `between` inclusive?
.. slug: tsql-between
.. date: 2025-12-16 17:10:00 UTC-03:00
.. tags: sql,databases
.. category: data-sci
.. author: rodigu
.. link: https://rodigu.github.io/
.. description: a caveat to the tsql `between`

the documentation doesn't seem to mention inclusivity at all until [section b](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/between-transact-sql?view=sql-server-ver17#b-use--and--instead-of-between).
and this information is actually only conclusively stated all the way down in [section d](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/between-transact-sql?view=sql-server-ver17#d-use-between-with-datetime-values).

however, as i have come to find out (not before a whole hour of debugging): it ... depends?

## context

lets create a table with two columns.
`date_vc` is a varchar that follows the formatting `'%d/%m/%Y'`

```sql
create table tsql_testing(
    [date_vc] varchar(20) not null,
    [date_dt] datetime not null
)
insert into tsql_testing (date_vc, date_dt)
values ('15/12/2025', '2025-12-15 23:48:13.000')
insert into tsql_testing (date_vc, date_dt)
values ('09/12/2025', '2025-12-09 23:48:13.000')
```

```sql
SELECT * FROM TSQL_TESTING
WHERE CONVERT(DATETIME,DATE_VC,103) BETWEEN '2025-12-09' AND '2025-12-15';

SELECT * FROM TSQL_TESTING
WHERE DATE_DT BETWEEN '12/09/2025' AND '12/15/2025'
```
