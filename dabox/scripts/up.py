"""Dabox entrypoint"""

from pathlib import Path

from rich import console

from dabox.env import FFMPEG_INPUT_FORMAT, PLATFORM, ROOT_DIR, RTSP_PORT
from dabox.gui.gui import start_gui
from dabox.util.cli_logo import cli_logo
from dabox.util.devices import get_stream_mapping
from dabox.util.subprocess import run_command, run_command_and_capture_output

CONSOLE = console.Console()


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
    elif PLATFORM == "osx":
        mtx_platform = "darwin_arm64"
        run_command(
            f"wget -nc -O {mtx_install_dir}/mediamtx.tar.gz https://github.com/bluenviron/mediamtx/releases/download/{mtx_version}/mediamtx_{mtx_version}_{mtx_platform}.tar.gz"
        )
        run_command(
            f"tar -xf {mtx_install_dir}/mediamtx.tar.gz --directory {mtx_install_dir}"
        )
    else:
        raise ValueError(f"Platform not recognized: {PLATFORM}")
    return mediamtx_path


def start_mediamtx_server():
    mediamtx_path = install_mediamtx()
    run_command_and_capture_output(str(mediamtx_path), background=True)


def start_cameras():
    stream_mapping = get_stream_mapping()
    frame_rate = 30
    video_size = "640x480"
    pixel_format = "yuyv422"
    for stream_name, device_name in stream_mapping.items():
        ffmpeg_cmd = f"ffmpeg -loglevel error -f {FFMPEG_INPUT_FORMAT} -framerate {frame_rate} -video_size {video_size} -pix_fmt {pixel_format} -i {device_name} -preset ultrafast -tune zerolatency -b:v 1M -c:v libx264 -bf 0 -f rtsp rtsp://localhost:{RTSP_PORT}/{stream_name}"
        run_command_and_capture_output(ffmpeg_cmd, background=True)


def main():
    cli_logo()

    start_mediamtx_server()
    start_cameras()
    start_gui()


if __name__ == "__main__":
    main()
