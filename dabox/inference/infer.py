import numpy as np
import onnxruntime
import zmq
from tqdm import tqdm

from dabox.env import DABOX_CACHE_DIR
from dabox.util.projection import backproject_depth
from dabox.util.subprocess import run_command


def main():
    context = zmq.Context()

    # Subscribe to cameras
    camera_names = ["camera0", "camera1"]
    sub_sockets = []
    for zmq_port in ["5556", "5557"]:
        sub_socket = context.socket(zmq.SUB)
        sub_socket.subscribe("")
        sub_socket.setsockopt(zmq.CONFLATE, 1)  # Always get last message
        sub_socket.connect(f"tcp://127.0.0.1:{zmq_port}")
        sub_sockets.append(sub_socket)

    # Bind to publish port
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:5555")

    model_name = "dabox_yolov8m.onnx"
    onnx_path = DABOX_CACHE_DIR / "onnx" / model_name
    if not onnx_path.is_file():
        onnx_path.parent.mkdir(parents=True, exist_ok=True)
        download_url = f"https://github.com/jefequien/dabox-research/releases/download/v0.2.1/{model_name}"
        run_command(f"wget -nc -O {onnx_path} {download_url}")

    providers = onnxruntime.get_available_providers()
    # Disable Tensorrt because it is slow to startup
    if "TensorrtExecutionProvider" in providers:
        providers.remove("TensorrtExecutionProvider")
    session = onnxruntime.InferenceSession(onnx_path, providers=providers)
    input_names = [model_input.name for model_input in session.get_inputs()]
    output_names = [model_output.name for model_output in session.get_outputs()]

    K = np.array([[0.5, 0.0, 0.5], [0.0, 0.667, 0.5], [0.0, 0.0, 1.0]])
    w, h = (640, 480)
    for _ in tqdm(range(10000000)):
        images = []
        for sub_socket in sub_sockets:
            payload = sub_socket.recv()
            image = np.frombuffer(payload, np.uint8).reshape((h, w, 3))
            images.append(image)

        out = []
        for camera_name, image in zip(camera_names, images):
            inputs = {
                input_name: input_tensor
                for input_name, input_tensor in zip(input_names, [image])
            }
            output_tensors = session.run(output_names, inputs)
            outputs = {
                output_name: output_tensor
                for output_name, output_tensor in zip(output_names, output_tensors)
            }

            boxes = outputs["det_bboxes"][0]
            scores = outputs["det_scores"][0]
            labels = outputs["det_classes"][0]

            # Make fake point cloud
            camera_pose = np.eye(4)
            colors = image[::8, ::8, :]  # Downsampling
            depth = np.ones(colors.shape[:2]) * 10.0
            points = backproject_depth(depth, K)
            colors = colors.reshape((-1, 3))

            if camera_name == "camera1":
                camera_pose[:3, 3] += np.ones(3)
                points += np.ones(3)

            camera_out = {
                "boxes": boxes,
                "scores": scores,
                "labels": labels,
                "camera_pose": camera_pose,
                "points": points,
                "colors": colors,
            }
            out.append(camera_out)
        socket.send_pyobj(out)
