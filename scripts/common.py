"""
common.py
Shared setup for the automation scripts: initialise Nornir from the repo's
config.yaml and inject device credentials at runtime (never from inventory files).
"""

import getpass
import os
from pathlib import Path

import yaml
from nornir import InitNornir
from nornir.core import Nornir

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = REPO_ROOT / "config.yaml"


def get_credentials() -> tuple[str, str]:
    """Return (username, password) from DEVICE_USERNAME / DEVICE_PASSWORD, prompting if unset."""
    username = os.environ.get("DEVICE_USERNAME") or input("Device username: ")
    password = os.environ.get("DEVICE_PASSWORD") or getpass.getpass("Device password: ")
    if not username or not password:
        raise SystemExit("Device username and password are required.")
    return username, password


def load_config(config_file: Path = CONFIG_FILE) -> dict:
    """Read config.yaml and resolve its relative paths against the config file's directory."""
    base = config_file.resolve().parent
    cfg = yaml.safe_load(config_file.read_text()) or {}
    options = cfg.get("inventory", {}).get("options", {})
    for key in ("host_file", "group_file", "defaults_file"):
        if key in options:
            options[key] = str(base / options[key])
    logging_cfg = cfg.get("logging", {})
    if logging_cfg.get("enabled") and logging_cfg.get("log_file"):
        log_file = base / logging_cfg["log_file"]
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logging_cfg["log_file"] = str(log_file)
    return cfg


def init_nornir(config_file: Path = CONFIG_FILE, credentials: tuple[str, str] | None = None) -> Nornir:
    """Create a Nornir object from config.yaml and apply device credentials to every host."""
    nr = InitNornir(**load_config(config_file))
    username, password = credentials or get_credentials()
    for host in nr.inventory.hosts.values():
        host.username = username
        host.password = password
    return nr
