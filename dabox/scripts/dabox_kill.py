from dabox.util.logging import logger
from dabox.util.subprocess import (
    run_command,
)


def main():
    ports = [
        8000,  # MediaMTX
        8080,  # Viser
    ]
    # ZMQ ports
    for i in range(10):
        ports.append(5555 + i)

    for port in ports:
        logger.info(f"Checking for processes on port: {port}")
        lsof_output = run_command(f"lsof -t -i:{port}", continue_on_fail=True)
        if len(lsof_output) != 0:
            logger.info(f"Killing processes: {lsof_output}")
            run_command(f"kill {lsof_output})", continue_on_fail=True)
