import cv2
import csv
import time
import os
import threading
import queue
from picamera2 import Picamera2
from ultralytics import YOLO
import gpio_handler

# --- Config ---
MODEL_PATH    = "best_ncnn_model"
CSV_PATH      = "detections.csv"
FRAMES_DIR    = "frames"
CONFIDENCE    = 0.5
FRAME_WIDTH   = 640
FRAME_HEIGHT  = 480
Y_THRESHOLD   = 350       # y2 must exceed this to be considered close
DEBOUNCE_SEC  = 2.0       # minimum seconds between triggers for the same class

# --- Setup output folder ---
os.makedirs(FRAMES_DIR, exist_ok=True)

# --- Detection queue (main thread → worker thread) ---
detection_queue = queue.Queue()

# --- Debounce tracker: class_name → last triggered timestamp ---
last_triggered = {}
debounce_lock  = threading.Lock()

# ----------------------------------------------------------------
# Placeholder — replace with your GPIO function later
# ----------------------------------------------------------------
def handle_close_object(class_name, center_x):
    gpio_handler.trigger(class_name, center_x, FRAME_WIDTH)

# ----------------------------------------------------------------
# Worker thread — consumes detections from queue, applies
# debounce, then calls handle_close_object
# ----------------------------------------------------------------
def worker():
    while True:
        item = detection_queue.get()
        if item is None:
            break  # poison pill — shut down thread

        class_name = item["class_name"]
        center_x   = item["center_x"]

        # Debounce — only trigger if enough time has passed for this class
        now = time.time()
        with debounce_lock:
            last = last_triggered.get(class_name, 0)
            if now - last >= DEBOUNCE_SEC:
                last_triggered[class_name] = now
                trigger = True
            else:
                trigger = False

        if trigger:
            handle_close_object(class_name, center_x)

        detection_queue.task_done()

# --- Start worker thread ---
worker_thread = threading.Thread(target=worker, daemon=True)
worker_thread.start()

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
        # Capture frame
        frame_rgb = picam2.capture_array()
        frame_rgb = cv2.flip(frame_rgb, 0)

        # FPS
        curr_time = time.time()
        fps       = round(1.0 / (curr_time - prev_time), 2)
        prev_time = curr_time
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Run inference on RGB
        results = model(frame_rgb, conf=CONFIDENCE, verbose=False)

        # Convert to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        # Parse detections
        detection_count  = 0
        frame_detections = []  # collects dets for this frame → queue

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

                # CSV logging
                csv_writer.writerow([
                    frame_id, timestamp, fps,
                    class_id, class_name, confidence,
                    x1, y1, x2, y2,
                    center_x, center_y,
                    width, height
                ])
                detection_count += 1

                # Collect for queue
                frame_detections.append({
                    "class_name" : class_name,
                    "confidence" : confidence,
                    "y2"         : y2,
                    "center_x"   : center_x,
                })

        # Log empty frame
        if detection_count == 0:
            csv_writer.writerow([
                frame_id, timestamp, fps,
                "", "", "",
                "", "", "", "",
                "", "", "", ""
            ])

        # Flush CSV every 10 frames to reduce SD card writes
        if frame_id % 10 == 0:
            csv_file.flush()

        # Push only the highest confidence detection that passes proximity logic
        if frame_detections:
            close = [d for d in frame_detections if d["confidence"] >= CONFIDENCE and d["y2"] > Y_THRESHOLD]
            if close:
                best = max(close, key=lambda d: d["confidence"])
                detection_queue.put(best)

        # Save raw frame
        frame_path = os.path.join(FRAMES_DIR, f"{frame_id:06d}.jpg")
        cv2.imwrite(frame_path, frame_bgr)

        # Live preview
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
    # Shut down worker thread cleanly
    detection_queue.put(None)
    worker_thread.join()

    csv_file.close()
    picam2.stop()
    cv2.destroyAllWindows()
    gpio_handler.cleanup()
    print(f"[INFO] Saved {frame_id} frames to '{FRAMES_DIR}/'")
    print(f"[INFO] Detections saved to '{CSV_PATH}'")