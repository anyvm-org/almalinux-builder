How the images are built:

Each image is built automatically in the
[anyvm-org/almalinux-builder](https://github.com/anyvm-org/almalinux-builder)
repo's GitHub Actions: it downloads the official AlmaLinux GenericCloud
image, customizes it (serial console, ssh, first-boot setup), boots it
in QEMU, pre-installs the packages listed in the conf, and exports the
disk as a compressed qcow2 image. No interactive installer is run.

Upstream media: the official AlmaLinux cloud images from
https://repo.almalinux.org/almalinux/ (download page:
https://almalinux.org/get-almalinux/).
