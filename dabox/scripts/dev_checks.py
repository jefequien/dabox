#!/usr/bin/env python
"""Runs formatting, linting, and type checking tests."""

import tyro
from rich import console

from dabox.util.subprocess import run_command

CONSOLE = console.Console()

TYPE_TESTS = ["mypy ."]
FORMAT_TESTS = ["ruff check --fix .", "ruff format ."]


def run_code_checks(
    skip_format_checks: bool = False,
    skip_type_checks: bool = False,
):
    """Runs formatting, linting, and type checking tests.

    Args:
        skip_format_checks: Whether or not to skip format tests.
        skip_type_checks: Whether or not to skip type tests.
    """

    assert (
        not skip_format_checks or not skip_type_checks
    ), "Cannot skip format and type tests at the same time."
    tests = []
    if not skip_format_checks:
        tests += FORMAT_TESTS
    if not skip_type_checks:
        tests += TYPE_TESTS

    for test in tests:
        CONSOLE.line()
        CONSOLE.rule(f"[bold green]Running: {test}")
        run_command(test)

    CONSOLE.line()
    CONSOLE.rule(characters="=")
    CONSOLE.print(
        "[bold green]:TADA: :TADA: :TADA: ALL CHECKS PASSED :TADA: :TADA: :TADA:",
        justify="center",
    )
    CONSOLE.rule(characters="=")


def entrypoint():
    """Entrypoint for use with pyproject scripts."""
    tyro.cli(run_code_checks)


if __name__ == "__main__":
    entrypoint()
