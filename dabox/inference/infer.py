import cv2
import numpy as np
import zmq
from tqdm import tqdm

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
    depth_size = (80, 60)
    for _ in tqdm(range(10000000)):
        image = vid.read()
        boxes, scores, labels = yolov8_detector(image)

        colors = cv2.resize(image, depth_size, cv2.INTER_LINEAR)
        depth = np.ones(colors.shape[:2]) * 10.0
        points = backproject_depth(depth, K)
        colors = colors.reshape((-1, 3))

        out = {
            "image": image,
            "boxes": boxes,
            "scores": scores,
            "labels": labels,
            "points": points.astype(np.float16),
            "colors": colors.astype(np.uint8),
        }
        socket.send_pyobj(out)
