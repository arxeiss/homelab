# homelab - generated docs, diagrams and helpers. Run `make` for the list of targets.
.DEFAULT_GOAL := help
SHELL := /bin/bash

VENV  ?= .venv
BIN   := $(VENV)/bin
PY    := $(BIN)/python
STAMP := $(VENV)/.installed

# ---- Diagram sources --------------------------------------------------------
INVENTORY   := inventory.yaml
INVENTORY_MD := network/inventory.md
NET_DIAGRAM := network/diagrams/network
DOT_SRC     := $(wildcard network/diagrams/*.dot)
WIRING_SRC  := $(wildcard esphome/devices/*/wiring.yaml)

GENERATED := $(INVENTORY_MD) \
            $(NET_DIAGRAM).svg $(NET_DIAGRAM).png \
            $(DOT_SRC:.dot=.svg) $(DOT_SRC:.dot=.png) \
            $(WIRING_SRC:.yaml=.svg) $(WIRING_SRC:.yaml=.png)

# ---- ESPHome (runs in Docker, no local install needed) ----------------------
ESPHOME_IMAGE ?= ghcr.io/esphome/esphome:stable
ESPHOME       := docker run --rm -it --network host -v "$(CURDIR)/esphome":/config $(ESPHOME_IMAGE)
DEVICE        ?=
ESPHOME_DEVICES := $(sort $(notdir $(wildcard esphome/devices/*)))

# ---- Read-only access to MikroTik / UniFi / Proxmox ---------------------------
# Credentials live outside the repo. Template: credentials.env.example, setup: ACCESS.md
CREDENTIALS ?= $(HOME)/.config/homelab/credentials.env
LOAD_CREDENTIALS = test -r "$(CREDENTIALS)" || { echo "Missing $(CREDENTIALS) - copy credentials.env.example, see ACCESS.md"; exit 1; }; \
	set -a; . "$(CREDENTIALS)"; set +a;
STATUS = $(LOAD_CREDENTIALS) python3 scripts/homelab_status.py

.PHONY: help
help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ---- Setup -------------------------------------------------------------------
$(STAMP): requirements.txt
	python3 -m venv $(VENV)
	$(BIN)/pip install -q --upgrade pip
	$(BIN)/pip install -q -r requirements.txt
	@touch $@

.PHONY: setup hooks check-graphviz
setup: $(STAMP) check-graphviz ## Create Python venv with wireviz, pre-commit

hooks: $(STAMP) ## Install git pre-commit hooks (gitleaks etc.)
	$(BIN)/pre-commit install

check-graphviz:
	@command -v dot >/dev/null || { echo "Graphviz 'dot' not found - install it (e.g. sudo apt install graphviz)"; exit 1; }

# ---- Generated files (committed) ---------------------------------------------
.PHONY: generate
generate: check-graphviz $(GENERATED) ## Regenerate network/inventory.md and all diagrams (network, *.dot, ESPHome wiring)

$(INVENTORY_MD): $(INVENTORY) scripts/inventory.py | $(STAMP)
	$(PY) scripts/inventory.py markdown $< -o $@

build/network.dot: $(INVENTORY) scripts/inventory.py | $(STAMP)
	$(PY) scripts/inventory.py dot $< -o $@

$(NET_DIAGRAM).%: build/network.dot
	dot -T$* $< -o $@

network/diagrams/%.svg: network/diagrams/%.dot
	dot -Tsvg $< -o $@

network/diagrams/%.png: network/diagrams/%.dot
	dot -Tpng -Gdpi=150 $< -o $@

esphome/devices/%/wiring.svg esphome/devices/%/wiring.png: esphome/devices/%/wiring.yaml | $(STAMP)
	$(BIN)/wireviz -f sp -o $(@D) -O wiring $<

# ---- Lint ---------------------------------------------------------------------
.PHONY: lint
lint: $(STAMP) ## Run all pre-commit checks (incl. secret scan) on the whole repo
	$(BIN)/pre-commit run --all-files

# ---- Live status (read-only, prints to terminal, nothing written to the repo) --
.PHONY: check-access mikrotik-status unifi-status pve-status status
check-access: ## Test read-only access to MikroTik, UniFi and Proxmox
	@$(STATUS) check

mikrotik-status: ## Router version + DHCP leases (dynamic vs static)
	@$(STATUS) mikrotik

unifi-status: ## UniFi devices (model, firmware, IP, uplink) + switch ports
	@$(STATUS) unifi

pve-status: ## Proxmox guests, storage, disks, backup jobs
	@$(STATUS) pve

status: mikrotik-status unifi-status pve-status ## All of the above - compare with inventory.yaml

# ---- MikroTik config export (committed) ------------------------------------------
.PHONY: mikrotik-export
mikrotik-export: ## Pull text config from router (secrets hidden, MACs + SSIDs masked)
	@$(LOAD_CREDENTIALS) \
	ssh -i "$${MIKROTIK_KEY/#\~/$$HOME}" -o BatchMode=yes "$$MIKROTIK_USER@$$MIKROTIK_HOST" '/export terse' \
	  | tr -d '\r' \
	  | grep -vE '^# (serial number|software id) =' \
	  | sed -E '1s/^# .* (by RouterOS .*)$$/# \1/' \
	  | sed -E 's/([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}/XX:XX:XX:XX:XX:XX/g' \
	  | sed -E 's/ssid=("[^"]*"|[^ ]+)/ssid="<redacted>"/g' \
	  > network/mikrotik/export.rsc
	@echo "Review before committing:  git diff network/mikrotik/export.rsc"

# ---- ESPHome -----------------------------------------------------------------
.PHONY: esphome-list esphome-config esphome-compile esphome-run esphome-logs esphome-check-device
esphome-list: ## List ESPHome devices
	@printf '%s\n' $(ESPHOME_DEVICES)

esphome-check-device:
	@test -n "$(DEVICE)" || { echo "Usage: make $(MAKECMDGOALS) DEVICE=<name>  (see make esphome-list)"; exit 1; }

esphome-config: esphome-check-device ## Validate device config (DEVICE=name)
	$(ESPHOME) config devices/$(DEVICE)/$(DEVICE).yaml

esphome-compile: esphome-check-device ## Compile firmware (DEVICE=name)
	$(ESPHOME) compile devices/$(DEVICE)/$(DEVICE).yaml

esphome-run: esphome-check-device ## Compile + flash over the air (DEVICE=name)
	$(ESPHOME) run devices/$(DEVICE)/$(DEVICE).yaml

esphome-logs: esphome-check-device ## Stream device logs (DEVICE=name)
	$(ESPHOME) logs devices/$(DEVICE)/$(DEVICE).yaml

# ---- Housekeeping ------------------------------------------------------------
.PHONY: clean
clean: ## Remove build output (keeps committed generated files)
	rm -rf build
