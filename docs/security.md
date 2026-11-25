# Security

This is a public repository that drives SSH sessions to network devices.

## Credentials

- The inventory must never contain real passwords. `groups.yaml` currently holds the placeholder `"{{ env.DEVICE_PASSWORD }}"`, which Nornir does **not** expand.
- Set credentials at runtime instead, after `InitNornir`:
  ```python
  import os, getpass
  pw = os.environ.get("DEVICE_PASSWORD") or getpass.getpass("Device password: ")
  for group in ("cisco_ios", "cisco_nxos"):
      nr.inventory.groups[group].password = pw
  ```
  Or use Nornir's `transform_function` to inject them for every host. Never log the value.
- `username: admin` is hard-coded in `groups.yaml`; prefer reading it from the environment too.
- Enable secrets (if needed) go in `connection_options.netmiko.extras.secret`, sourced the same way.

## Sensitive output

- Running configs contain password hashes, SNMP communities, keys and TACACS/RADIUS secrets. `.gitignore` covers `backups/`, `reports/` and `logs/`; keep it that way and never force-add files from them.
- Treat `compliance.csv` as internal: it reveals which devices are missing hardening controls.

## Device safety

- Both scripts send only `show` commands. Any future write path (config push) must default to a dry run, show a diff, and require an explicit confirmation flag.
- Netmiko connections run in parallel (`num_workers`); lower it for fragile or rate-limited devices.
- Host key checking follows Netmiko defaults; do not disable it globally.

## Supply chain

`requirements.txt` uses unpinned minimums (`>=`). Pin versions (or add a lock file) and run `pip-audit -r requirements.txt` before releases.
