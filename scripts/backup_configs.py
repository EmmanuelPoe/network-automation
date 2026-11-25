"""
backup_configs.py
Backup running configurations from all devices in the inventory.
Saves timestamped files to backups/<host>/ (gitignored: configs contain secrets).

Usage:
    DEVICE_USERNAME=admin DEVICE_PASSWORD=... python scripts/backup_configs.py
"""

from datetime import datetime
from pathlib import Path

from nornir_netmiko.tasks import netmiko_send_command
from rich.console import Console
from rich.table import Table

from common import REPO_ROOT, init_nornir

console = Console()
BACKUP_DIR = REPO_ROOT / "backups"


def backup_device(task, backup_dir: Path = BACKUP_DIR):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result = task.run(
        task=netmiko_send_command,
        command_string="show running-config",
    )
    host_dir = backup_dir / task.host.name
    host_dir.mkdir(parents=True, exist_ok=True)
    backup_file = host_dir / f"{task.host.name}_{timestamp}.cfg"
    backup_file.write_text(result.result)
    task.host["backup_file"] = str(backup_file)


def main():
    BACKUP_DIR.mkdir(exist_ok=True)
    nr = init_nornir()

    console.print("[bold blue]Starting config backup for all devices...[/bold blue]")
    results = nr.run(task=backup_device)

    table = Table(title="Backup Results")
    table.add_column("Host", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("File")

    for host, result in results.items():
        if result.failed:
            table.add_row(host, "[red]FAILED[/red]", str(result.exception))
        else:
            table.add_row(host, "[green]OK[/green]", nr.inventory.hosts[host].get("backup_file", ""))

    console.print(table)


if __name__ == "__main__":
    main()
