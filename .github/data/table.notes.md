
No `sshfs` cell is listed for any release: `fuse-sshfs` is not packaged in
AlmaLinux's BaseOS or AppStream for 9 or 10 (it lives in EPEL), and a base
image should not carry a third-party repository. `rsync`, `nfs-utils` and
`tree` are all in BaseOS, so every other sync method listed above is real.

There is no 9 `ppc64le` image even though upstream publishes one. Under
QEMU TCG that guest boots to a login prompt and then loses cloud-init to a
deterministic SIGSEGV inside `libpython3.9.so.1.0` -- every restart faults
at the same instruction address -- so the network is never configured and
sshd is never reachable (CI run 32710687202, cancelled after 62 minutes).
The fault is specific to the CPython 3.9 / ppc64le / TCG combination:
9 `aarch64` and 9 `s390x` run the same Python 3.9 and build fine, and 10
`ppc64le` (Python 3.12) builds fine on the same emulated architecture. It
is an upstream-image-meets-emulator defect, not a builder configuration
one, so the release is simply not offered rather than shipped broken.
