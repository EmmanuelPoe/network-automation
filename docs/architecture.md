# Architecture

## Flow

```
config.yaml ──> InitNornir ──> SimpleInventory (hosts.yaml + groups.yaml)
                     │
                     ▼ nr.run(task=..., num_workers threads)
            netmiko_send_command over SSH (port 22) to each host
                     │
          ┌──────────┴───────────┐
   backup_configs.py       compliance_check.py
   backups/<host>/*.cfg    reports/compliance.csv + Rich table
```

## Inventory model

- **hosts.yaml**: name → `hostname` (management IP) and `groups`.
- **groups.yaml** has two kinds of groups:
  - platform/credential groups `cisco_ios` and `cisco_nxos`: `platform` (Netmiko device type), `username`, `password`, `port`
  - role groups `core`, `distribution`, `access`: `data.role` and `data.backup_priority` (currently unused by the scripts)
- Each host belongs to one platform group and one role group, so it inherits connection settings from the first and metadata from the second.

## Scripts

### `backup_configs.py`
- Task `backup_device`: `show running-config`, writes `backups/<host>/<host>_<YYYYmmdd_HHMMSS>.cfg`, stores the path in `task.host["backup_file"]`.
- Prints a results table (OK/FAILED per host). `BACKUP_DIR` is resolved relative to the script, but `config.yaml` is opened relative to the current directory.

### `compliance_check.py`
- Loads `templates/baseline_policy.yaml`: a list of `checks`, each with `name`, `command`, and `must_contain` and/or `must_not_contain` substrings.
- For each host and check, runs the command and records a violation per missing required string or present forbidden string. Matching is a plain substring test on raw CLI output.
- Writes all violations to CSV (`host, check, expected, status`) and prints a table, or a pass message if none.

### Baseline policy (current checks)

NTP server configured; `ip ssh version 2`; no `transport input telnet` on VTY 0-4; `banner login` present; `service password-encryption`; no `snmp-server community public|private`.

## Not implemented

Config push, interface report and Jinja2 templating (despite `jinja2` in requirements and the README). `config.yaml` sets `logging.log_file: logs/nornir.log`; the `logs/` directory is not created by the scripts.
