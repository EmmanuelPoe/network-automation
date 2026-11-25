# Testing

There are no tests and no CI. Use these layers, cheapest first.

## 1. Static checks

```bash
pip install ruff
ruff check scripts && ruff format --check scripts
python -c "import yaml,sys; [yaml.safe_load(open(f)) for f in sys.argv[1:]]" config.yaml inventory/*.yaml templates/*.yaml
```

## 2. Config loads (no devices needed)

```bash
python -c "from nornir import InitNornir; nr = InitNornir(config_file='config.yaml'); print(list(nr.inventory.hosts))"
```

This currently fails with the Nornir 2 config error described in CLAUDE.md; it should print the four host names once fixed.

## 3. Unit tests without devices (recommended to add)

Mock `netmiko_send_command` so tasks run offline. A minimal pattern with pytest:

```python
from nornir.core.task import Result

def fake_send(task, command_string, **_):
    outputs = {"show running-config | include ip ssh": "ip ssh version 2"}
    return Result(host=task.host, result=outputs.get(command_string, ""))

def test_ssh_v2_passes(monkeypatch, nr):           # nr = fixture building InitNornir from a tmp inventory
    import scripts.compliance_check as cc
    monkeypatch.setattr(cc, "netmiko_send_command", fake_send)
    ...
```

Good first tests: `must_contain`/`must_not_contain` logic in `check_compliance`, CSV columns, and the backup file naming.

## 4. Against lab devices

Use Cisco DevNet sandboxes, CML or containerlab images, with a separate inventory file. Never point tests at production devices.
