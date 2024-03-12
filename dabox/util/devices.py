import re

from dabox.env import PLATFORM
from dabox.util.subprocess import run_command_and_capture_output


def _get_device_names() -> list[str]:
    if PLATFORM == "linux":
        list_devices_str = run_command_and_capture_output("v4l2-ctl --list-devices")
        device_names = [
            x.group().strip() for x in re.finditer(r"/dev(.*?)\n", list_devices_str)
        ]
    elif PLATFORM == "osx":
        # Only support one camera on Mac
        device_names = ["0"]
    else:
        raise ValueError(f"Platform not recognized: {PLATFORM}")
    return device_names


def get_stream_mapping() -> dict[str, str]:
    device_names = _get_device_names()
    stream_mapping = {}
    for idx, device_name in enumerate(device_names):
        stream_name = f"camera{idx}"
        stream_mapping[stream_name] = device_name
    return stream_mapping
