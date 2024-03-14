"""Viser GUI"""

import numpy as np
import viser
import zmq

from dabox.env import ROOT_DIR, WEBRTC_PORT
from dabox.util.devices import get_device_infos
from dabox.util.drawing import draw_detections

from .theme import setup_viser_theme


def main():
    """Start visualization server."""
    server = viser.ViserServer(label="DABOX")
    setup_viser_theme(server)

    stream_names = [device_info.stream_name for device_info in get_device_infos()]
    markdown_source = (ROOT_DIR / "dabox/gui/assets/video_streams.mdx").read_text()
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
        boxes = out["boxes"]
        scores = out["scores"]
        labels = out["labels"]

        image = np.zeros((h, w, 3), dtype=np.uint8)
        debug_vis = draw_detections(image, boxes, scores, labels)

        # Place point cloud.
        server.add_point_cloud(
            "/points_main",
            points=out["points"],
            colors=out["colors"],
            point_size=0.1,
        )

        # Place the frustum.
        fov = 2 * np.arctan2(h / 2, K[1, 1] * h)
        aspect = w / h
        server.add_camera_frustum(
            "/frames/t0/frustum",
            fov=fov,
            aspect=aspect,
            scale=0.15,
            image=debug_vis,
            wxyz=np.array([1.0, 0.0, 0.0, 0.0]),
            position=np.zeros(3),
        )

        # Add some axes.
        server.add_frame(
            "/frames/t0/frustum/axes",
            axes_length=0.05,
            axes_radius=0.005,
        )


if __name__ == "__main__":
    main()
