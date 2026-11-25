# Network Automation

Python scripts for Cisco IOS and NX-OS devices built on [Nornir](https://nornir.readthedocs.io/) 3 and [Netmiko](https://github.com/ktbyers/netmiko). They read a YAML inventory, connect over SSH in parallel, and run read-only `show` commands.

## Features

- **Config backup** — `show running-config` from every device, saved to `backups/<host>/<host>_<timestamp>.cfg`
- **Compliance check** — audits each device against `templates/baseline_policy.yaml` and writes violations to a CSV

## Project structure

```
network-automation/
├── config.yaml                 # Nornir 3 settings (threaded runner, inventory paths, logging)
├── inventory/
│   ├── hosts.yaml              # devices and their groups
│   └── groups.yaml             # platform groups (cisco_ios, cisco_nxos) and role groups (core, distribution, access)
├── scripts/
│   ├── common.py               # Nornir setup + runtime credential injection
│   ├── backup_configs.py
│   └── compliance_check.py
├── templates/
│   └── baseline_policy.yaml    # compliance checks
├── tests/                      # offline tests (Netmiko is mocked)
├── backups/  reports/  logs/   # generated output, gitignored
├── requirements.txt            # runtime dependencies
└── requirements-dev.txt        # + pytest, ruff
```

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

export DEVICE_USERNAME=admin
export DEVICE_PASSWORD='...'          # or omit both and you will be prompted

python scripts/backup_configs.py
python scripts/compliance_check.py --report reports/compliance.csv
```

Credentials are never stored in the inventory; `scripts/common.py` applies them to every host at runtime. Scripts can be run from any directory.

## Inventory format

```yaml
# inventory/hosts.yaml
core-sw-01:
  hostname: 192.168.1.1     # management IP or DNS name
  groups:
    - cisco_ios             # platform group: Netmiko device type, port
    - core                  # role group: data.role, data.backup_priority
```

## Compliance policy format

```yaml
# templates/baseline_policy.yaml
checks:
  - name: SSH version 2
    command: show running-config | include ip ssh
    must_contain:
      - "ip ssh version 2"
  - name: Telnet disabled
    command: show line vty 0 4
    must_not_contain:
      - "transport input telnet"
```

Matching is a plain substring test on the command output. The default policy checks NTP, SSH v2, telnet on VTY lines, login banner, password encryption, and default SNMP communities.

## Development

```bash
pip install -r requirements-dev.txt
ruff check scripts tests && ruff format --check scripts tests
pytest -q
```

CI runs the same steps on every pull request. Tests never connect to devices.

## Roadmap

Config push from Jinja2 templates (dry run with diff by default) and an interface status report.

Agent and contributor docs: [CLAUDE.md](CLAUDE.md) and [docs/](docs/).
