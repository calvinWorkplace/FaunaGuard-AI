from flask import Flask, render_template, request
from PIL import Image
import os
import numpy as np
import tensorflow as tf



app = Flask(__name__)

model = tf.keras.models.load_model("C:/Users/calvi/OneDrive/Dokumen/BINUS/Semester 3/Ai/CODE AI/Code AI/model2.h5")




class_labels = [
    "Anjing", "Badak", "Bekantan", "Beruang Madu", "Rangkong Badak",
    "Cendrawasih", "Domba", "Elang Jawa", "Gajah Asia", "Kakaktua Putih",
    "Kakaktua Raja", "Kerbau", "Kucing", "Kuda", "Kupu-kupu",
    "Macan Tutul", "Orang Utan", "Singa", "Tapir", "Ular", "Zebra"
]

conservation_status = {
    "Anjing": "Normal",
    "Badak": "Langka",
    "Bekantan": "Langka",
    "Beruang Madu": "Langka",
    "Rangkong Badak": "Langka",
    "Cendrawasih": "Langka",
    "Domba": "Normal",
    "Elang Jawa": "Langka",
    "Gajah Asia": "Langka",
    "Kakaktua Putih": "Langka",
    "Kakaktua Raja": "Langka",
    "Kerbau": "Normal",
    "Kucing": "Normal",
    "Kuda": "Normal",
    "Kupu-kupu": "Normal",
    "Macan Tutul": "Langka",
    "Orang Utan": "Langka",
    "Singa": "Normal",
    "Tapir": "Langka",
    "Ular": "Normal",
    "Zebra": "Normal"
}


UPLOAD_FOLDER = "static/uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def preprocess_image(image_path):
    img = Image.open(image_path)
    img = img.resize((299, 299))  # Sesuaikan dengan ukuran input model
    img = np.array(img) / 255.0  # Normalisasi
    img = np.expand_dims(img, axis=0)  # Tambahkan dimensi batch
    return img

def predict_animal(image_path):
    processed_image = preprocess_image(image_path)
    predictions = model.predict(processed_image)

    predicted_label = class_labels[np.argmax(predictions)]
    confidence = np.max(predictions)
    status = conservation_status.get(predicted_label, "Status tidak diketahui")
  
    return predicted_label, confidence, status

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == "POST":
        file = request.files['file']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            # Prediksi, confidence, dan status konservasi dari hewan yang diprediksi
            prediction, confidence, status = predict_animal(file_path)
             
            # Kirim semua data ke template
            return render_template("result.html", image_file=file.filename, prediction=prediction, confidence=confidence, status=status)
    
    return render_template("upload.html")

# Rute untuk halaman login
@app.route("/login")
def login():
    return render_template("login.html")

# Rute untuk halaman sign up
@app.route("/signup")
def signup():
    return render_template("signUp.html")

if __name__ == "__main__":
    app.run(debug=True)
