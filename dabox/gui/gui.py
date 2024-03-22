"""Viser GUI"""

import numpy as np
import viser
import zmq

from dabox.env import ASSETS_DIR, WEBRTC_PORT
from dabox.util.devices import get_device_infos
from dabox.util.drawing import draw_detections

from .theme import setup_viser_theme


def main():
    """Start visualization server."""
    server = viser.ViserServer(label="DABOX")
    setup_viser_theme(server)

    stream_names = [device_info.stream_name for device_info in get_device_infos()]
    markdown_source = (ASSETS_DIR / "video_streams.mdx").read_text()
    markdown_source = markdown_source.replace("$WEBRTC_PORT", str(WEBRTC_PORT))
    markdown_source = markdown_source.replace("$STREAM_NAMES", str(stream_names))
    server.add_gui_markdown(content=markdown_source)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.subscribe("")
    socket.setsockopt(zmq.CONFLATE, 1)  # Always get last message
    socket.connect("tcp://127.0.0.1:5555")

    w, h = (640, 480)
    K = np.array([[0.5, 0.0, 0.5], [0.0, 0.667, 0.5], [0.0, 0.0, 1.0]])
    while True:
        out = socket.recv_pyobj()
        for idx, camera_out in enumerate(out):
            boxes = camera_out["boxes"]
            scores = camera_out["scores"]
            labels = camera_out["labels"]
            camera_pose = camera_out["camera_pose"]
            points = camera_out["points"]
            colors = camera_out["colors"]

            image = np.zeros((h, w, 3), dtype=np.uint8)
            image_vis = draw_detections(image, boxes, scores, labels)

            # Place point cloud.
            server.add_point_cloud(
                f"/{idx}/points_main",
                points=points,
                colors=colors,
                point_size=0.1,
            )

            # Place the frustum.
            fov = 2 * np.arctan2(h / 2, K[1, 1] * h)
            aspect = w / h
            server.add_camera_frustum(
                f"/{idx}/frames/t0/frustum",
                fov=fov,
                aspect=aspect,
                scale=0.15,
                image=image_vis,
                wxyz=np.array([1.0, 0.0, 0.0, 0.0]),
                position=camera_pose[:3, 3],
            )


if __name__ == "__main__":
    main()
