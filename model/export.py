from ultralytics import YOLO

model = YOLO("weights/best.pt")

model.export(
    format="ncnn",
    imgsz=416,
    half=False,    # Pi 4 doesn't support half precision
)

print("Export done. NCNN files saved in weights/best_ncnn_model/")