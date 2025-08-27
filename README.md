# 🫀 Cardio-Tool: Cardiovascular Risk & ECG Interpretation

> **Research Use Only (RUO)**
> This tool provides rule-based cardiovascular risk scoring and ECG interpretation for **education, simulation, and research**.
> ⚠️ **Not for clinical diagnosis or patient care.**

Built with Python and evidence-based guidelines (ACC/AHA, ESC). Includes a FastAPI backend, test suite, and extensible calculator design.

---

## 📋 Features

- ✅ **ASCVD 10-Year Risk Score** (Pooled Cohort Equations)
- ✅ **Blood Pressure Classification** (ACC/AHA 2017)
- ✅ **CHA₂DS₂-VASc Stroke Risk** (for atrial fibrillation)
- ✅ **ECG Rhythm Interpretation** (rate, regularity, P-waves)
- ✅ **12-Lead ECG Findings** (ST, QT, LVH, Q waves)
- ✅ **FastAPI HTTP Endpoints** for integration
- ✅ **Pytest Suite** for validation and regression testing
- ✅ **Input validation** for all calculators

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/cardio-tool.git
cd cardio-tool
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```
# OR
```bash
venv\Scripts\activate     # Windows
```
Upgrade pip:
```bash
pip install --upgrade pip
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Tests
```bash
export PYTHONPATH=.
pytest tests/ -v
```

## ▶️ Run the FastAPI Server

Start the API server:
```bash
uvicorn main:app --reload --port=8000
```

Then open:

🔹 Swagger UI: http://localhost:8000/docs
🔹 ReDoc: http://localhost:8000/redoc
 You can now test endpoints like:

POST /ascvd
POST /bp-category
POST /ecg/comprehensive

📊 Optional: Run Streamlit Dashboard

If you have a Streamlit dashboard (dashboard.py):
```bash
streamlit run dashboard.py
```

🧪 Example API Usage

Request: ASCVD Risk
```bash
curl -X POST http://localhost:8000/ascvd \
  -H "Content-Type: application/json" \
  -d '{
    "age": 60,
    "sex": "Male",
    "race": "White",
    "total_cholesterol": 200,
    "hdl": 50,
    "systolic_bp": 120,
    "on_htn_meds": false,
    "smoker": false,
    "diabetes": false
}'
```

Response:
```bash
{
  "risk": 0.078,
  "risk_percent": 7.8
}
```

## 📚 Available Calculators

| Calculator | Function | Input | Output |
|----------|--------|-------|--------|
| **ASCVD Risk** | `ascvd()` | Demographics, lipids, BP | 10-year CVD risk (%) |
| **BP Category** | `bp_category()` | SBP, DBP | Hypertension stage |
| **CHA₂DS₂-VASc** | `cha2ds2vasc()` | AFib risk factors | Stroke risk score (0–9) |
| **ECG Rhythm** | `ecg_interpret()` | Rate, regularity, P-waves | Rhythm diagnosis |
| **12-Lead ECG** | `interpret_12lead_findings()` | ST, QT, LVH, Q waves | Risk-level summary |
| **Comprehensive ECG** | `interpret_ecg_comprehensive()` | Full ECG data | Structured report |

---

## 📖 API Documentation

For full details on inputs, outputs, and examples, see:
👉 [`API.md`](API.md)

---

## 🐳 Optional: Run with Docker

If you have a `Dockerfile`:

```bash
docker build -t cardio-tool .
docker run -p 8000:8000 cardio-tool
```

## 🧩 Development

### Add New Calculators

Add function in app/calculators/
Write tests in tests/
Expose via FastAPI in main.py

### Run Tests
```bash
export PYTHONPATH=.
pytest tests/ -v
```

### Code Style

We follow PEP 8. Consider using:

black for formatting
isort for import sorting
mypy for type checking

### Install Dev Tools
```bash
pip install black isort mypy pytest-cov
```

## 🛑 Disclaimer

This software is for research and educational purposes only.
It is not a medical device and is not intended for diagnosis or treatment.
Always consult a licensed clinician for patient care decisions.

## 🙌 Support

For questions or contributions, contact:
