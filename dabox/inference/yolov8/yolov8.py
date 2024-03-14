import numpy as np
import onnxruntime

from dabox.env import DABOX_CACHE_DIR
from dabox.util.subprocess import run_command


class YOLOv8:
    def __init__(self, model_name, conf_thres=0.7, iou_thres=0.5):
        self.model_name = model_name
        self.conf_threshold = conf_thres
        self.iou_threshold = iou_thres

        model_path = DABOX_CACHE_DIR / "models" / model_name
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
        providers = onnxruntime.get_available_providers()
        # Disable Tensorrt because it is slow to startup
        if "TensorrtExecutionProvider" in providers:
            providers.remove("TensorrtExecutionProvider")
        self.session = onnxruntime.InferenceSession(path, providers=providers)
        # Get model info
        model_inputs = self.session.get_inputs()
        model_outputs = self.session.get_outputs()
        self.input_shape = tuple(model_inputs[0].shape)
        self.input_names = [model_inputs[i].name for i in range(len(model_inputs))]
        self.output_names = [model_outputs[i].name for i in range(len(model_outputs))]

    def prepare_input(self, image):
        # Scale input pixel values to 0 to 1
        input_img = image.astype(np.float32)
        input_img = input_img / 255.0
        input_img = input_img.transpose(2, 0, 1)
        input_tensor = input_img[np.newaxis, :, :, :]
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


def multiclass_nms(boxes, scores, class_ids, iou_threshold):
    unique_class_ids = np.unique(class_ids)

    keep_boxes = []
    for class_id in unique_class_ids:
        class_indices = np.where(class_ids == class_id)[0]
        class_boxes = boxes[class_indices, :]
        class_scores = scores[class_indices]

        class_keep_boxes = nms(class_boxes, class_scores, iou_threshold)
        keep_boxes.extend(class_indices[class_keep_boxes])

    return keep_boxes


def nms(boxes, scores, iou_threshold):
    # Sort by score
    sorted_indices = np.argsort(scores)[::-1]

    keep_boxes = []
    while sorted_indices.size > 0:
        # Pick the last box
        box_id = sorted_indices[0]
        keep_boxes.append(box_id)

        # Compute IoU of the picked box with the rest
        ious = compute_iou(boxes[box_id, :], boxes[sorted_indices[1:], :])

        # Remove boxes with IoU over the threshold
        keep_indices = np.where(ious < iou_threshold)[0]

        # print(keep_indices.shape, sorted_indices.shape)
        sorted_indices = sorted_indices[keep_indices + 1]

    return keep_boxes


def compute_iou(box, boxes):
    # Compute xmin, ymin, xmax, ymax for both boxes
    xmin = np.maximum(box[0], boxes[:, 0])
    ymin = np.maximum(box[1], boxes[:, 1])
    xmax = np.minimum(box[2], boxes[:, 2])
    ymax = np.minimum(box[3], boxes[:, 3])

    # Compute intersection area
    intersection_area = np.maximum(0, xmax - xmin) * np.maximum(0, ymax - ymin)

    # Compute union area
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    boxes_area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union_area = box_area + boxes_area - intersection_area

    # Compute IoU
    iou = intersection_area / union_area

    return iou


def xywh2xyxy(x):
    # Convert bounding box (x, y, w, h) to bounding box (x1, y1, x2, y2)
    y = np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2
    y[..., 1] = x[..., 1] - x[..., 3] / 2
    y[..., 2] = x[..., 0] + x[..., 2] / 2
    y[..., 3] = x[..., 1] + x[..., 3] / 2
    return y
