# MikroTik

- `export.rsc` - text config, produced by `make mikrotik-export ROUTER=admin@<ip>`.
  Sensitive values are hidden by RouterOS 7; serial/software-ID lines are stripped. Review the diff!
- Binary `.backup` files are git-ignored - keep them on backup storage.

Docs: [docs/network/mikrotik.md](../../docs/network/mikrotik.md)
