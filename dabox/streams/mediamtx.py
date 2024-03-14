from pathlib import Path

from dabox.env import FFMPEG_INPUT_FORMAT, PLATFORM, ROOT_DIR, RTSP_PORT
from dabox.util.devices import get_stream_mapping
from dabox.util.logging import logger
from dabox.util.subprocess import run_command


def install_mediamtx(mtx_version="v1.6.0") -> Path:
    mtx_install_dir = ROOT_DIR / ".output" / f"mediamtx_{mtx_version}"
    mediamtx_path = mtx_install_dir / "mediamtx"
    if mediamtx_path.is_file():
        return mediamtx_path

    logger.info("Installing MediaMTX")
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


def get_ffmpeg_commands() -> dict[str, str]:
    stream_mapping = get_stream_mapping()
    frame_rate = 30
    video_size = "640x480"
    pixel_format = "yuyv422"
    # video_size = "1280x720"
    # pixel_format = "mjpeg"
    ffmpeg_commands = {}
    for stream_name, device_name in stream_mapping.items():
        ffmpeg_cmd = f"ffmpeg -f {FFMPEG_INPUT_FORMAT} -loglevel error -framerate {frame_rate} -video_size {video_size} -pix_fmt {pixel_format} -i /dev/video0" + \
            " -preset ultrafast -tune zerolatency  -pix_fmt rgb24 -pkt_size 921600 -f rawvideo zmq:tcp://127.0.0.1:5556" + \
            " -preset ultrafast -tune zerolatency -b:v 1M -vcodec libx264 -bf 0 -f rtsp rtsp://localhost:8554/camera0"
        ffmpeg_commands[stream_name] = ffmpeg_cmd
    return ffmpeg_commands
