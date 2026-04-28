"""
compliance_check.py
Audit network devices against a baseline policy.
Reports violations as a CSV and prints a summary table.
"""
import csv
import sys
from pathlib import Path
import yaml
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from rich.console import Console
from rich.table import Table

console = Console()
POLICY_FILE = Path(__file__).parent.parent / "templates" / "baseline_policy.yaml"


def load_policy():
    with open(POLICY_FILE) as f:
        return yaml.safe_load(f)


def check_compliance(task, policy):
    violations = []
    for check in policy.get("checks", []):
        result = task.run(
            task=netmiko_send_command,
            command_string=check["command"],
        )
        for required in check.get("must_contain", []):
            if required not in result.result:
                violations.append({
                    "host": task.host.name,
                    "check": check["name"],
                    "expected": required,
                    "status": "FAIL",
                })
        for forbidden in check.get("must_not_contain", []):
            if forbidden in result.result:
                violations.append({
                    "host": task.host.name,
                    "check": check["name"],
                    "expected": f"NOT '{forbidden}'",
                    "status": "FAIL",
                })
    task.host["violations"] = violations


def main(report_path="reports/compliance.csv"):
    policy = load_policy()
    nr = InitNornir(config_file="config.yaml")

    console.print("[bold blue]Running compliance checks...[/bold blue]")
    nr.run(task=check_compliance, policy=policy)

    all_violations = []
    for host in nr.inventory.hosts.values():
        all_violations.extend(host.get("violations", []))

    Path(report_path).parent.mkdir(exist_ok=True)
    with open(report_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["host", "check", "expected", "status"])
        writer.writeheader()
        writer.writerows(all_violations)

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
    else:
        console.print("[bold green]All devices passed compliance checks.[/bold green]")


if __name__ == "__main__":
    report = sys.argv[1] if len(sys.argv) > 1 else "reports/compliance.csv"
    main(report)
