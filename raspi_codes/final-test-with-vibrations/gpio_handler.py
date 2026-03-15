import lgpio
import time

# --- GPIO setup ---
h = lgpio.gpiochip_open(4)

M1, M2, M3, M4, M5 = 17, 27, 22, 23, 24
ALL_MOTORS = [M1, M2, M3, M4, M5]

GROUPS = {
    'l': [M1, M2, M3],
    'm': [M2, M3, M4],
    'r': [M3, M4, M5],
}

for pin in ALL_MOTORS:
    lgpio.gpio_claim_output(h, pin)

# --- Timing constants ---
SHORT = 0.15
LONG  = 0.5
GAP   = 0.15
PAUSE = 0.3

# --- Direction thresholds (percentage of frame width) ---
LEFT_THRESHOLD  = 0.10   # center_x <= 10% of frame width → Left
RIGHT_THRESHOLD = 0.90   # center_x >= 90% of frame width → Right

# --- Class name → object code mapping ---
CLASS_MAP = {
    'chair'       : 'f',
    'dining table': 'f',
    'couch'       : 'f',
    'bed'         : 'f',
    'person'      : 'p',
    'stairs'      : 's',
    'wall'        : 'w',
    'elevation'   : 'e',
}

# --- Motor functions ---
def fire(pins, duration, intensity=100):
    for pin in pins:
        lgpio.tx_pwm(h, pin, 200, intensity)
    time.sleep(duration)
    for pin in pins:
        lgpio.tx_pwm(h, pin, 200, 0)
        lgpio.gpio_write(h, pin, 0)

def stop_all():
    for pin in ALL_MOTORS:
        lgpio.tx_pwm(h, pin, 200, 0)
        lgpio.gpio_write(h, pin, 0)

# --- Vibration patterns ---
def pattern_f(pins):
    """Furniture - two long: __ """
    fire(pins, LONG)
    time.sleep(GAP)
    fire(pins, LONG)
    time.sleep(PAUSE)

def pattern_p(pins):
    """People - three short: ..."""
    fire(pins, SHORT)
    time.sleep(GAP)
    fire(pins, SHORT)
    time.sleep(GAP)
    fire(pins, SHORT)
    time.sleep(PAUSE)

def pattern_s(pins):
    """Stairs - short then long: ._"""
    fire(pins, SHORT)
    time.sleep(GAP)
    fire(pins, LONG)
    time.sleep(PAUSE)

def pattern_w(pins):
    """Walls - long then two short: _.."""
    fire(pins, LONG)
    time.sleep(GAP)
    fire(pins, SHORT)
    time.sleep(GAP)
    fire(pins, SHORT)
    time.sleep(PAUSE)

def pattern_e(pins):
    """Elevations - two short then long: .._"""
    fire(pins, SHORT)
    time.sleep(GAP)
    fire(pins, SHORT)
    time.sleep(GAP)
    fire(pins, LONG)
    time.sleep(PAUSE)

PATTERNS = {
    'f': pattern_f,
    'p': pattern_p,
    's': pattern_s,
    'w': pattern_w,
    'e': pattern_e,
}

# --- Main trigger function called by inference.py ---
def trigger(class_name, center_x, frame_width):
    # Map class name to object code — skip if unknown
    obj = CLASS_MAP.get(class_name.lower())
    if obj is None:
        return

    # Map center_x to direction code
    ratio = center_x / frame_width
    if ratio <= LEFT_THRESHOLD:
        direction = 'l'
    elif ratio >= RIGHT_THRESHOLD:
        direction = 'r'
    else:
        direction = 'm'

    print(f"[GPIO] {class_name} → obj={obj} | direction={direction} | center_x={center_x} ({ratio:.0%})")

    # Fire the pattern
    PATTERNS[obj](GROUPS[direction])

# --- Cleanup ---
def cleanup():
    stop_all()
    lgpio.gpiochip_close(h)