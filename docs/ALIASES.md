# Identical-file aliases intentionally omitted

This repository has exactly one physical copy for each unique Git blob
content. In older or external strategies the same bytes may be referenced
by a different filename. The aliases below are names of **identical**
blobs in the public source collections, **not** additional files.

| Canonical file | Other names with identical content |
| --- | --- |
| `files/fake/active_discord_udp.bin` | `ACTIVE_DISCORD_UDP.bin` |
| `files/fake/active_game_udp.bin` | `ACTIVE_GAME_UDP.bin` |
| `files/fake/fake_quic_3.bin` | `quic_7.bin` |
| `files/fake/fake_quic.bin` | `fake_quic_1.bin` |
| `files/fake/fake_tls_3.bin` | `tls_clienthello_2.bin`, `tls_clienthello_www_google_com_2.bin` |
| `files/fake/fake_tls_6.bin` | `tls_clienthello_5.bin` |
| `files/fake/fake_tls_7.bin` | `tls_clienthello_18.bin` |
| `files/fake/quic_2.bin` | `1.bin` |

An installer must not silently create duplicate BLOBs or rewrite an existing
user-authored strategy. Any strategy referring to a removed alias requires
explicit migration, validation, or an informative compatibility warning.
These aliases may overlap names of official bol-van/zapret2 resources;
the installer must compare against the **selected upstream version**.

Special note: `tls_clienthello_max_ru.bin` and
`tls_clienthello_max_ru_extended.bin` are **different binary contents**,
not aliases. The latter is the 654-byte user-supplied variant with
unresolved original provenance.
