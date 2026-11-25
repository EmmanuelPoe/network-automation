# Security

This is a public repository that drives SSH sessions to network devices.

## Credentials

- Credentials never live in the inventory. `common.init_nornir()` sets `username`/`password` on every host from `DEVICE_USERNAME` / `DEVICE_PASSWORD`, or prompts (password hidden via `getpass`).
- Prefer exporting the variables from a password manager for the session over writing them in shell profiles; never put them in `config.yaml`, inventory files or tests (tests use obviously fake `lab-user`/`lab-pass`).
- Enable secrets, if a future script needs them, go in `host.connection_options["netmiko"].extras["secret"]`, set in `init_nornir()` from an environment variable.
- Never log credentials; Nornir's log (`logs/nornir.log`) records task results, so do not include secrets in result strings.

## Sensitive output

- Running configs contain password hashes, SNMP communities, keys and TACACS/RADIUS secrets. `backups/`, `reports/` and `logs/` are gitignored; keep it that way and never force-add files from them.
- Treat `compliance.csv` as internal: it reveals which devices are missing hardening controls.

## Device safety

- Both scripts send only `show` commands. Any future write path (config push) must default to a dry run, show a diff, save the pre-change config, and require an explicit `--commit` flag.
- Connections run in parallel (`runner.options.num_workers: 10`); lower it for fragile or rate-limited devices.
- Host key checking follows Netmiko defaults; do not disable it globally.

## Supply chain

`requirements.txt` uses minimum versions (`>=`). For repeatable installs, pin versions (e.g. `pip freeze > requirements.lock` from a tested venv) and run `pip-audit -r requirements.txt` before releases.
