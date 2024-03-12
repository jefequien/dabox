"""Run commands with python subprocess module."""

import subprocess
import sys

from rich import console

CONSOLE = console.Console()


def run_command(command: str, background: bool = False) -> str:
    """Run a command kill actions if it fails

    Args:
        command: Command to run.
        background: Whether to background the command.
    """
    if background:
        subprocess.Popen(command, shell=True)
        return ""
    
    res = subprocess.run(command, shell=True, check=False)
    ret_code = res.returncode
    if ret_code != 0:
        CONSOLE.print(f"[bold red]Error: `{command}` failed.")
        sys.exit(1)
    return res.stdout
