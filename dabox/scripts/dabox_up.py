"""Dabox entrypoint"""

import subprocess
import time

from dabox.streams.mediamtx import get_ffmpeg_commands, install_mediamtx
from dabox.util.cli_logo import cli_logo
from dabox.util.logging import logger
from dabox.util.subprocess import (
    interrupt_ipc_subprocess,
    open_ipc_subprocess,
)

_SUBPROCESS_WAIT_TIMEOUT = 3
_CHECK_SUBPROCESS_INTERVAL = 5


def main():
    cli_logo()

    mediamtx_path = install_mediamtx()
    ffmpeg_commands = get_ffmpeg_commands()

    processes = {}
    for stream_name, ffmpeg_command in ffmpeg_commands.items():
        processes[stream_name] = open_ipc_subprocess(ffmpeg_command)
    processes["mediamtx"] = open_ipc_subprocess(str(mediamtx_path))
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
        logger.info("Shutting down DABOX services...")
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
                logger.info(f"Killed {process_name}")

        logger.info("DABOX services shut down.")


if __name__ == "__main__":
    main()
