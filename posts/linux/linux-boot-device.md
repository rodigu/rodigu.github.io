<!--
.. title: creating a bootable usb on linux
.. slug: linux-boot-device
.. date: 2026-08-03 15:59:37 UTC-03:00
.. tags: terminal, cachyos, steam-deck
.. category: linux
.. link: 
.. description: making a bootable usb for cachyos handheld
.. type: text
-->

i have only ever had laptops, and am considering building a pc.
however, pc parts are currently pretty expensive (particularly here in brasil).

have been using cachyos in my personal laptop for over a year now, and i enjoy it.
recently learned that cachy has a handheld version made specifically for devices like the steam deck.
so i am going to try it out.

<!-- TEASER_END -->

## making a bootable device

i got the cachyos handheld distro iso torrent magnet from their [downloads page](https://cachyos.org/download/).

balena etcher has not been working on my laptop, so i followed [linuxconfig's tutorial](https://linuxconfig.org/how-to-make-a-bootable-usb-from-an-iso-in-linux).

### get device path

```bash
sudo fdisk -l
```

### `dd`

```bash
sudo dd bs=4M if=/path/to/file.iso of=/dev/sdX status=progress oflag=sync
```

## the cachyos handheld experience
