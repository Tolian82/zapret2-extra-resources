# Zapret2 Extra Resources

Additional Lua modules and packet payload (BLOB) files for [bol-van/zapret2](https://github.com/bol-van/zapret2), curated for use by [os-zapret2-restyle](https://github.com/Tolian82/os-zapret2-restyle).

- `lua/`: supplementary modules (not loaded automatically).
- `files/fake/`: supplementary payloads (not injected automatically).
- `manifest.json`: immutable resource inventory with source references and Git blob hashes.
- `LICENSE`, `NOTICE`, `CONTRIBUTORS.md`, `licenses/`: attribution and third-party licensing.

**No upstream files intentionally repackaged.** Files duplicate to the official bol-van/zapret2 `v1.0.6` tree by Git blob content or by target path are excluded. Files matching one another exactly are deduplicated; see `docs/ALIASES.md`. The official release may change: future installers must check collisions with their selected runtime version.

**Important:** This repository is a resource catalog, not an endorsement that every payload works or every supplementary Lua module can be loaded together. The plugin's existing Strategy configurations must be respected. Publishing resources does not install them automatically on OPNsense.

## Sources and legal

This repository contains redistributed resources from several community projects. See [NOTICE](NOTICE), [CONTRIBUTORS.md](CONTRIBUTORS.md), and [licenses](licenses/) for attribution and preserved license texts. The top-level MIT LICENSE applies only to original material of this repository, **not as a claim of authorship or new license grant over third-party files**. Missing precise authorship is documented openly; please send corrections with supporting links.

Source origins include [avatarDD/zapret-gui](https://github.com/avatarDD/zapret-gui) and [AmantesNihilo/zapret-universal-interface](https://github.com/AmantesNihilo/zapret-universal-interface). Official Zapret2 is maintained by bol-van.
