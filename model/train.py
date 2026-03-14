from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="datasets/combined/data.yaml",
    epochs=100,
    imgsz=416,
    batch=16,
    pretrained=True,
    patience=20,
    device="cpu",
    workers=4,
)