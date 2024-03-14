"""Run commands with python subprocess module."""

import signal
import subprocess
import sys
from typing import Any

from .logging import logger


def run_command(command: str) -> str:
    """Run a command kill actions if it fails

    Args:
        command: Command to run.
    """
    res = subprocess.run(
        command, shell=True, capture_output=True, text=True, check=False
    )
    ret_code = res.returncode
    if ret_code != 0:
        logger.error(f"Run command failed: {command}")
        sys.exit(1)
    return res.stdout


def open_ipc_subprocess(command: str, **kwargs: Any) -> subprocess.Popen[Any]:
    """Sets the correct flags to support graceful termination."""
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

    parts = command.split(" ")
    return subprocess.Popen(
        parts,
        creationflags=creationflags,
        **kwargs,
    )


def interrupt_ipc_subprocess(proc: subprocess.Popen[Any]) -> None:
    """Send CTRL_BREAK on Windows, SIGINT on other platforms."""
    if sys.platform == "win32":
        proc.send_signal(signal.CTRL_BREAK_EVENT)
    else:
        proc.send_signal(signal.SIGINT)
