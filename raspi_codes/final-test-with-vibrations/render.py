import cv2
import csv
import os
from collections import defaultdict

# --- Config ---
CSV_PATH    = "detections.csv"
FRAMES_DIR  = "frames"

# --- Colours per class (auto-assigned) ---
COLOURS = [
    (255,  56,  56), (255, 157,  51), (255, 255,  51),
    ( 51, 255, 255), ( 51, 153, 255), (153,  51, 255),
    (255,  51, 153), ( 51, 255, 153), (255, 128,   0),
    (128,   0, 255),
]

def get_colour(class_id):
    return COLOURS[int(class_id) % len(COLOURS)]

# --- Load CSV ---
def load_csv(path):
    detections = defaultdict(list)
    frame_info  = {}

    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                fid = int(row["frame_id"])
            except ValueError:
                continue

            if fid not in frame_info:
                frame_info[fid] = {
                    "timestamp" : row.get("timestamp", ""),
                    "fps"       : row.get("fps", ""),
                }

            if row["class_name"].strip() == "":
                continue

            try:
                detections[fid].append({
                    "class_id"   : int(row["class_id"]),
                    "class_name" : row["class_name"],
                    "confidence" : float(row["confidence"]),
                    "x1"         : int(row["x1"]),
                    "y1"         : int(row["y1"]),
                    "x2"         : int(row["x2"]),
                    "y2"         : int(row["y2"]),
                    "center_x"   : float(row["center_x"]),
                    "center_y"   : float(row["center_y"]),
                    "width"      : int(row["width"]),
                    "height"     : int(row["height"]),
                })
            except (ValueError, KeyError):
                continue

    return detections, frame_info

# --- Draw detections ---
def draw_detections(frame, dets):
    for det in dets:
        x1, y1, x2, y2 = det["x1"], det["y1"], det["x2"], det["y2"]
        colour          = get_colour(det["class_id"])
        label           = f"{det['class_name']}  {det['confidence']:.0%}"

        # Bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)

        # Label background — inside the box at the top-left corner
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.rectangle(frame, (x1, y1), (x1 + tw + 4, y1 + th + 8), colour, -1)

        # Label text — drawn inside the box
        cv2.putText(frame, label, (x1 + 2, y1 + th + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (255, 255, 255), 1, cv2.LINE_AA)

        # Center dot
        cx, cy = int(det["center_x"]), int(det["center_y"])
        cv2.circle(frame, (cx, cy), 4, colour, -1)

        # Size info below box
        size_label = f"{det['width']}x{det['height']}px"
        cv2.putText(frame, size_label, (x1, y2 + 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                    colour, 1, cv2.LINE_AA)

    return frame

# --- Validate inputs ---
if not os.path.exists(CSV_PATH):
    print(f"[ERROR] CSV not found: {CSV_PATH}")
    exit(1)

if not os.path.exists(FRAMES_DIR):
    print(f"[ERROR] Frames directory not found: {FRAMES_DIR}")
    exit(1)

# --- Load data ---
print("[INFO] Loading detections from CSV...")
detections, frame_info = load_csv(CSV_PATH)

# --- Get sorted frame list ---
frame_files = sorted([
    f for f in os.listdir(FRAMES_DIR)
    if f.endswith(".jpg")
])

if not frame_files:
    print(f"[ERROR] No frames found in '{FRAMES_DIR}/'")
    exit(1)

total_frames = len(frame_files)
print(f"[INFO] Found {total_frames} frames.")
print("[INFO] Controls:  q = quit  |  space = pause/resume  |  ← → = step frame")

# --- Playback ---
paused = False
idx    = 0

while idx < total_frames:
    fname    = frame_files[idx]
    frame_id = int(os.path.splitext(fname)[0])

    frame = cv2.imread(os.path.join(FRAMES_DIR, fname))
    if frame is None:
        idx += 1
        continue

    # Draw detections
    dets  = detections.get(frame_id, [])
    frame = draw_detections(frame, dets)

    # Overlays
    info     = frame_info.get(frame_id, {})
    fps_val  = info.get("fps", "?")
    ts_val   = info.get("timestamp", "")

    cv2.putText(frame, f"FPS: {fps_val}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Frame: {frame_id} / {total_frames - 1}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(frame, f"Detections: {len(dets)}", (10, 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(frame, ts_val, (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1, cv2.LINE_AA)

    if paused:
        cv2.putText(frame, "PAUSED", (frame.shape[1] // 2 - 50, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)

    cv2.imshow("Playback  (q=quit  space=pause  arrows=step)", frame)

    key = cv2.waitKey(100) & 0xFF

    if key == ord("q"):
        break
    elif key == ord(" "):
        paused = not paused
    elif key == 83 or key == ord("d"):   # right arrow or d → next frame
        idx = min(idx + 1, total_frames - 1)
    elif key == 81 or key == ord("a"):   # left arrow or a → prev frame
        idx = max(idx - 1, 0)
    elif not paused:
        idx += 1

cv2.destroyAllWindows()
print("[INFO] Playback finished.")