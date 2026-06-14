import os
import uuid
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ── Config ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
MODEL_PATH = os.path.join(BASE_DIR, "models", "model2.h5")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB max upload

# ── Model (lazy-loaded so the server starts even without TensorFlow) ─────────
model = None
tf = None
np = None
Image = None

def load_model():
    global model, tf, np, Image
    try:
        import tensorflow as _tf
        import numpy as _np
        from PIL import Image as _Image
        tf = _tf
        np = _np
        Image = _Image
    except ImportError as e:
        print(f"[WARNING] Dependency not available: {e}. Prediction will be disabled.")
        return

    if not os.path.exists(MODEL_PATH):
        print(f"[WARNING] Model not found at '{MODEL_PATH}'. Place model2.h5 inside the models/ folder.")
        return
    print("[INFO] Loading model…")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("[INFO] Model loaded successfully.")

CLASS_LABELS = [
    "Anjing", "Badak", "Bekantan", "Beruang Madu", "Rangkong Badak",
    "Cendrawasih", "Domba", "Elang Jawa", "Gajah Asia", "Kakaktua Putih",
    "Kakaktua Raja", "Kerbau", "Kucing", "Kuda", "Kupu-kupu",
    "Macan Tutul", "Orang Utan", "Singa", "Tapir", "Ular", "Zebra"
]

CONSERVATION_STATUS = {
    "Anjing": "Normal", "Badak": "Langka", "Bekantan": "Langka",
    "Beruang Madu": "Langka", "Rangkong Badak": "Langka", "Cendrawasih": "Langka",
    "Domba": "Normal", "Elang Jawa": "Langka", "Gajah Asia": "Langka",
    "Kakaktua Putih": "Langka", "Kakaktua Raja": "Langka", "Kerbau": "Normal",
    "Kucing": "Normal", "Kuda": "Normal", "Kupu-kupu": "Normal",
    "Macan Tutul": "Langka", "Orang Utan": "Langka", "Singa": "Normal",
    "Tapir": "Langka", "Ular": "Normal", "Zebra": "Normal"
}

# ── Helpers ─────────────────────────────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path: str):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((299, 299))
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)  # (1, 299, 299, 3)

def predict(image_path: str) -> dict:
    processed = preprocess_image(image_path)
    preds = model.predict(processed, verbose=0)[0]          # shape (21,)
    idx = int(np.argmax(preds))
    label = CLASS_LABELS[idx]
    confidence = float(preds[idx])
    status = CONSERVATION_STATUS.get(label, "Tidak diketahui")

    # Top-3 predictions for extra context
    top3_idx = np.argsort(preds)[::-1][:3]
    top3 = [
        {"label": CLASS_LABELS[i], "confidence": round(float(preds[i]) * 100, 2)}
        for i in top3_idx
    ]

    return {
        "label": label,
        "confidence": round(confidence * 100, 2),
        "status": status,
        "top3": top3,
    }

# ── Routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict_route():
    if tf is None:
        return jsonify({"error": "TensorFlow belum terinstall. Jalankan: pip install tensorflow"}), 503

    if model is None:
        return jsonify({"error": "Model belum dimuat. Letakkan model2.h5 di folder models/."}), 503

    if "file" not in request.files:
        return jsonify({"error": "Tidak ada file yang diunggah."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Tidak ada file yang dipilih."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Format file tidak didukung. Gunakan PNG, JPG, JPEG, atau WEBP."}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(save_path)

    try:
        result = predict(save_path)
        result["image_url"] = f"/static/uploads/{unique_name}"
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Gagal memproses gambar: {str(e)}"}), 500

# ── Entry ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    load_model()
    app.run(debug=True)
