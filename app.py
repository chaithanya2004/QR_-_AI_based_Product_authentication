from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import tensorflow as tf
import numpy as np
import cv2
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route("/")
def home():
    return "App running"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# ---------------- QR Verification Model ----------------
model = tf.keras.models.load_model('model/qr_authenticator_model.h5')
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
IMG_SIZE = 128

# ---------------- AI Package Verification Model ----------------
# ---------------- AI Package Verification Model ----------------
ai_package_model = tf.keras.models.load_model('package_verifier.h5')

# Get correct size automatically
AI_IMG_SIZE = ai_package_model.input_shape[1]



# ---------------- FIXED PACKAGE VERIFICATION LOGIC ----------------
# Using model softmax probabilities:
# pred[0] = Genuine
# pred[1] = Fake
def ai_predict_label(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (AI_IMG_SIZE, AI_IMG_SIZE))
    img = img.astype("float32") / 255.0
    img = np.expand_dims(img, axis=0)

    # Sigmoid model → single output neuron
    pred = ai_package_model.predict(img, verbose=0)[0][0]

    if pred >= 0.5:
        return "Genuine"
    else:
        return "Fake"



# ---------------- Helper Functions ----------------
def predict_image(img_path):
    img = cv2.imread(img_path)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img_array = img.astype('float32') / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)[0]
    class_index = np.argmax(prediction)

    qr_data = scan_qr(img_path)

    if qr_data is None:
        return "Non-QR / Unrelated QR", 2

    classes = ["Fake Product", "Genuine Product", "Non-QR / Unrelated QR"]
    return classes[class_index], class_index


def scan_qr(img_path):
    img = cv2.imread(img_path)
    detector = cv2.QRCodeDetector()

    data, points, _ = detector.detectAndDecode(img)
    if data:
        return data.strip()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    data, points, _ = detector.detectAndDecode(gray)
    if data:
        return data.strip()

    resized = cv2.resize(img, None, fx=1.5, fy=1.5)
    data, points, _ = detector.detectAndDecode(resized)
    if data:
        return data.strip()

    return None

#this is extra added 
def is_payment_qr(qr_data):
    if not qr_data:
        return False
    qr_data = qr_data.lower()
    return (
        "upi://" in qr_data or
        "paytm" in qr_data or
        "gpay" in qr_data or
        "phonepe" in qr_data
    )



def fetch_product_details(url):
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        return {"qr_url": url}
    except:
        return {"qr_url": url}


# ---------------- Routes ----------------
@app.route("/")
def main_page():
    return render_template("new.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/login_user", methods=['POST'])
def login_user():
    return redirect(url_for('home_page'))

@app.route("/signup_user", methods=['POST'])
def signup_user():
    return redirect(url_for('home_page'))

@app.route("/home")
def home_page():
    return render_template("new1.html")

@app.route("/index")
def index():
    return render_template("index.html")

# ---------------- QR Verification Upload ----------------
@app.route('/predict', methods=['POST'])
def upload_image():
    file = request.files['file']
    if not file:
        return "No file uploaded"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # 1️⃣ Scan QR first
    qr_data = scan_qr(filepath)

    # 2️⃣ Block payment QR
    if is_payment_qr(qr_data):
        return render_template(
            'result.html',
            ai_result="Payment QR – Not a Product",
            product_info={"qr_url": qr_data, "name": "Payment QR"},
            img_path=filepath
        )

    # 3️⃣ Normal QR/CNN verification
    ai_result, class_index = predict_image(filepath)

    if class_index == 2:
        product_info = {"qr_url": None, "name": "Unrelated / Non-QR Image"}
    else:
        if qr_data is None:
            product_info = {"qr_url": None, "name": "QR Not Detected"}
        else:
            product_info = fetch_product_details(qr_data)

    return render_template(
        'result.html',
        ai_result=ai_result,
        product_info=product_info,
        img_path=filepath
    )


# ---------------- AI Package Verification (UPDATED) ----------------
@app.route('/ai_verify', methods=['GET', 'POST'])
def ai_verify():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "No file uploaded"

        file = request.files['image']
        if file.filename == '':
            return "Invalid file"

        filename = secure_filename(file.filename)
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(img_path)

        # prediction result
        result = ai_predict_label(img_path)

        # redirect to result page
        return render_template("ai_result.html",
                               result=result,
                               img_path=img_path)

    return render_template('ai_verify.html')



# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True)
