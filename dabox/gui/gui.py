"""Camera Visualizer

Connect to a RealSense camera, then visualize RGB-D readings as a point clouds. Requires
pyrealsense2.
"""

import cv2
import numpy as np
import viser
from tqdm import tqdm
from viser.theme import TitlebarButton, TitlebarConfig, TitlebarImage

from dabox.env import ROOT_DIR, RTSP_PORT, WEBRTC_PORT
from dabox.util.devices import get_stream_mapping
from dabox.util.projection import backproject_depth
from dabox.util.video_capture import VideoCapture
from dabox.yolov8.yolov8 import YOLOv8


def start_gui():
    # Start visualization server.
    server = viser.ViserServer(label="DaBox")
    buttons = (
        TitlebarButton(
            text="Github",
            icon="GitHub",
            href="https://github.com/jefequien/DaBox",
        ),
        TitlebarButton(
            text="Documentation",
            icon="Description",
            href="https://github.com/jefequien/DaBox",
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

    # define a video capture object
    vid = VideoCapture(f"rtsp://localhost:{RTSP_PORT}/camera0")
    K = np.array([[0.5, 0.0, 0.5], [0.0, 0.667, 0.5], [0.0, 0.0, 1.0]])
    max_width = 80
    model_path = "./yolov8n.onnx"
    yolov8_detector = YOLOv8(model_path, conf_thres=0.5, iou_thres=0.5)

    for _ in tqdm(range(10000000)):
        frame = vid.read()

        # Update object localizer
        boxes, scores, class_ids = yolov8_detector(frame)
        frame = yolov8_detector.draw_detections(frame)

        image = frame[:, :, ::-1]
        h_ori, w_ori = image.shape[:2]
        w = min(w_ori, max_width)
        h = int(w * (h_ori / w_ori))

        colors = cv2.resize(image, (w, h), cv2.INTER_LINEAR)
        depth = np.ones(colors.shape[:2]) * 10.0
        points = backproject_depth(depth, K)
        colors = colors.reshape((-1, 3))

        # Place point cloud.
        server.add_point_cloud(
            "/points_main",
            points=points.astype(np.float16),
            colors=colors.astype(np.uint8),
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
    start_gui()
