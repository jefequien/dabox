from pathlib import Path

from dabox.env import FFMPEG_INPUT_FORMAT, PLATFORM, ROOT_DIR
from dabox.util.devices import get_device_infos
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
    device_infos = get_device_infos()
    network_size = (640, 480)
    network_pix_fmt = "rgb24"
    network_pkt_size = network_size[0] * network_size[1] * 3

    ffmpeg_commands = {}
    for device_info in device_infos:
        ffmpeg_cmd = (
            f"ffmpeg -f {FFMPEG_INPUT_FORMAT} -loglevel error -framerate {device_info.frame_rate} -video_size {device_info.video_size[0]}x{device_info.video_size[1]} -pix_fmt {device_info.pixel_format} -i {device_info.name}"
            + f" -preset ultrafast -tune zerolatency -s {network_size[0]}x{network_size[1]} -pix_fmt {network_pix_fmt} -pkt_size {network_pkt_size} -f rawvideo zmq:tcp://127.0.0.1:{device_info.zmq_port}"
            + f" -preset ultrafast -tune zerolatency -b:v 1M -vcodec libx264 -bf 0 -f rtsp rtsp://localhost:8554/{device_info.stream_name}"
        )
        ffmpeg_commands[device_info.name] = ffmpeg_cmd
    return ffmpeg_commands
