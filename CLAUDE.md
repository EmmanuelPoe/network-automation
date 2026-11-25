# CLAUDE.md

Guidance for AI agents working in this repository. Read this first, then the matching file in `docs/`.

## What this is

Python CLI scripts that use **Nornir 3 + Netmiko** to run read-only commands against Cisco IOS/NX-OS devices listed in a YAML inventory:

- `scripts/backup_configs.py` — `show running-config` on every host, saved to `backups/<host>/<host>_<timestamp>.cfg`
- `scripts/compliance_check.py` — runs the checks in `templates/baseline_policy.yaml`, writes violations to `--report` (default `reports/compliance.csv`) and prints a Rich table
- `scripts/common.py` — shared `init_nornir()`: loads `config.yaml` with paths resolved from the repo root and injects credentials from `DEVICE_USERNAME` / `DEVICE_PASSWORD` (or prompts)

## Commands

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt         # runtime deps + pytest + ruff
pytest -q                                   # offline tests, Netmiko mocked
ruff check scripts tests && ruff format --check scripts tests
export DEVICE_USERNAME=admin DEVICE_PASSWORD='...'
python scripts/backup_configs.py
python scripts/compliance_check.py --report reports/compliance.csv
```

CI (`.github/workflows/ci.yml`) runs ruff and pytest on every pull request.

## Layout

```
config.yaml                 Nornir 3 config: threaded runner (10 workers), SimpleInventory, logging to logs/nornir.log
inventory/hosts.yaml        4 example devices on 192.168.x.x (lab addresses)
inventory/groups.yaml       platform groups (cisco_ios, cisco_nxos: platform + port) and role groups (core, distribution, access)
scripts/                    common.py, backup_configs.py, compliance_check.py
templates/baseline_policy.yaml   compliance checks
tests/test_scripts.py       offline tests
ruff.toml                   lint config (line length 110; scripts' modules are first-party)
```

## Rules for agents

- Scripts connect to real network devices. Never run them against an inventory you did not create for testing unless the user asks; keep commands read-only.
- Never put usernames, passwords, enable secrets or SNMP communities in inventory files, policies or tests. Credentials come only from `init_nornir()`.
- New scripts must use `common.init_nornir()` and repo-root paths (`common.REPO_ROOT`), so they work from any directory.
- `backups/`, `reports/` and `logs/` hold device output (configs contain secrets); they are gitignored and must stay that way.
- Every behavior change gets an offline test (mock `netmiko_send_command` in the script's module namespace).

## Docs

- [docs/architecture.md](docs/architecture.md)
- [docs/security.md](docs/security.md)
- [docs/testing.md](docs/testing.md)
- [docs/agent-guide.md](docs/agent-guide.md)

There is no UI; output is Rich tables in the terminal plus files.
