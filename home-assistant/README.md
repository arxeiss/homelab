# Home Assistant config

`config/` mirrors the YAML parts of HA's `/config`. See
[docs/home-assistant/index.md](../docs/home-assistant/index.md) for what belongs here and how to sync.

- Put features in `config/packages/<feature>.yaml` (enable with
  `homeassistant: packages: !include_dir_named packages` in `configuration.yaml`).
- `secrets.yaml` is git-ignored; `config/secrets.example.yaml` lists the keys.
