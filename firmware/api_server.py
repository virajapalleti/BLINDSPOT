from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Maps app object names → YOLO class names
OBJECT_MAP = {
    'furniture': ['chair', 'dining table', 'couch', 'bed'],
    'people':    ['person'],
    'stairs':    ['stairs'],
    'walls':     [],        # not in your model yet
    'elevation': [],        # not in your model yet
}

current_patterns = {}
current_range = 2.0

@app.route('/status')
def status():
    return jsonify({"status": "ok"}), 200

@app.route('/apply', methods=['POST'])
def apply_pattern():
    data = request.json
    obj = data.get('object')
    pattern = data.get('pattern')
    current_patterns[obj] = pattern
    print(f"Pattern set: {obj} → {pattern}")
    return jsonify({"ok": True}), 200

@app.route('/range', methods=['POST'])
def set_range():
    global current_range
    current_range = request.json.get('range', 2.0)
    print(f"Range set to: {current_range}m")
    return jsonify({"ok": True}), 200

@app.route('/patterns', methods=['GET'])
def get_patterns():
    return jsonify(current_patterns), 200

@app.route('/object_map', methods=['GET'])
def get_object_map():
    return jsonify(OBJECT_MAP), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)