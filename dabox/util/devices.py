import re

from dabox.env import PLATFORM
from dabox.util.subprocess import run_command


def _get_device_names() -> list[str]:
    if PLATFORM == "linux":
        list_devices_str = run_command("v4l2-ctl --list-devices")
        all_video_device_names = [
            x.group().strip()
            for x in re.finditer(r"/dev/video(.*?)\n", list_devices_str)
        ]
        print(all_video_device_names)

        device_names = []
        for device_name in all_video_device_names:
            device_info_str = run_command(
                f"v4l2-ctl --device={device_name} --all"
            )
            if "Format Video Capture" in device_info_str:
                device_names.append(device_name)

    elif PLATFORM == "osx":
        # Only support one camera on Mac
        device_names = ["0"]
    else:
        raise ValueError(f"Platform not recognized: {PLATFORM}")

    # Verify device
    return device_names


def get_stream_mapping() -> dict[str, str]:
    device_names = _get_device_names()
    stream_mapping = {}
    for idx, device_name in enumerate(device_names):
        stream_name = f"camera{idx}"
        stream_mapping[stream_name] = device_name
    return stream_mapping
