<h1> # UniML — Multi-Domain Machine Learning Web App </h1>

> 🎓 **Final Year Project** — B.Tech Computer Science Engineering, The Apollo University (2026)

UniML is a multi-domain ML-powered web application built with Flask. It brings together four intelligent modules — **Banking**, **Education**, **Loan Eligibility**, and **Healthcare** — under a single authenticated platform. Each module uses real machine learning models, OCR, and PDF parsing to deliver actionable insights.

---

## 🌐 Live Modules

| Module | What It Does |
|---|---|
| 🏦 Banking | Upload bank statements (PDF), auto-parse transactions, generate financial summaries |
| 🎓 Education | Upload a resume (image/PDF/text), get an ATS score and domain-specific feedback |
| 💰 Loan | Input income & EMI details, get loan eligibility, risk score, and required documents |
| 🏥 Healthcare | Upload a medical report image, OCR extracts vitals, ML predicts health condition |

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **ML Model:** Scikit-learn (Random Forest Classifier)
- **OCR:** OpenCV + Tesseract (pytesseract)
- **PDF Parsing:** PyPDF2
- **Auth:** SQLite + Werkzeug password hashing (session-based)
- **Frontend:** HTML, CSS, Jinja2 templates
- **Model Persistence:** joblib

---

## 📁 Project Structure

```
UniML/
├── app.py                  # Main Flask app — all routes
├── train_model.py          # Train & save healthcare ML model
├── database.db             # SQLite user database
├── requirements.txt        # Python dependencies
│
├── model/
│   └── healthcare_model.pkl  # Saved Random Forest model
│
├── banking/
│   ├── parser.py           # PDF bank statement parser
│   └── utils.py            # Data analysis & summary generation
│
├── education/
│   └── resume_analyzer.py  # ATS resume scoring logic
│
├── static/
│   └── uploads/            # Uploaded files (reports, resumes, statements)
│
└── templates/
    ├── auth.html            # Login / Signup page
    ├── dashboard.html       # User dashboard
    ├── banking_home.html
    ├── banking_upload.html
    ├── banking_result.html
    ├── education_upload.html
    ├── education_result.html
    ├── loan.html
    ├── loan_result.html
    ├── healthcare_upload.html
    └── result.html          # Healthcare prediction result
```

---

## ⚙️ Prerequisites

Before running UniML, make sure you have:

- Python 3.8+
- pip
- **Tesseract OCR** installed on your system

### Install Tesseract OCR (Windows)

1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to the default path: `C:\Program Files\Tesseract-OCR\`
3. The app is pre-configured to look at that path in `app.py`

> For Linux/Mac: `sudo apt install tesseract-ocr` or `brew install tesseract`

---

## 📦 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/rahulachari/UniML.git
cd UniML
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Libraries installed:**

| Library | Purpose |
|---|---|
| `flask` | Web framework |
| `opencv-python` | Image preprocessing for OCR |
| `pillow` | Image handling |
| `pytesseract` | OCR — text extraction from images |
| `scikit-learn` | Random Forest ML model |
| `pandas` | Data manipulation |
| `numpy` | Numerical operations |
| `joblib` | Save/load trained ML model |
| `werkzeug` | Password hashing & file utilities |

### 4. Train the Healthcare ML Model

This generates `model/healthcare_model.pkl` (required to run the app):

```bash
python train_model.py
```

You should see: `✅ Model trained and saved`

### 5. Run the App

```bash
python app.py
```

Open your browser and go to: **http://127.0.0.1:5000**

---

## 🚀 How to Use

1. **Sign up** with a username and password on the home page
2. **Log in** to access the dashboard
3. Choose a module:
   - **Banking** → Upload a bank statement PDF
   - **Education** → Upload your resume (PNG, JPG, PDF, or TXT) + select a domain
   - **Loan** → Fill in income, current EMI, loan amount, employment type, and loan type
   - **Healthcare** → Upload a medical report image (blood test, etc.)
4. View ML-powered results and recommendations

---

## 🧠 Healthcare ML Model Details

- **Algorithm:** Random Forest Classifier (150 estimators)
- **Training Data:** 800 synthetically generated records
- **Input Features:** Hemoglobin, WBC count, Blood Sugar, Blood Pressure, Pulse
- **Output Classes:** Healthy, Anemia, Diabetes, Hypertension, Infection, Cardiac Stress
- **Confidence Score:** Displayed with each prediction

---

## 👥 Team

Built as a **group final year project** for B.Tech CSE at The Apollo University (2026).

**Rahul Achari** — Backend Developer
- SQLite authentication system
- Education ML module (ATS Resume Scorer)
- Flask routing & session management

---

## 📄 License

This project was developed for academic purposes as a final year B.Tech CSE project.

---
