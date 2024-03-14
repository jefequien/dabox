#!/usr/bin/env python
"""Runs formatting, linting, and type checking tests."""

from dabox.util.logging import logger
from dabox.util.subprocess import run_command

TYPE_TESTS = ["mypy ."]
FORMAT_TESTS = ["ruff check --fix .", "ruff format ."]


def run_preflight(
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
        logger.info(f"Running: {test}")
        run_command(test)

    logger.info("ALL CHECKS PASSED!!!")
