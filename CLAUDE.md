# CLAUDE.md

Guidance for AI agents working in this repository. Read this first, then the matching file in `docs/`.

## What this is

Python CLI scripts that use **Nornir 3 + Netmiko** to run commands against Cisco IOS/NX-OS devices listed in a YAML inventory:

- `scripts/backup_configs.py` — `show running-config` on every host, saved to `backups/<host>/<host>_<timestamp>.cfg`
- `scripts/compliance_check.py` — runs the checks in `templates/baseline_policy.yaml`, writes violations to `reports/compliance.csv` (or the path given as the first positional argument) and prints a Rich table

**The README overstates the repo.** `scripts/push_config.py`, `scripts/interface_report.py` and `templates/ntp_config.j2` do not exist, and `compliance_check.py` takes a positional path, not `--report`.

## Known blockers — the scripts do not run as committed

1. `config.yaml` is in **Nornir 2 format**. With Nornir 3 (`nornir>=3.4.0`), `InitNornir(config_file="config.yaml")` raises `TypeError: CoreConfig.__init__() got an unexpected keyword argument 'num_workers'`. Nornir 3 needs:
   ```yaml
   runner:
     plugin: threaded
     options: {num_workers: 10}
   inventory:
     plugin: SimpleInventory
     options: {host_file: inventory/hosts.yaml, group_file: inventory/groups.yaml}
   ```
2. `inventory/groups.yaml` sets `password: "{{ env.DEVICE_PASSWORD }}"`. SimpleInventory does not render templates, so Netmiko receives that literal string. Set the password at runtime instead (see [docs/security.md](docs/security.md)).

## Commands

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export DEVICE_PASSWORD='...'          # after fixing blocker 2
python scripts/backup_configs.py      # run from the repo root: paths in config.yaml are relative
python scripts/compliance_check.py [reports/compliance.csv]
```

## Layout

```
config.yaml                 Nornir config (needs the v3 fix above)
inventory/hosts.yaml        4 example devices on 192.168.x.x (lab addresses)
inventory/groups.yaml       platform/credential groups (cisco_ios, cisco_nxos) and role groups (core, distribution, access)
scripts/                    backup_configs.py, compliance_check.py
templates/baseline_policy.yaml   compliance checks
requirements.txt            netmiko, nornir, nornir-netmiko, nornir-utils, pyyaml, jinja2, rich (unpinned minimums)
```

## Rules for agents

- Scripts connect to real network devices. Never run them against an inventory you did not create for testing unless the user asks; prefer read-only `show` commands.
- Never put real passwords, enable secrets or SNMP communities in inventory files, policies or tests.
- `backups/`, `reports/` and `logs/` hold device configs (which contain secrets); they are generated output and must not be committed.
- Keep scripts runnable from the repo root.

## Docs

- [docs/architecture.md](docs/architecture.md)
- [docs/security.md](docs/security.md)
- [docs/testing.md](docs/testing.md)
- [docs/agent-guide.md](docs/agent-guide.md)

There is no UI; output is Rich tables in the terminal plus files.
