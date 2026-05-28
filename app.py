import os
import re
import sqlite3
import cv2
import pytesseract
import joblib
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from banking.utils import analyze_data, generate_summary
from banking.parser import parse_pdf
from education.resume_analyzer import analyze_resume

# -------------------- LOAN TYPES --------------------

LOAN_TYPES = {
    "home": {
        "name": "Home Loan",
        "max_multiplier": 60,
        "interest": "8% - 10%",
        "docs_salaried": ["Aadhaar", "PAN", "Salary Slips (6 months)", "Bank Statement (6 months)", "Property Documents"],
        "docs_self": ["Aadhaar", "PAN", "IT Returns (2 yrs)", "Business Proof", "Property Documents"]
    },
    "personal": {
        "name": "Personal Loan",
        "max_multiplier": 20,
        "interest": "10% - 18%",
        "docs_salaried": ["Aadhaar", "PAN", "Salary Slips (3 months)", "Bank Statement"],
        "docs_self": ["Aadhaar", "PAN", "IT Returns", "Business Proof"]
    },
    "education": {
        "name": "Education Loan",
        "max_multiplier": 40,
        "interest": "7% - 12%",
        "docs_salaried": ["Aadhaar", "PAN", "Admission Letter", "Fee Structure", "Bank Statement"],
        "docs_self": ["Aadhaar", "PAN", "Admission Letter", "IT Returns"]
    },
    "car": {
        "name": "Car Loan",
        "max_multiplier": 30,
        "interest": "9% - 12%",
        "docs_salaried": ["Aadhaar", "PAN", "Salary Slips", "Bank Statement", "Vehicle Quotation"],
        "docs_self": ["Aadhaar", "PAN", "IT Returns", "Vehicle Quotation"]
    }
}

# -------------------- APP CONFIG --------------------

app = Flask(__name__)
app.secret_key = "uniml_secret_key"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -------------------- LOAD MODEL --------------------

model = joblib.load("model/healthcare_model.pkl")

# -------------------- DATABASE --------------------

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# -------------------- AUTH --------------------

@app.route("/")
def home():
    return render_template("auth.html")

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    password = generate_password_hash(request.form["password"])

    try:
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users(username,password) VALUES (?,?)",
                  (username, password))
        conn.commit()
        conn.close()
    except:
        return "Username already exists"

    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()

    if user and check_password_hash(user[2], password):
        session["user"] = username
        return redirect("/dashboard")

    return "Invalid Credentials"

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# -------------------- BANKING --------------------

@app.route("/banking")
def banking():
    return render_template("banking_home.html")

@app.route("/banking_upload")
def banking_upload():
    return render_template("banking_upload.html")

@app.route("/process_banking", methods=["POST"])
def process_banking():
    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    df = parse_pdf(filepath)
    df = analyze_data(df)
    summary = generate_summary(df)

    return render_template("banking_result.html",
                           tables=df.to_dict(orient="records"),
                           summary=summary)

# -------------------- EDUCATION --------------------

@app.route("/education")
def education():
    return render_template("education_upload.html")


@app.route('/process_education', methods=['POST'])
def process_education():

    file = request.files['resume']

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    domain = request.form.get("domain")

    text = ""

    # 🔥 IMAGE OCR
    if filepath.lower().endswith(('.png', '.jpg', '.jpeg')):
        img = cv2.imread(filepath)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Improve OCR accuracy
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        text = pytesseract.image_to_string(gray)

    # 🔥 PDF OCR
    elif filepath.lower().endswith('.pdf'):
        from PyPDF2 import PdfReader
        reader = PdfReader(filepath)
        for page in reader.pages:
            text += page.extract_text() or ""

    # 🔥 TXT fallback
    else:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    # 🚨 sanity check
    if not text.strip():
        return "Text extraction failed. Try a clearer image."

    result = analyze_resume(text, domain)

    return render_template('education_result.html', data=result)
# -------------------- LOAN --------------------

@app.route("/loan")
def loan():
    return render_template("loan.html")

@app.route("/process_loan", methods=["POST"])
def process_loan():

    income = float(request.form["income"])
    emi = float(request.form["emi"])
    loan_amount = float(request.form["loan_amount"])
    employment = request.form["employment"]
    loan_type = request.form["loan_type"]

    loan = LOAN_TYPES[loan_type]

    max_emi = 0.4 * income
    remaining = max_emi - emi
    eligible_amount = remaining * loan["max_multiplier"]

    # 🔥 RISK CALCULATION (FIXED)
    ratio = emi / income

    if ratio < 0.3:
        risk = 85
    elif ratio < 0.5:
        risk = 65
    else:
        risk = 40

    # 🔥 DECISION
    if eligible_amount >= loan_amount and ratio < 0.4:
        decision = "APPROVED"
    elif eligible_amount >= loan_amount * 0.7:
        decision = "PARTIAL"
    else:
        decision = "REJECTED"

    # DOCUMENTS
    docs = loan["docs_salaried"] if employment == "salaried" else loan["docs_self"]

    # SUGGESTIONS
    suggestions = []

    if ratio > 0.5:
        suggestions.append("High EMI compared to income")

    if eligible_amount < loan_amount:
        suggestions.append("Requested amount exceeds eligibility")

    if risk < 60:
        suggestions.append("Improve financial stability")

    if decision == "APPROVED":
        suggestions.append("Good financial profile")

    return render_template("loan_result.html",
                           loan=loan,
                           income=income,
                           loan_amount=loan_amount,
                           eligible_amount=round(eligible_amount, 2),
                           decision=decision,
                           risk=risk,
                           docs=docs,
                           suggestions=suggestions)

# -------------------- HEALTHCARE MODULE --------------------

@app.route("/healthcare")
def healthcare():
    if "user" not in session:
        return redirect("/")
    return render_template("healthcare_upload.html")

# -------------------- HELPER FUNCTIONS --------------------

def extract_all_parameters(text):
    parameters = {}

    patterns = [
        r"([A-Za-z\s]+)[\:\-]\s*(\d+\.?\d*)",
        r"([A-Za-z\s]+)\s+(\d+\.?\d*)"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for name, value in matches:
            name = name.strip().lower()
            try:
                parameters[name] = float(value)
            except:
                continue

    return parameters


def get_value(parameters, keys, default):
    for key in keys:
        for param_name, val in parameters.items():
            if key in param_name.lower():
                return val
    return default


def generate_medical_suggestions(prediction):

    mapping = {
        "Anemia": {
            "symptoms": "Fatigue, dizziness, pale skin",
            "diagnosis": "Complete Blood Count (CBC)",
            "doctor": "Hematologist"
        },
        "Diabetes": {
            "symptoms": "Frequent urination, thirst, fatigue",
            "diagnosis": "HbA1c test",
            "doctor": "Endocrinologist"
        },
        "Hypertension": {
            "symptoms": "Headache, chest pain, dizziness",
            "diagnosis": "Blood pressure monitoring",
            "doctor": "Cardiologist"
        },
        "Infection": {
            "symptoms": "Fever, swelling",
            "diagnosis": "Blood test",
            "doctor": "General Physician"
        },
        "Cardiac Stress": {
            "symptoms": "Rapid heartbeat, fatigue",
            "diagnosis": "ECG",
            "doctor": "Cardiologist"
        }
    }

    suggestions = []

    for key in mapping:
        if key in prediction:
            suggestions.append({
                "condition": key,
                **mapping[key]
            })

    if not suggestions:
        suggestions.append({
            "condition": "General Health",
            "symptoms": "No major symptoms",
            "diagnosis": "Routine check-up",
            "doctor": "General Physician"
        })

    return suggestions

# -------------------- HEALTHCARE PREDICTION --------------------

@app.route("/predict", methods=["POST"])
def predict():

    if "report" not in request.files:
        return "No file uploaded"

    file = request.files["report"]

    if file.filename == "":
        return "No file selected"

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        img = cv2.imread(filepath)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
    except:
        return "Error processing image"

    if not text.strip():
        return "OCR failed. Please upload a clearer report."

    parameters = extract_all_parameters(text)

    hb = get_value(parameters, ["hemoglobin", "hb"], 13.5)
    wbc = get_value(parameters, ["wbc"], 8000)
    sugar = get_value(parameters, ["glucose", "sugar"], 110)
    bp = get_value(parameters, ["bp", "pressure"], 120)
    pulse = get_value(parameters, ["pulse", "heart"], 75)

    try:
        features = [[hb, wbc, sugar, bp, pulse]]
        prediction = model.predict(features)[0]
        confidence = round(max(model.predict_proba(features)[0]) * 100, 2)
    except:
        prediction = "Unable to predict"
        confidence = 0

    explanations = []

    if hb < 11:
        explanations.append(f"Hemoglobin is low ({hb})")
    if wbc > 11000:
        explanations.append(f"WBC is high ({wbc})")
    if sugar > 140:
        explanations.append(f"Blood sugar is high ({sugar})")
    if bp > 140:
        explanations.append(f"Blood pressure is high ({bp})")
    if pulse > 100:
        explanations.append(f"Pulse rate is high ({pulse})")

    return render_template(
        "result.html",
        report_summary={
            "Condition": prediction,
            "Confidence": f"{confidence}%",
            "Status": "Abnormal" if prediction != "Healthy" else "Normal"
        },
        important_values=[{
            "name": k.title(),
            "value": v,
            "range": "Medical standard"
        } for k, v in parameters.items()],
        why_values_matter=explanations if explanations else ["All values are normal"],
        reason_for_prediction=f"Prediction '{prediction}' based on extracted parameters.",
        suggested_steps=generate_medical_suggestions(prediction),
        extracted_text=text
    )
# -------------------- MAIN --------------------

if __name__ == "__main__":
    app.run(debug=True)