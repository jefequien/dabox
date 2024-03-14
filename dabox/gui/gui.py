"""Camera Visualizer

Connect to a RealSense camera, then visualize RGB-D readings as a point clouds. Requires
pyrealsense2.
"""

import numpy as np
import viser
import zmq
from tqdm import tqdm
from viser.theme import TitlebarButton, TitlebarConfig, TitlebarImage

from dabox.env import ROOT_DIR, WEBRTC_PORT
from dabox.util.devices import get_stream_mapping


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
        image_url_light="https://docs.nerf.studio/_static/imgs/logo.png",
        image_url_dark="https://docs.nerf.studio/_static/imgs/logo-dark.png",
        image_alt="DaBox Logo",
        href="https://docs.nerf.studio/",
    )
    titlebar_theme = TitlebarConfig(buttons=buttons, image=image)
    server.configure_theme(
        titlebar_content=titlebar_theme,
        control_layout="collapsible",
        control_width="medium",
        dark_mode=True,
        show_logo=True,
        show_share_button=False,
        brand_color=(230, 180, 30),
    )

    stream_names = list(get_stream_mapping().keys())
    markdown_source = (ROOT_DIR / "dabox/gui/assets/video_streams.mdx").read_text()
    markdown_source = markdown_source.replace("$WEBRTC_PORT", str(WEBRTC_PORT))
    markdown_source = markdown_source.replace("$STREAM_NAMES", str(stream_names))
    server.add_gui_markdown(content=markdown_source)

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://127.0.0.1:5555")
    socket.subscribe("")

    K = np.array([[0.5, 0.0, 0.5], [0.0, 0.667, 0.5], [0.0, 0.0, 1.0]])
    for _ in tqdm(range(10000000)):
        out = socket.recv_pyobj()
        image = out["image"]
        h, w = image.shape[:2]

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
            image=image,
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
