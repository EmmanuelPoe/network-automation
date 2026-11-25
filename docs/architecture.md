# Architecture

## Flow

```
config.yaml ──> common.load_config() (resolve inventory/log paths from repo root)
                     │
                     ▼
               InitNornir(**cfg) ──> SimpleInventory (hosts.yaml + groups.yaml)
                     │  common.init_nornir() sets username/password on every host
                     ▼ nr.run(task=..., threaded runner, 10 workers)
            netmiko_send_command over SSH (port 22) to each host
                     │
          ┌──────────┴───────────┐
   backup_configs.py       compliance_check.py
   backups/<host>/*.cfg    reports/compliance.csv + Rich table
```

## Inventory model

- **hosts.yaml**: name → `hostname` (management IP) and `groups`.
- **groups.yaml** has two kinds of groups:
  - platform groups `cisco_ios` and `cisco_nxos`: `platform` (Netmiko device type) and `port`
  - role groups `core`, `distribution`, `access`: `data.role` and `data.backup_priority` (available to tasks; not used by the current scripts)
- Each host belongs to one platform group and one role group. Credentials are not in the inventory.

## `scripts/common.py`

- `REPO_ROOT`, `CONFIG_FILE`
- `get_credentials()` → `(DEVICE_USERNAME, DEVICE_PASSWORD)` from the environment, prompting (password via `getpass`) when unset
- `load_config(path)` → config dict with `host_file`, `group_file`, `defaults_file` and `log_file` made absolute; creates the log directory
- `init_nornir(config_file=CONFIG_FILE, credentials=None)` → Nornir object with credentials applied to every host (tests pass `credentials=` explicitly)

## Scripts

### `backup_configs.py`
- Task `backup_device(task, backup_dir=REPO_ROOT/"backups")`: `show running-config`, writes `<backup_dir>/<host>/<host>_<YYYYmmdd_HHMMSS>.cfg`, stores the path in host data `backup_file`.
- Prints a results table (OK/FAILED per host).

### `compliance_check.py`
- `load_policy()` reads `templates/baseline_policy.yaml`: `checks`, each with `name`, `command`, and `must_contain` and/or `must_not_contain` substrings.
- `evaluate(host, check, output)` (pure) returns violation dicts; `check_compliance` runs each check's command and stores violations in host data `violations`.
- `write_report()` writes CSV columns `host, check, expected, status`.
- Hosts that could not be reached are reported separately, and the "all passed" message only appears when every host was checked.
- CLI: `--report PATH` (default `reports/compliance.csv` under the repo root).

### Baseline policy (current checks)

NTP server configured; `ip ssh version 2`; no `transport input telnet` on VTY 0-4; `banner login` present; `service password-encryption`; no `snmp-server community public|private`.

## Not implemented (README roadmap)

Config push and an interface report. `jinja2` is already a dependency for templated pushes.
