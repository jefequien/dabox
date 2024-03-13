"""Dabox entrypoint"""

import subprocess
import time

from rich import console

from dabox.streams.mediamtx import start_camera_processes, start_mediamtx_process
from dabox.util.cli_logo import cli_logo
from dabox.util.logging import logger
from dabox.util.subprocess import (
    interrupt_ipc_subprocess,
    open_ipc_subprocess,
)

CONSOLE = console.Console()

_SUBPROCESS_WAIT_TIMEOUT = 10
_CHECK_SUBPROCESS_INTERVAL = 5


def main():
    cli_logo()
    camera_processes = start_camera_processes()
    mediamtx_process = start_mediamtx_process()
    time.sleep(1)
    gui_process = open_ipc_subprocess("python -m dabox.gui")

    try:
        while True:
            time.sleep(_CHECK_SUBPROCESS_INTERVAL)

            for camera_process in camera_processes:
                if camera_process.poll() is not None:
                    raise Exception(
                        "camera process shut down unexpectedly with return code"
                        f" {camera_process.returncode}"
                    )

            if mediamtx_process.poll() is not None:
                raise Exception(
                    "mediamtx process shut down unexpectedly with return code"
                    f" {mediamtx_process.returncode}"
                )

            if gui_process.poll() is not None:
                raise Exception(
                    "gui process shut down unexpectedly with return code"
                    f" {gui_process.returncode}"
                )

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received")
    except Exception:
        logger.exception("An unexpected exception has occurred")
    finally:
        logger.info("Shutting down DaBox services...")
        for camera_process in camera_processes:
            interrupt_ipc_subprocess(camera_process)
        interrupt_ipc_subprocess(mediamtx_process)
        interrupt_ipc_subprocess(gui_process)

        for camera_process in camera_processes:
            try:
                camera_process.wait(timeout=_SUBPROCESS_WAIT_TIMEOUT)
            except subprocess.TimeoutExpired:
                logger.warning(
                    "camera process did not terminate cleanly, killing the process"
                )
                camera_process.kill()

        try:
            mediamtx_process.wait(timeout=_SUBPROCESS_WAIT_TIMEOUT)
        except subprocess.TimeoutExpired:
            logger.warning(
                "mediamtx process did not terminate cleanly, killing the process"
            )
            mediamtx_process.kill()

        try:
            gui_process.wait(timeout=_SUBPROCESS_WAIT_TIMEOUT)
        except subprocess.TimeoutExpired:
            logger.warning("gui process did not terminate cleanly, killing the process")
            gui_process.kill()

        logger.info("DaBox services shut down.")


if __name__ == "__main__":
    main()
