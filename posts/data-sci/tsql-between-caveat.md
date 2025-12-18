.. title: is tsql's `between` inclusive?
.. slug: tsql-between
.. date: 2025-12-16 17:10:00 UTC-03:00
.. tags: sql,databases
.. category: data-sci
.. author: rodigu
.. link: https://rodigu.github.io/
.. description: a caveat to the tsql `between`

the documentation doesn't seem to mention inclusivity at all until [section b](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/between-transact-sql?view=sql-server-ver17#b-use--and--instead-of-between), which suggests that `between` is inclusive.
the information is only really explicitly stated all the way down in [section d](https://learn.microsoft.com/en-us/sql/t-sql/language-elements/between-transact-sql?view=sql-server-ver17#d-use-between-with-datetime-values), where it states that (for datetime values, at least), `between` is inclusive.

however, as i have come to find out (not before a whole hour of debugging[^1]): it ... depends?

[^1]: it is a tremendously unpleasant experience to find out that a bug derives not from a mistake i have made, bet from an *undocumented* issue from the tool i am using. all the more aggravating when this is not someone's foss passion project, but a prod tool by a massive tech company (which we pay good money to deploy on *their* azure servers). well, at least this is not as bad as powerbi.

## context

lets create a table with two columns.
`date_vc` is a `varchar` that follows the formatting `'%d/%m/%Y'` (as per the usual cron formatting[^2]).
`date_dt` is a `datetime` column.

[^2]: not entirely sure of the name. i have seen this formatting in different places, such as a [rust library](https://docs.rs/chrono/latest/chrono/format/strftime/index.html) and the [python standard library](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes), but i can't find a proper standards definition, nor the origin of this formatting convention.

this was an issue i ran into at work, involving real data.
here, i'll demonstrate it with a sample table.

here is a sample sql script to create the tables and insert some values into them.

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

now, notice that, as previously mentioned, `date_vc` has string values with style 103 (`'%d/%m/%Y'`),
the British/French standard as per the [microsoft documentation](https://learn.microsoft.com/en-us/sql/t-sql/functions/cast-and-convert-transact-sql?view=sql-server-ver17#date-and-time-styles).

## between is (not?) inclusive

if we try to select the following using `between`, what should be the expected behavior?

```sql
select date_vc, date_dt from tsql_testing
where convert(datetime,date_vc,103) between '2025-12-09' and '2025-12-15';
```

we convert the `varchar` column `date_vc` to datetime, and select between those two dates.

as alluded to in microsoft's own documentation, we do get that this between select is indeed inclusive, as we fetch the following from the select:

>|date_vc|date_dt|
>|-|-|
>| 09/12/2025 | 2025-12-09 23:48:13.000 |
>| 15/12/2025 | 2025-12-15 23:48:13.000 |

note that, even if we were to use the 103 standard with `between '12/09/2025' and '12/15/2025'`, we'd still get the same response.

now, if we do the ***exact same select*** for the `datetime` column `date_dt` (again, it doesn't matter which standard and formatting you pick):

```sql
select date_vc, date_dt from tsql_testing
where date_dt between '12/09/2025' and '12/15/2025'
```

we get a response non-inclusive of the second value:

>|date_vc|date_dt|
>|-|-|
>|09/12/2025 | 2025-12-09 23:48:13.000|

is this a quirk of tsql? or is this also in other sql dialects?
