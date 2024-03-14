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
    processes = start_camera_processes()
    processes["mediamtx"] = start_mediamtx_process()
    processes["inference"] = open_ipc_subprocess("python -m dabox.inference")
    processes["gui"] = open_ipc_subprocess("python -m dabox.gui")

    try:
        while True:
            time.sleep(_CHECK_SUBPROCESS_INTERVAL)

            for process_name, process in processes.items():
                if process.poll() is not None:
                    raise Exception(
                        f"{process_name} process shut down unexpectedly with return code"
                        f" {process.returncode}"
                    )

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received")
    except Exception:
        logger.exception("An unexpected exception has occurred")
    finally:
        logger.info("Shutting down DaBox services...")
        for _, process in processes.items():
            interrupt_ipc_subprocess(process)

        for process_name, process in processes.items():
            try:
                process.wait(timeout=_SUBPROCESS_WAIT_TIMEOUT)
            except subprocess.TimeoutExpired:
                logger.warning(
                    f"{process_name} process did not terminate cleanly, killing the process"
                )
                process.kill()

        logger.info("DaBox services shut down.")


if __name__ == "__main__":
    main()
