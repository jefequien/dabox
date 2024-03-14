import cv2
import numpy as np
import zmq

from dabox.env import RTSP_PORT
from dabox.util.projection import backproject_depth

from .video_capture import VideoCapture
from .yolov8.yolov8 import YOLOv8


def main():
    vid = VideoCapture(f"rtsp://localhost:{RTSP_PORT}/camera0")
    yolov8_detector = YOLOv8("yolov8n.onnx", conf_thres=0.5, iou_thres=0.5)

    # Creates a socket instance
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:5555")

    K = np.array([[0.5, 0.0, 0.5], [0.0, 0.667, 0.5], [0.0, 0.0, 1.0]])
    debug_size = (640, 480)
    depth_size = (80, 60)
    while True:
        image = vid.read()

        _ = yolov8_detector(image)

        debug_vis = yolov8_detector.draw_detections(image)
        debug_vis = cv2.resize(debug_vis, debug_size, cv2.INTER_LINEAR)

        colors = cv2.resize(debug_vis, depth_size, cv2.INTER_LINEAR)
        depth = np.ones(colors.shape[:2]) * 10.0
        points = backproject_depth(depth, K)
        colors = colors.reshape((-1, 3))

        out = {
            "image": debug_vis,
            "points": points.astype(np.float16),
            "colors": colors.astype(np.uint8),
        }
        socket.send_pyobj(out)
