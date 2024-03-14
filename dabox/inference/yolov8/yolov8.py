import numpy as np
import onnxruntime

from dabox.env import ROOT_DIR
from dabox.util.subprocess import run_command

from .utils import multiclass_nms, xywh2xyxy


class YOLOv8:
    def __init__(self, model_name, conf_thres=0.7, iou_thres=0.5):
        self.model_name = model_name
        self.conf_threshold = conf_thres
        self.iou_threshold = iou_thres

        model_path = ROOT_DIR / ".output" / "models" / model_name
        if not model_path.is_file():
            model_path.parent.mkdir(parents=True, exist_ok=True)
            download_url = "https://github.com/jefequien/dabox-research/releases/download/v0.2.0/yolov8n.onnx"
            run_command(f"wget -nc -O {model_path} {download_url}")

        # Initialize model
        self.initialize_model(model_path)

    def __call__(self, image):
        input_tensor = self.prepare_input(image)
        assert (
            input_tensor.shape == self.input_shape
        ), f"{input_tensor.shape} must match {self.input_shape}"

        outputs = self.session.run(
            self.output_names, {self.input_names[0]: input_tensor}
        )
        boxes, scores, class_ids = self.process_output(outputs)
        return boxes, scores, class_ids

    def initialize_model(self, path):
        self.session = onnxruntime.InferenceSession(
            path, providers=onnxruntime.get_available_providers()
        )
        # Get model info
        model_inputs = self.session.get_inputs()
        model_outputs = self.session.get_outputs()
        self.input_shape = tuple(model_inputs[0].shape)
        self.input_names = [model_inputs[i].name for i in range(len(model_inputs))]
        self.output_names = [model_outputs[i].name for i in range(len(model_outputs))]

    def prepare_input(self, image):
        # Scale input pixel values to 0 to 1
        input_img = image / 255.0
        input_img = input_img.transpose(2, 0, 1)
        input_tensor = input_img[np.newaxis, :, :, :].astype(np.float32)
        return input_tensor

    def process_output(self, output):
        predictions = np.squeeze(output[0]).T

        # Filter out object confidence scores below threshold
        scores = np.max(predictions[:, 4:], axis=1)
        predictions = predictions[scores > self.conf_threshold, :]
        scores = scores[scores > self.conf_threshold]

        if len(scores) == 0:
            return [], [], []

        # Get the class with the highest confidence
        class_ids = np.argmax(predictions[:, 4:], axis=1)

        # Get bounding boxes for each object
        boxes = predictions[:, :4]
        boxes = xywh2xyxy(boxes)

        # Apply non-maxima suppression to suppress weak, overlapping bounding boxes
        # indices = nms(boxes, scores, self.iou_threshold)
        indices = multiclass_nms(boxes, scores, class_ids, self.iou_threshold)
        return boxes[indices], scores[indices], class_ids[indices]
