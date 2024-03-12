"""Dabox entrypoint"""

import re
from pathlib import Path

from rich import console

from dabox.env import FFMPEG_INPUT_FORMAT, PLATFORM, ROOT_DIR, RTSP_PORT
from dabox.gui.gui import start_gui
from dabox.util.cli_logo import cli_logo
from dabox.util.subprocess import run_command, run_command_and_capture_output

CONSOLE = console.Console()


def get_input_devices() -> list[str]:
    if PLATFORM == "linux":
        list_devices_str = run_command_and_capture_output("v4l2-ctl --list-devices")
        devices = [
            x.group().strip() for x in re.finditer(r"/dev(.*?)\n", list_devices_str)
        ]
    elif PLATFORM == "osx":
        # Only support one camera on Mac
        devices = ["0"]
    else:
        raise ValueError(f"Platform not recognized: {PLATFORM}")
    return devices


def install_mediamtx(mtx_version="v1.6.0") -> Path:
    mtx_install_dir = ROOT_DIR / ".output" / f"mediamtx_{mtx_version}"
    mediamtx_path = mtx_install_dir / "mediamtx"
    if mediamtx_path.is_file():
        return mediamtx_path

    CONSOLE.print("Installing MediaMTX")
    mtx_install_dir.mkdir(parents=True, exist_ok=True)
    if PLATFORM == "linux":
        mtx_platform = "linux_amd64"
        run_command(
            f"wget -nc -O {mtx_install_dir}/mediamtx.tar.gz https://github.com/bluenviron/mediamtx/releases/download/{mtx_version}/mediamtx_{mtx_version}_{mtx_platform}.tar.gz"
        )
        run_command(
            f"tar -xf {mtx_install_dir}/mediamtx.tar.gz --directory {mtx_install_dir}"
        )
    return mediamtx_path


def start_mediamtx_server():
    mediamtx_path = install_mediamtx()
    run_command_and_capture_output(str(mediamtx_path), background=True)


def start_cameras():
    input_devices = get_input_devices()
    for idx, input_device in enumerate(input_devices):
        mtx_path = f"camera{idx}"
        ffmpeg_cmd = f"ffmpeg -loglevel error -f {FFMPEG_INPUT_FORMAT} -framerate 30 -video_size 640x480 -pix_fmt yuyv422 -i {input_device} -preset ultrafast -tune zerolatency -b:v 1M -c:v libx264 -bf 0 -f rtsp rtsp://localhost:{RTSP_PORT}/{mtx_path}"
        run_command_and_capture_output(ffmpeg_cmd, background=True)


def main():
    cli_logo()

    start_mediamtx_server()
    start_cameras()
    start_gui()


if __name__ == "__main__":
    main()
