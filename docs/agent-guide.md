# Agent guide

## First fixes (in order)

1. Convert `config.yaml` to Nornir 3 format (see CLAUDE.md).
2. Replace the `{{ env.DEVICE_PASSWORD }}` placeholder with runtime injection (see security.md).
3. Make the README match the code, or implement the missing scripts.

## Recipes

**Add a compliance check**: append to `templates/baseline_policy.yaml`:
```yaml
  - name: AAA new-model enabled
    command: show running-config | include aaa new-model
    must_contain:
      - "aaa new-model"
```
Use the narrowest `show ... | include` that captures the line, because matching is a substring test.

**Add a device**: add it to `inventory/hosts.yaml` with one platform group (`cisco_ios` or `cisco_nxos`) and one role group. Use documentation/lab IPs in committed examples.

**Add a script**: put it in `scripts/`, follow the existing shape (task function + `main()` + Rich table), read `config.yaml` relative to the repo root, write output under a gitignored directory, and send only read-only commands unless the user asked for writes.

**Implement `push_config.py` (README promise)**: render a Jinja2 template per host, show the rendered config, require a `--commit` flag to send it with `netmiko_send_config`, and save the pre-change running config first.

## Pitfalls

- `compliance_check.py` stores violations in host data (`task.host["violations"]`) and reads them back from `nr.inventory`; keep that if you refactor, or return them through `Result`.
- NX-OS output differs from IOS (e.g. `show line vty 0 4` does not exist on NX-OS); platform-specific checks need a filter on `task.host.platform`.
- The README's `--report` flag does not exist; the script uses `sys.argv[1]`. Switch to `argparse` if you touch the CLI.

## Done means

Config loads, ruff passes, any new logic has an offline test, and README/docs are accurate.
