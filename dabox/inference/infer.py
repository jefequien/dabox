import cv2
import numpy as np
import zmq
from tqdm import tqdm

from dabox.util.projection import backproject_depth

from .yolov8.yolov8 import YOLOv8


def main():
    yolov8_detector = YOLOv8("yolov8n.onnx", conf_thres=0.5, iou_thres=0.5)

    context = zmq.Context()
    # Subscribe to camera0
    sub_socket = context.socket(zmq.SUB)
    sub_socket.subscribe("")
    sub_socket.setsockopt(zmq.CONFLATE, 1)  # Always get last message
    sub_socket.connect("tcp://127.0.0.1:5556")

    # Bind to publish port
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:5555")

    K = np.array([[0.5, 0.0, 0.5], [0.0, 0.667, 0.5], [0.0, 0.0, 1.0]])
    w, h = (640, 480)
    depth_size = (80, 60)
    for _ in tqdm(range(10000000)):
        payload = sub_socket.recv()
        image = np.frombuffer(payload, np.uint8).reshape((h, w, 3))

        boxes, scores, labels = yolov8_detector(image)

        # Make fake point cloud
        colors = cv2.resize(image, depth_size)
        depth = np.ones(colors.shape[:2]) * 10.0
        points = backproject_depth(depth, K).astype(np.float16)
        colors = colors.reshape((-1, 3)).astype(np.uint8)

        out = {
            "boxes": boxes,
            "scores": scores,
            "labels": labels,
            "points": points,
            "colors": colors,
        }
        socket.send_pyobj(out)
