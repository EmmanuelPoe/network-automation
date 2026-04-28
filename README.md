# Network Automation

Python-based network automation scripts for managing Cisco IOS and NX-OS devices at scale using Netmiko and Nornir.

## Features

- **Config Backup** — bulk backup running configs from all devices to timestamped files
- **Config Push** — deploy configuration changes across multiple devices simultaneously
- **Compliance Check** — audit devices against a baseline policy and report violations
- **Interface Report** — generate a CSV report of all interface states across the network

## Tech Stack

- Python 3.10+
- [Netmiko](https://github.com/ktbyers/netmiko) — multi-vendor SSH library
- [Nornir](https://nornir.readthedocs.io/) — automation framework
- PyYAML — inventory and config management

## Project Structure

```
network-automation/
├── inventory/
│   ├── hosts.yaml        # Device inventory
│   └── groups.yaml       # Device groups (core, distribution, access)
├── scripts/
│   ├── backup_configs.py     # Backup running configs
│   ├── push_config.py        # Push config changes
│   ├── compliance_check.py   # Audit against baseline
│   └── interface_report.py   # Generate interface state report
├── templates/
│   └── baseline_policy.yaml  # Compliance baseline
├── backups/              # Config backups (gitignored)
├── reports/              # Generated reports (gitignored)
├── requirements.txt
└── config.yaml           # Global settings
```

## Quick Start

```bash
pip install -r requirements.txt

# Backup all device configs
python scripts/backup_configs.py

# Run compliance check
python scripts/compliance_check.py --report reports/compliance.csv

# Push a config change
python scripts/push_config.py --template templates/ntp_config.j2 --hosts core
```

## Inventory Format

```yaml
# inventory/hosts.yaml
core-sw-01:
  hostname: 192.168.1.1
  groups:
    - cisco_ios
    - core

dist-sw-01:
  hostname: 192.168.1.2
  groups:
    - cisco_nxos
    - distribution
```
