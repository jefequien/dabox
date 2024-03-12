"""Run commands with python subprocess module."""

import subprocess
import sys

from rich import console

CONSOLE = console.Console()


def run_command(
    command: str, continue_on_fail: bool = False, background: bool = False
) -> bool:
    """Run a command kill actions if it fails

    Args:
        command: Command to run.
        continue_on_fail: Whether to continue running commands if the current one fails..
    """
    if background:
        subprocess.Popen(command, shell=True)
        return True

    ret_code = subprocess.call(command, shell=True)
    if ret_code != 0:
        CONSOLE.print(f"[bold red]Error: `{command}` failed.")
        if not continue_on_fail:
            sys.exit(1)
    return ret_code == 0
