"""Camera Visualizer

Connect to a RealSense camera, then visualize RGB-D readings as a point clouds. Requires
pyrealsense2.
"""

import numpy as np
import viser
import zmq
from viser.theme import TitlebarButton, TitlebarConfig, TitlebarImage

from dabox.env import ROOT_DIR, WEBRTC_PORT
from dabox.inference.yolov8.utils import draw_detections
from dabox.util.devices import get_device_names


def main():
    """Start visualization server."""
    server = viser.ViserServer(label="DaBox")
    buttons = (
        TitlebarButton(
            text="Github",
            icon="GitHub",
            href="https://github.com/jefequien/dabox",
        ),
        TitlebarButton(
            text="Documentation",
            icon="Description",
            href="https://github.com/jefequien/dabox",
        ),
    )
    image = TitlebarImage(
        image_url_light="https://github.com/jefequien/dabox/blob/main/docs/dabox-logo.png?raw=true",
        image_url_dark="https://github.com/jefequien/dabox/blob/main/docs/dabox-logo-dark.png?raw=true",
        image_alt="DABOX Logo",
        href="https://github.com/jefequien/dabox",
    )
    titlebar_theme = TitlebarConfig(buttons=buttons, image=image)
    server.configure_theme(
        titlebar_content=titlebar_theme,
        control_layout="collapsible",
        control_width="medium",
        dark_mode=False,
        show_logo=True,
        show_share_button=False,
        brand_color=(230, 180, 30),
    )

    device_names = get_device_names()
    stream_names = [f"camera{stream_id}" for stream_id in range(len(device_names))]
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
