"""Viser GUI"""

import numpy as np
import viser
import zmq
from transformations import quaternion_from_matrix

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
    sub_socket = context.socket(zmq.SUB)
    sub_socket.subscribe("")
    sub_socket.setsockopt(zmq.LINGER, 0)  # Stop immediately after socket is closed
    sub_socket.setsockopt(zmq.CONFLATE, 1)  # Always get last message
    sub_socket.connect("tcp://127.0.0.1:5555")

    while True:
        out = sub_socket.recv_pyobj()
        for camera_name, camera_out in out.items():
            w, h = camera_out["image_size"]
            K = camera_out["K"]
            camera_mat = camera_out["camera_mat"]
            boxes = camera_out["boxes"]
            scores = camera_out["scores"]
            labels = camera_out["labels"]
            points = camera_out["points"]
            colors = camera_out["colors"]

            image = np.zeros((h, w, 3), dtype=np.uint8)
            image_vis = draw_detections(image, boxes, scores, labels)

            # Place point cloud.
            server.add_point_cloud(
                f"/{camera_name}/points_main",
                points=points,
                colors=colors,
                point_size=0.1,
            )

            # Place the frustum.
            fov = 2 * np.arctan2(h / 2, K[1, 1] * h)
            server.add_camera_frustum(
                f"/{camera_name}/frames/t0/frustum",
                fov=fov,
                aspect=w / h,
                scale=0.15,
                image=image_vis,
                wxyz=quaternion_from_matrix(camera_mat),
                position=camera_mat[:3, 3],
            )


if __name__ == "__main__":
    main()
