from ultralytics import YOLO


def main():
    model = YOLO("yolov8n.pt")
    model.export(format="onnx", imgsz=[480, 640])


if __name__ == "__main__":
    main()
