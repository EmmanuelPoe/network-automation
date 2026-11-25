# Agent guide

## Recipes

**Add a compliance check**: append to `templates/baseline_policy.yaml`:
```yaml
  - name: AAA new-model enabled
    command: show running-config | include aaa new-model
    must_contain:
      - "aaa new-model"
```
Use the narrowest `show ... | include` that captures the line, because matching is a substring test. If the check is IOS-only, see the NX-OS pitfall below. Extend `test_compliance_run_and_report` or add a focused test.

**Add a device**: add it to `inventory/hosts.yaml` with one platform group (`cisco_ios` or `cisco_nxos`) and one role group. Use documentation/lab IPs in committed examples, and update `test_config_loads_inventory_from_any_directory`.

**Add a script**: put it in `scripts/`, import `from common import REPO_ROOT, init_nornir`, write output under a gitignored directory relative to `REPO_ROOT`, send only read-only commands unless the user asked for writes, add `argparse` for options, and add an offline test.

**Implement config push (roadmap)**: render a Jinja2 template per host, show the rendered config and a diff against the current running config, save the pre-change config, and only send with `netmiko_send_config` when `--commit` is given. Default to dry run.

## Pitfalls

- `compliance_check.py` stores violations in host data (`task.host["violations"]`) and reads them back from `nr.inventory`; keep that if you refactor, or return them through `Result`.
- NX-OS output differs from IOS (e.g. `show line vty 0 4` does not exist on NX-OS); platform-specific checks need a filter on `task.host.platform` or a per-platform policy.
- Nornir warns about conflicting logging configuration under pytest; it is harmless.
- `init_nornir()` prompts when credentials are missing — pass `credentials=` in tests and non-interactive tools.

## Done means

`pytest -q` and ruff pass, new behavior has an offline test, README/docs are accurate, and no device output or credentials are staged.
