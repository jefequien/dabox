from dabox.util.logging import logger
from dabox.util.subprocess import run_command


def main():
    ports = [
        8000,  # MediaMTX
        8080,  # Viser
    ]
    # ZMQ ports
    for i in range(10):
        ports.append(5555 + i)

    for port in ports:
        logger.info(f"Killing processes on port: {port}")
        run_command(f"kill $(lsof -t -i:{port})", continue_on_fail=True)
