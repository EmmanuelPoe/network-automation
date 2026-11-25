# Testing

```bash
pip install -r requirements-dev.txt
pytest -q                                          # 6 tests, offline
ruff check scripts tests && ruff format --check scripts tests
```

CI (`.github/workflows/ci.yml`, Python 3.11) runs the same three commands on every pull request and push to `main`.

## What `tests/test_scripts.py` covers

| Test | Checks |
|---|---|
| `test_config_loads_inventory_from_any_directory` | Nornir 3 config loads from a different working directory; hosts, platforms and role data are correct |
| `test_credentials_are_injected_not_templated` | every host gets the runtime credentials |
| `test_get_credentials_from_environment` | `DEVICE_USERNAME` / `DEVICE_PASSWORD` are read |
| `test_evaluate_must_contain_and_must_not_contain` | the policy matching rules |
| `test_compliance_run_and_report` | full Nornir run with mocked Netmiko: compliant output → no violations; `snmp-server community public` → one violation per host; CSV columns |
| `test_backup_writes_timestamped_file` | backup task writes `<host>/<host>_<timestamp>.cfg` with the device output |

## How mocking works

Each script imports `netmiko_send_command` into its own module, so tests replace it there:

```python
from nornir.core.task import Result

def fake_send(outputs):
    def _send(task, command_string, **_):
        return Result(host=task.host, result=outputs.get(command_string, ""))
    return _send

monkeypatch.setattr(compliance_check, "netmiko_send_command", fake_send({...}))
```

Build Nornir with `common.init_nornir(credentials=("lab-user", "lab-pass"))` so no prompt appears.

## Against lab devices

Use Cisco DevNet sandboxes, CML or containerlab images with a separate inventory file. Never point tests or ad-hoc runs at production devices.
