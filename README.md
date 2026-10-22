# Zapret2 Extra Resources

A supplementary, deduplicated Lua and fake-packet BLOB catalog for
[bol-van/zapret2](https://github.com/bol-van/zapret2), intended to be
integrated with [os-zapret2-restyle](https://github.com/Tolian82/os-zapret2-restyle)
on OPNsense in a **separate later plugin change**.

## Contents (2026-10-22)

- **19** Lua modules in [lua/](lua/).
- **54** unique BIN payloads in [files/fake/](files/fake/).
- **73** actual resource files. No duplicate contents among these files
  according to their Git blob SHA values.
- Full source paths and per-file Git blob hashes in
  [inventory/sources.json](inventory/sources.json).
- Duplicate filename references and canonical names in
  [docs/ALIASES.md](docs/ALIASES.md).

Files identical to officially shipped bol-van/zapret2 resources have been
excluded, comparing both upstream `v1.0.6` and `master` at the time of
publication. Resources with different content but similar names may exist.
Future upstream changes require another comparison before installation.

**Compatibility and availability:** This is a collection, not an assurance
that each strategy works or all Lua modules can be loaded together. Publishing
these files neither installs them on OPNsense nor modifies a Zapret2 service.
The plugin integration must implement collision checks, proper rollback,
resource integrity verification, and safeguards against overwriting user files.

**The `wgobfs` script is not included** because current official
`zapret-obfs.lua` already implements it. The same filename existed as an
official upstream file in older releases.

## Search capability descriptions (schema 1)

[Optional reviewed descriptors](inventory/capabilities.json) are separate from
the source/provenance inventory. A descriptor names an actual shipped resource,
its supported protocol/transport, native action or exported Lua function, and
exact dependencies/arguments. The current initial examples cover one TLS
ClientHello payload and one custom Lua desync function; they are **not** a
permanent list of allowed files, a claim of bypass success, or instructions to
load every Lua module.

The integration must look up descriptors by **files actually present** in the
installed `ResourceInventory`. New resources can be described in JSON without
changing Python source; removed/unreadable resources are never made executable
by lingering metadata. Files with no supported, verified capability remain
visible but **unsupported**, not silently guessed by filename. Adding a new
native action beyond the plugin's supported renderer remains a code feature,
not an arbitrary executable-string escape hatch.

Run `python3 scripts/verify_inventory.py` before publishing. It checks
real source bytes against the Git blob SHA and size, rejects duplicate and
symlink files, and checks descriptor paths, formats, exports and arguments.
This is a **catalog integrity** check; operational strategy results require
separate installed OPNsense tests.

## Licenses and attribution

See [LICENSE](LICENSE) for original packaging materials,
[NOTICE](NOTICE) and [CONTRIBUTORS.md](CONTRIBUTORS.md) for provenance, and
[licenses/](licenses/) for preserved MIT third-party notices. Not every
source author and packet capture origin is identifiable. In particular,
`files/fake/tls_clienthello_max_ru_extended.bin` is an unverified
provenance exception, clearly called out in NOTICE.

## Updating resources

- Prefer reviewed, pinned Git revisions and sources with attributable rights.
- Keep only one physical file for each exact Git blob payload.
- Never override a bol-van/zapret2 file or a user's custom file silently.
- Do not rename an existing strategy dependency without migration.
- Refresh `inventory/sources.json` whenever resources change.
