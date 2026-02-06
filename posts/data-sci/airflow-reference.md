.. title: airflow reference
.. slug: airflow-reference
.. date: 2025-03-30 16:20:00 UTC-03:00
.. tags: python, airflow, reference
.. author: rodigu
.. status: draft
.. category: data-sci
.. link: https://rodigu.github.io/
.. description: useful airflow snippets

## deploying and debugging the airflow daemon


```bash
systemctl daemon-reload
```

### `systemctl`

```bash
systemctl start airflow-scheduler
systemctl start airflow-webserver
```

```bash
systemctl status airflow-scheduler
systemctl status airflow-webserver
```

```bash
systemctl stop airflow-scheduler
systemctl stop airflow-webserver
```

```bash
systemctl restart airflow-scheduler
systemctl restart airflow-webserver
```

### logs

```bash
journalctl -u airflow-webserver.service
```
