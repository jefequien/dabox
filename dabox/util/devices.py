import re
from dataclasses import dataclass

from dabox.env import PLATFORM
from dabox.util.subprocess import run_command


@dataclass
class DeviceInfo:
    name: str
    frame_rate: int
    video_size: tuple[int, int]
    pixel_format: str
    stream_name: str
    zmq_port: int


def get_device_infos() -> list[DeviceInfo]:
    device_infos: list[DeviceInfo] = []
    if PLATFORM == "linux":
        list_devices_str = run_command("v4l2-ctl --list-devices")
        device_names_all = [
            x.group().strip()
            for x in re.finditer(r"/dev/video(.*?)\n", list_devices_str)
        ]
        # Filter for physical cameras
        device_names = []
        for device_name in device_names_all:
            device_info_str = run_command(f"v4l2-ctl --device={device_name} --all")
            if "Format Video Capture" in device_info_str:
                device_names.append(device_name)

        for idx, device_name in enumerate(device_names):
            device_info = DeviceInfo(
                name=device_name,
                frame_rate=30,
                video_size=(1280, 720),
                pixel_format="mjpeg",
                stream_name=f"camera{idx}",
                zmq_port=5556 + idx,
            )
            device_infos.append(device_info)

    elif PLATFORM == "osx":
        # Currently, we only support one camera on Mac
        device_names = ["0"]
        for idx, device_name in enumerate(device_names):
            device_info = DeviceInfo(
                name=device_name,
                frame_rate=30,
                video_size=(1280, 720),
                pixel_format="yuyv422",
                stream_name=f"camera{idx}",
                zmq_port=5556 + idx,
            )
            device_infos.append(device_info)
    else:
        raise ValueError(f"Platform not recognized: {PLATFORM}")

    return device_infos
