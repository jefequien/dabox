"""Dabox entrypoint"""

import time

from dabox.env import ROOT_DIR
from dabox.util.cli_logo import cli_logo
from dabox.util.subprocess import run_command


def start_mediamtx_server():
    MEDIAMTX_INSTALL_DIR = ROOT_DIR / ".output" / "mediamtx_downloads"
    mediamtx_cmd = f"{MEDIAMTX_INSTALL_DIR}/mediamtx"
    run_command(mediamtx_cmd, background=True)


def start_cameras():
    FFMPEG_INPUT_FORMAT = "v4l2"
    RTSP_PORT = 8554
    input_devices = [
        "/dev/video0",
        "/dev/video2",
    ]
    for idx, input_device in enumerate(input_devices):
        mtx_path = f"camera{idx}"
        ffmpeg_cmd = f"ffmpeg -f {FFMPEG_INPUT_FORMAT} -framerate 30 -video_size 640x480 -pix_fmt yuyv422 -i {input_device} -preset ultrafast -tune zerolatency -b:v 1M -c:v libx264 -bf 0 -f rtsp rtsp://localhost:{RTSP_PORT}/{mtx_path}"
        run_command(ffmpeg_cmd, background=True)


def main():
    cli_logo()

    start_mediamtx_server()
    start_cameras()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
