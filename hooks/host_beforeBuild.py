# host_beforeBuild.py -- download the DATED cloud image, never the "-latest"
# alias.
#
# The confs keep AlmaLinux's stable "-latest" URL so they do not rot when a
# point release lands. That name, however, is a MUTABLE file behind Fastly,
# and repo.almalinux.org serves it with
#   cache-control: public, max-age=31536000, immutable
# The CDN answers different byte ranges of one URL from different cache
# entries (each 206 carries its own ETag / Last-Modified), so after upstream
# replaces "-latest" some ranges can still come from the PREVIOUS build. The
# result is a file of the right size, with every Content-Range correct,
# stitched from two different images.
#
# Seen 2026-11-16, run 43789416704 (build 10-s390x): the Nov-09 and Oct-12
# s390x images are both exactly 257884160 bytes, and the CDN still served
# the Oct-12 bytes for [100000000, 120000000) and [180000000, 200000000);
# the rest was the Nov-09 build. qemu-img convert failed with
# "Cluster allocation offset ... unaligned". The same mix came back over a
# single stream from another POP, so this is not the 8-thread downloader. It
# is also the LUCKY case: had the stale segment covered only data clusters,
# convert would have succeeded and the image would have shipped with silently
# corrupt files.
#
# The dated files are written once and never replaced, so a cached segment
# of one can only ever be a segment of that same file. This hook reads the
# directory's CHECKSUM (sha256sum format), finds the dated build whose hash
# equals the "-latest" entry, and points VM_VHD_LINK at it.
#
# beforeBuild runs long before _prep_vhd_disk() reads VM_VHD_LINK, and this
# file is exec()'d into build.py's globals, so assigning os.environ is
# enough (same mechanism as nextbsd-builder's hook). A conf that already
# names a dated file is left alone.

_al_link = env("VM_VHD_LINK")
_al_m = re.match(r"^(https?://.+/)([^/]+-latest\.[^/]+\.qcow2)$", _al_link)
if not _al_m:
    log("VM_VHD_LINK is not a -latest alias, using it as is: %s" % _al_link)
else:
    _al_dir, _al_latest = _al_m.group(1), _al_m.group(2)
    _al_sums_url = _al_dir + "CHECKSUM"
    _al_sums = None
    for _al_try in range(3):
        try:
            _al_req = urllib.request.Request(
                _al_sums_url, headers={"User-Agent": "anyvm-almalinux-builder"})
            with urllib.request.urlopen(_al_req, timeout=60) as _al_resp:
                _al_sums = _al_resp.read().decode("utf-8", "replace")
            break
        except Exception as _al_err:
            log("cannot read %s (attempt %d of 3): %s"
                % (_al_sums_url, _al_try + 1, _al_err))
            if _al_try < 2:
                time.sleep(15 * (_al_try + 1))
    if _al_sums is None:
        log("FATAL: no CHECKSUM to resolve %s against" % _al_latest)
        sys.exit(1)

    # "<sha256>  <name>" per line; a leading "*" marks binary mode.
    _al_entries = []
    for _al_line in _al_sums.splitlines():
        _al_f = _al_line.split()
        if len(_al_f) == 2 and re.match(r"^[0-9a-f]{64}$", _al_f[0]):
            _al_entries.append((_al_f[0], _al_f[1].lstrip("*")))

    _al_hash = [h for (h, n) in _al_entries if n == _al_latest]
    if len(_al_hash) != 1:
        log("FATAL: expected exactly 1 CHECKSUM entry for %s in %s, found %d"
            % (_al_latest, _al_sums_url, len(_al_hash)))
        sys.exit(1)
    # Identical hashes are identical bytes, so if upstream ever lists the
    # same build under two dated names either one is correct.
    _al_dated = sorted(n for (h, n) in _al_entries
                       if h == _al_hash[0] and n != _al_latest)
    if not _al_dated:
        log("FATAL: no dated file in %s has the sha256 of %s (%s)"
            % (_al_sums_url, _al_latest, _al_hash[0]))
        sys.exit(1)

    os.environ["VM_VHD_LINK"] = _al_dir + _al_dated[-1]
    log("%s is %s (sha256 %s)" % (_al_latest, _al_dated[-1], _al_hash[0]))
    log("VM_VHD_LINK=%s" % os.environ["VM_VHD_LINK"])
