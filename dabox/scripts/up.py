"""Dabox entrypoint"""

import time
import re

from dabox.env import FFMPEG_INPUT_FORMAT, ROOT_DIR, RTSP_PORT, PLATFORM
from dabox.util.cli_logo import cli_logo
from dabox.util.subprocess import run_command_and_capture_output


def get_input_devices() -> list[str]:
    if PLATFORM == "linux":
        list_devices_str = run_command_and_capture_output("v4l2-ctl --list-devices")
        devices = [x.group().strip() for x in re.finditer(r'/dev(.*?)\n', list_devices_str)]
    elif PLATFORM == "osx":
        # Only support one camera on Mac
        devices = ["0"]
    else:
        raise ValueError(f"Platform not recognized: {PLATFORM}")
    return devices


def start_mediamtx_server():
    MEDIAMTX_INSTALL_DIR = ROOT_DIR / ".output" / "mediamtx_downloads"
    mediamtx_cmd = f"{MEDIAMTX_INSTALL_DIR}/mediamtx"
    run_command_and_capture_output(mediamtx_cmd, background=True)


def start_cameras():
    input_devices = get_input_devices()
    for idx, input_device in enumerate(input_devices):
        mtx_path = f"camera{idx}"
        ffmpeg_cmd = f"ffmpeg -f {FFMPEG_INPUT_FORMAT} -framerate 30 -video_size 640x480 -pix_fmt yuyv422 -i {input_device} -preset ultrafast -tune zerolatency -b:v 1M -c:v libx264 -bf 0 -f rtsp rtsp://localhost:{RTSP_PORT}/{mtx_path}"
        run_command_and_capture_output(ffmpeg_cmd, background=True)


def main():
    cli_logo()

    start_mediamtx_server()
    start_cameras()


if __name__ == "__main__":
    main()
