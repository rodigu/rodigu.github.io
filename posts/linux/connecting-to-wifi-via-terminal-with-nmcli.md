<!--
.. title: connecting to wifi via terminal with nmcli
.. slug: connecting-to-wifi-via-terminal-with-nmcli
.. date: 2026-02-28 16:19:37 UTC-03:00
.. tags: terminal
.. category: linux
.. link: 
.. description: 
.. type: text
-->

went to sesc paulista.
last time i visited was years ago, soon after it first opened.
the top floor now seems to be accessible only through reservations now.

this was the first time i tried connecting to wifi with this new arch installation.

the cachyos distro came with `nmcli`. i am not yet certain that it is a common dependency for other distros.

this lists the available wifi networks:

```bash
nmcli device wifi list
```

this connects to wifi:

```bash
nmcli device wifi connect connection_name password connection_password
```
