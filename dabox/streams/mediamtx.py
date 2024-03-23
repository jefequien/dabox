from pathlib import Path

from dabox.env import ASSETS_DIR, DABOX_CACHE_DIR, FFMPEG_INPUT_FORMAT, PLATFORM
from dabox.util.devices import get_device_infos
from dabox.util.logging import logger
from dabox.util.subprocess import run_command


def _install_mediamtx(mtx_version="v1.6.0") -> Path:
    mtx_install_dir = DABOX_CACHE_DIR / f"mediamtx_{mtx_version}"
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


def get_mediamtx_command() -> str:
    mediamtx_path = _install_mediamtx()
    mediamtx_config_path = ASSETS_DIR / "mediamtx.yml"
    mediamtx_command = f"{mediamtx_path} {mediamtx_config_path}"
    return mediamtx_command


def get_ffmpeg_commands() -> dict[str, str]:
    device_infos = get_device_infos()
    network_size = (640, 480)
    network_pkt_size = network_size[0] * network_size[1] * 3

    ffmpeg_commands = {}
    for device_info in device_infos:
        videos_dir = DABOX_CACHE_DIR / "videos" / device_info.stream_name
        videos_dir.mkdir(parents=True, exist_ok=True)

        ffmpeg_cmd = (
            f"ffmpeg -f {FFMPEG_INPUT_FORMAT} -loglevel fatal -framerate {device_info.frame_rate} -video_size {device_info.video_size[0]}x{device_info.video_size[1]} -pix_fmt {device_info.pixel_format} -i {device_info.name}"
            + f" -preset ultrafast -tune zerolatency -vcodec libx264 -b:v 1M -bf 0 -f rtsp rtsp://localhost:8554/{device_info.stream_name}"
            + f" -pix_fmt rgb24 -s {network_size[0]}x{network_size[1]} -pkt_size {network_pkt_size} -f rawvideo zmq:tcp://127.0.0.1:{device_info.zmq_port}"
            + f" -vcodec mjpeg -f segment -segment_time 60 -segment_format mp4 -reset_timestamps 1 -segment_atclocktime 1 -strftime 1 {videos_dir}/%Y-%m-%d-%H-%M-%S.mp4"
        )
        ffmpeg_commands[device_info.name] = ffmpeg_cmd
    return ffmpeg_commands
