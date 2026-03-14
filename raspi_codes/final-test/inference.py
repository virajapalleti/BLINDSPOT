import cv2
import csv
import time
import os
from picamera2 import Picamera2
from ultralytics import YOLO

# --- Config ---
MODEL_PATH   = "best_ncnn_model"
CSV_PATH     = "detections.csv"
FRAMES_DIR   = "frames"
CONFIDENCE   = 0.5
FRAME_WIDTH  = 640
FRAME_HEIGHT = 480

# --- Setup output folder ---
os.makedirs(FRAMES_DIR, exist_ok=True)

# --- Load model ---
print("[INFO] Loading NCNN model...")
model = YOLO(MODEL_PATH, task="detect")
print("[INFO] Model loaded.")

# --- Setup camera ---
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (FRAME_WIDTH, FRAME_HEIGHT)}
)
picam2.configure(config)
picam2.start()
time.sleep(1)
print("[INFO] Camera started.")
print("[INFO] Press 'q' in the preview window to stop and save.")

# --- Setup CSV ---
csv_file   = open(CSV_PATH, "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow([
    "frame_id", "timestamp", "fps",
    "class_id", "class_name", "confidence",
    "x1", "y1", "x2", "y2",
    "center_x", "center_y", "width", "height"
])

frame_id  = 0
prev_time = time.time()

try:
    while True:
        # Capture frame (Picamera2 gives RGB natively)
        frame_rgb = picam2.capture_array()

        # Flip vertically on the RGB frame before anything else
        frame_rgb = cv2.flip(frame_rgb, 0)

        # FPS
        curr_time = time.time()
        fps       = round(1.0 / (curr_time - prev_time), 2)
        prev_time = curr_time
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Run inference on RGB — YOLO expects RGB, not BGR
        results = model(frame_rgb, conf=CONFIDENCE, verbose=False)

        # Convert to BGR only for OpenCV (imwrite / imshow)
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        # Parse detections
        detection_count = 0
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                confidence       = round(float(box.conf[0]), 4)
                class_id         = int(box.cls[0])
                class_name       = model.names[class_id]
                center_x         = round((x1 + x2) / 2, 2)
                center_y         = round((y1 + y2) / 2, 2)
                width            = x2 - x1
                height           = y2 - y1

                csv_writer.writerow([
                    frame_id, timestamp, fps,
                    class_id, class_name, confidence,
                    x1, y1, x2, y2,
                    center_x, center_y,
                    width, height
                ])
                detection_count += 1

        # If no detections, still log the frame so renderer knows it exists
        if detection_count == 0:
            csv_writer.writerow([
                frame_id, timestamp, fps,
                "", "", "",
                "", "", "", "",
                "", "", "", ""
            ])

        csv_file.flush()

        # Save raw frame (no boxes — renderer draws them)
        frame_path = os.path.join(FRAMES_DIR, f"{frame_id:06d}.jpg")
        cv2.imwrite(frame_path, frame_bgr)

        # Live preview (just FPS monitor, no boxes)
        preview = frame_bgr.copy()
        cv2.putText(preview, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(preview, f"Frame: {frame_id}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.putText(preview, f"Detections: {detection_count}", (10, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.imshow("Inference Preview  (press q to stop)", preview)

        print(f"[Frame {frame_id:05d}] FPS: {fps:.1f} | Detections: {detection_count}")
        frame_id += 1

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("\n[INFO] 'q' pressed — stopping and saving...")
            break

except KeyboardInterrupt:
    print("\n[INFO] Interrupted.")

finally:
    csv_file.close()
    picam2.stop()
    cv2.destroyAllWindows()
    print(f"[INFO] Saved {frame_id} frames to '{FRAMES_DIR}/'")
    print(f"[INFO] Detections saved to '{CSV_PATH}'")