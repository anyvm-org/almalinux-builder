

| Release | x86_64 | aarch64 | s390x | ppc64le |
|---------|---------|---------|---------|---------|
| 10 | ✅ (rsync,scp,nfs,tar) | ✅ (rsync,scp,nfs,tar) | ✅ (rsync,scp,nfs,tar) | ✅ (rsync,scp,nfs,tar) |
| 9 | ✅ (rsync,scp,nfs,tar) | ✅ (rsync,scp,nfs,tar) | ✅ (rsync,scp,nfs,tar) | ✅ (rsync,scp,nfs,tar) |


No `sshfs` cell is listed for any release: `fuse-sshfs` is not packaged in
AlmaLinux's BaseOS or AppStream for 9 or 10 (it lives in EPEL), and a base
image should not carry a third-party repository. `rsync`, `nfs-utils` and
`tree` are all in BaseOS, so every other sync method listed above is real.

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
