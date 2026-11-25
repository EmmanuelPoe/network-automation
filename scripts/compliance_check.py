"""
compliance_check.py
Audit network devices against a baseline policy.
Reports violations as a CSV and prints a summary table.

Usage:
    export DEVICE_USERNAME=admin DEVICE_PASSWORD=...
    python scripts/compliance_check.py [--report reports/compliance.csv]
"""

import argparse
import csv
from pathlib import Path

import yaml
from nornir_netmiko.tasks import netmiko_send_command
from rich.console import Console
from rich.table import Table

from common import REPO_ROOT, init_nornir

console = Console()
POLICY_FILE = REPO_ROOT / "templates" / "baseline_policy.yaml"
DEFAULT_REPORT = REPO_ROOT / "reports" / "compliance.csv"
FIELDS = ["host", "check", "expected", "status"]


def load_policy(policy_file: Path = POLICY_FILE) -> dict:
    with open(policy_file) as f:
        return yaml.safe_load(f)


def evaluate(host: str, check: dict, output: str) -> list[dict]:
    """Return violations for one check given the device's command output."""
    violations = []
    for required in check.get("must_contain", []):
        if required not in output:
            violations.append({"host": host, "check": check["name"], "expected": required, "status": "FAIL"})
    for forbidden in check.get("must_not_contain", []):
        if forbidden in output:
            violations.append(
                {"host": host, "check": check["name"], "expected": f"NOT '{forbidden}'", "status": "FAIL"}
            )
    return violations


def check_compliance(task, policy):
    violations = []
    for check in policy.get("checks", []):
        result = task.run(
            task=netmiko_send_command,
            command_string=check["command"],
        )
        violations.extend(evaluate(task.host.name, check, result.result))
    task.host["violations"] = violations


def write_report(violations: list[dict], report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(violations)


def main(report_path: Path = DEFAULT_REPORT):
    policy = load_policy()
    nr = init_nornir()

    console.print("[bold blue]Running compliance checks...[/bold blue]")
    results = nr.run(task=check_compliance, policy=policy)

    all_violations = []
    for host in nr.inventory.hosts.values():
        all_violations.extend(host.get("violations", []))

    write_report(all_violations, report_path)

    failed_hosts = [name for name, result in results.items() if result.failed]
    for name in failed_hosts:
        console.print(f"[red]{name}: could not be checked ({results[name].exception})[/red]")

    table = Table(title="Compliance Summary")
    table.add_column("Host", style="cyan")
    table.add_column("Check")
    table.add_column("Expected")
    table.add_column("Status")

    for v in all_violations:
        table.add_row(v["host"], v["check"], v["expected"], "[red]FAIL[/red]")

    if all_violations:
        console.print(table)
        console.print(f"\n[yellow]Report saved to {report_path}[/yellow]")
    elif not failed_hosts:
        console.print("[bold green]All devices passed compliance checks.[/bold green]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit devices against templates/baseline_policy.yaml")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="CSV output path")
    main(parser.parse_args().report)
