"""Offline tests: no device connections. Netmiko calls are replaced with canned output."""

import csv
import sys
from pathlib import Path

import pytest
from nornir.core.task import Result

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import backup_configs
import common
import compliance_check

CREDS = ("lab-user", "lab-pass")


@pytest.fixture
def nr(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # prove paths do not depend on the current directory
    return common.init_nornir(credentials=CREDS)


def test_config_loads_inventory_from_any_directory(nr):
    assert sorted(nr.inventory.hosts) == ["access-sw-01", "core-sw-01", "core-sw-02", "dist-sw-01"]
    assert nr.inventory.hosts["dist-sw-01"].platform == "cisco_nxos"
    assert nr.inventory.hosts["core-sw-01"]["role"] == "core"


def test_credentials_are_injected_not_templated(nr):
    for host in nr.inventory.hosts.values():
        assert (host.username, host.password) == CREDS


def test_get_credentials_from_environment(monkeypatch):
    monkeypatch.setenv("DEVICE_USERNAME", "u")
    monkeypatch.setenv("DEVICE_PASSWORD", "p")
    assert common.get_credentials() == ("u", "p")


def test_evaluate_must_contain_and_must_not_contain():
    check = {"name": "x", "must_contain": ["ip ssh version 2"], "must_not_contain": ["telnet"]}
    assert compliance_check.evaluate("h", check, "ip ssh version 2") == []
    violations = compliance_check.evaluate("h", check, "transport input telnet")
    assert [v["expected"] for v in violations] == ["ip ssh version 2", "NOT 'telnet'"]


def fake_send(outputs):
    def _send(task, command_string, **_):
        return Result(host=task.host, result=outputs.get(command_string, ""))

    return _send


def test_compliance_run_and_report(nr, monkeypatch, tmp_path):
    compliant = {
        "show running-config | include ntp": "ntp server 192.0.2.1",
        "show running-config | include ip ssh": "ip ssh version 2",
        "show line vty 0 4": "transport input ssh",
        "show running-config | include banner": "banner login ^C",
        "show running-config | include service password": "service password-encryption",
        "show running-config | include snmp-server community": "",
    }
    monkeypatch.setattr(compliance_check, "netmiko_send_command", fake_send(compliant))
    nr.run(task=compliance_check.check_compliance, policy=compliance_check.load_policy())
    assert all(h.get("violations") == [] for h in nr.inventory.hosts.values())

    bad = dict(compliant)
    bad["show running-config | include snmp-server community"] = "snmp-server community public RO"
    monkeypatch.setattr(compliance_check, "netmiko_send_command", fake_send(bad))
    nr.run(task=compliance_check.check_compliance, policy=compliance_check.load_policy())
    violations = [v for h in nr.inventory.hosts.values() for v in h["violations"]]
    assert len(violations) == 4 and {v["check"] for v in violations} == {"SNMP community strings"}

    report = tmp_path / "out" / "c.csv"
    compliance_check.write_report(violations, report)
    rows = list(csv.DictReader(report.open()))
    assert rows[0].keys() == {"host", "check", "expected", "status"} and len(rows) == 4


def test_backup_writes_timestamped_file(nr, monkeypatch, tmp_path):
    fake = fake_send({"show running-config": "hostname R1"})
    monkeypatch.setattr(backup_configs, "netmiko_send_command", fake)
    result = nr.filter(name="core-sw-01").run(task=backup_configs.backup_device, backup_dir=tmp_path)
    assert not result.failed
    files = list((tmp_path / "core-sw-01").glob("core-sw-01_*.cfg"))
    assert len(files) == 1 and files[0].read_text() == "hostname R1"
