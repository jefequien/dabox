"""Run commands with python subprocess module."""

import subprocess
import sys

from rich import console

CONSOLE = console.Console()


def run_command(command: str, continue_on_fail: bool = False) -> bool:
    """Run a command kill actions if it fails

    Args:
        command: Command to run.
        continue_on_fail: Whether to continue running commands if the current one fails..
    """
    res = subprocess.run(command, shell=True, check=False)
    ret_code = res.returncode
    if ret_code != 0:
        CONSOLE.print(f"[bold red]Error: `{command}` failed.")
        if not continue_on_fail:
            sys.exit(1)
    return ret_code == 0


def run_command_and_capture_output(command: str, background: bool = False) -> str:
    if background:
        subprocess.Popen(command, shell=True)
        return ""

    res = subprocess.run(
        command, shell=True, capture_output=True, text=True, check=False
    )
    return res.stdout
