.. title: airflow task inside task group failed
.. slug: airflow-task_group-failure
.. date: 2025-03-30 16:20:00 UTC-03:00
.. tags: python, airflow
.. author: rodigu
.. category: data-sci
.. link: https://rodigu.github.io/
.. description: checking if an airflow task has failed

checking if a task has failed in airflow is simple enough, and may be done with:

```py
from airflow.operators.python import get_current_context

@task
def check_task_failed(task_id: str) -> bool:
      context = get_current_context()
      return (
          context["dag_run"].get_task_instance(task_id=task_id).state
          == State.FAILED
      )
```

however, if the task is nested within a `task_group`, referencing the task with `task_id` doesn't work.
in theory, tasks inside a `task_group` should be indexed with `group_id.task_id`[^1], but trying `get_task_instance`
with this ID structure will return a `NoneType`.

the one way i have found to actually make it work, is with the following:

```py
from airflow.operators.python import get_current_context

@task
def check_task_failed(group_id: str, task_id: str) -> bool:
      context = get_current_context()
      failed_tasks = context["dag_run"].get_task_instances(state=State.FAILED)
      return f"{group_id}.{task_id}" in {
          ft.task_id for ft in failed_tasks
      }
```

which i was able to implement based an answer on stackoverflow[^2].

before finding that answer, i struggled with missing docs, llm hallucinations. and what i am fairly sure were people posting llm bullshit as if it were real.

[^1]: [astronomer docs on `task_groups`](https://www.astronomer.io/docs/learn/task-groups/){:target="_blank"}
[^2]: [the answer to my problems, thank you mati.o](https://stackoverflow.com/questions/73740427/airflow-how-to-get-list-of-upstream-failed-tasks){:target="_blank"}
