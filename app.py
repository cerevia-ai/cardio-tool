# app.py

import streamlit as st
from utils import create_pdf_report

# Import the calculators for risk assessment
from app.calculators.ascvd import ascvd
from app.calculators.bp_category import bp_category
from app.calculators.cha2ds2vasc import cha2ds2vasc
from app.calculators.ecg_interpret import (
    interpret_rhythm,
    interpret_12lead_findings,
    interpret_ecg_comprehensive,
)
from app.validators.patient_input import (
    validate_ascvd_input,
    validate_bp_input,
    validate_cha2ds2vasc_input,
    validate_ecg_rhythm_input,
    validate_ecg_12lead_input,
)

# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="Cardio-Tool Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("Cardio-Tool")
st.sidebar.markdown("""
> **Research Use Only (RUO)**
> Not for clinical diagnosis.
""")

# Patient ID Input (New)
patient_id = st.sidebar.text_input("Patient ID (Optional)", key="patient_id")

tool = st.sidebar.selectbox(
    "Choose a tool",
    [
        "Home",
        "ASCVD Risk Calculator",
        "Blood Pressure Category",
        "CHA₂DS₂-VASc Stroke Risk",
        "ECG Interpretation",
    ],
)

# -----------------------------
# Persistent Results Summary (New)
st.sidebar.divider()
st.sidebar.markdown("### 🔹 Recent Results")

# Retrieve results from session state
if 'ascvd_risk' in st.session_state:
    st.sidebar.markdown(f"**ASCVD Risk**: {st.session_state.ascvd_risk:.1%}")
if 'bp_category' in st.session_state:
    st.sidebar.markdown(f"**BP Category**: {st.session_state.bp_category}")
if 'cha2ds2vasc_score' in st.session_state:
    st.sidebar.markdown(f"**CHA₂DS₂-VASc**: {st.session_state.cha2ds2vasc_score}")
if 'ecg_rhythm' in st.session_state:
    st.sidebar.markdown(f"**ECG Rhythm**: {st.session_state.ecg_rhythm}")

st.sidebar.divider()
st.sidebar.markdown("### 📚 References")
st.sidebar.markdown("""
- [2013 ACC/AHA ASCVD Risk](https://doi.org/10.1161/01.cir.0000437741.48606.98)
- [2017 ACC/AHA Hypertension](https://doi.org/10.1161/HYP.0000000000000065)
- [CHA₂DS₂-VASc Score](https://www.sciencedirect.com/science/article/abs/pii/S0012369210600670)
""")

# -----------------------------
# Home Page
# -----------------------------

if tool == "Home":
    st.title("Cardio-Tool Dashboard")
    st.markdown("""
    ⚠️ **Not for clinical use** — for education, simulation, and research only.

    Welcome to **Cardio-Tool**, a research-grade cardiovascular risk and ECG interpretation tool.

    ### Features
    - **ASCVD 10-Year Risk** (Pooled Cohort Equations)
    - **Blood Pressure Classification** (ACC/AHA 2017)
    - **CHA₂DS₂-VASc Stroke Risk** for AFib
    - **ECG Rhythm & 12-Lead Interpretation**

    ### Get Started
    Use the sidebar to navigate to a calculator.
    """)

    st.info("Tip: All inputs are validated for physiological plausibility.")

# -----------------------------
# ASCVD Risk Calculator
# -----------------------------

elif tool == "ASCVD Risk Calculator":
    st.title("ASCVD 10-Year Risk Calculator")

    st.markdown("""
    Estimates 10-year risk of atherosclerotic cardiovascular disease.
    Based on [2013 ACC/AHA Pooled Cohort Equations](https://doi.org/10.1161/01.cir.0000437741.48606.98).
    """, unsafe_allow_html=True)

    # Add COR/LOE Tooltip (New)
    st.markdown(
        """
        <div style="position: relative; display: inline-block;">
            <span style="visibility: hidden; width: 200px; background-color: #555; color: #fff; text-align: center; border-radius: 6px; padding: 5px; position: absolute; z-index: 1; bottom: 125%; left: 50%; margin-left: -100px; font-size: 0.8em;">
                COR: I (Strong Recommendation)<br>LOE: B (Moderate Evidence)
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        age = st.slider("Age", min_value=40, max_value=79, value=60, step=1)
        sex = st.selectbox("Sex", ["Male", "Female"])
        race = st.selectbox("Race", ["White", "Black"])
        total_cholesterol = st.slider("Total Cholesterol (mg/dL)", 100, 400, 200, step=5)
        hdl = st.slider("HDL (mg/dL)", 20, 100, 50, step=1)

    with col2:
        sbp = st.slider("Systolic BP (mmHg)", 70, 250, 120, step=1)
        on_htn_meds = st.checkbox("On Hypertension Medications?")
        smoker = st.checkbox("Current Smoker?")
        diabetes = st.checkbox("Diabetes?")

    if st.button("Calculate ASCVD Risk"):
        data = {
            "age": age,
            "sex": sex,
            "race": race,
            "total_cholesterol": total_cholesterol,
            "hdl": hdl,
            "sbp": sbp,
            "on_htn_meds": on_htn_meds,
            "smoker": smoker,
            "diabetes": diabetes,
        }

        try:
            validate_ascvd_input(data)
            risk = ascvd(data)
            st.success(f"**10-Year ASCVD Risk: {risk:.1%}**")
            if risk < 0.05:
                st.info("**Low Risk**: <5% — Lifestyle therapy recommended.")
            elif risk < 0.075:
                st.warning("**Borderline Risk**: 5–7.5% — Consider risk enhancers.")
            elif risk < 0.20:
                st.warning("**Intermediate Risk**: 7.5–20% — Shared decision making for statin.")
            else:
                st.error("**High Risk**: ≥20% — High-intensity statin recommended.")

            # Store result in session state
            st.session_state.ascvd_risk = risk

            # Prepare data for report
            report_data = {
                "Patient ID": patient_id or "N/A",
                "Age": age,
                "Sex": sex,
                "Race": race,
                "Risk Factors": [
                    f"Total Cholesterol: {total_cholesterol} mg/dL",
                    f"HDL: {hdl} mg/dL",
                    f"Systolic BP: {sbp} mmHg",
                    f"On HTN Meds: {'Yes' if on_htn_meds else 'No'}",
                    f"Smoker: {'Yes' if smoker else 'No'}",
                    f"Diabetes: {'Yes' if diabetes else 'No'}"
                ],
                "10-Year ASCVD Risk": f"{risk:.1%}",
                "Risk Category": "High" if risk >= 0.20 else "Intermediate" if risk >= 0.075 else "Low",
                "Recommendation": "High-intensity statin recommended" if risk >= 0.20 else "Shared decision making for statin" if risk >= 0.075 else "Lifestyle therapy recommended"
            }

            # Generate pdf
            pdf_bytes = create_pdf_report(report_data, "ASCVD Risk Calculator")
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name="ascvd_risk_report.pdf",
                mime="application/pdf",
                key="ascvd_pdf"
            )

        except ValueError as e:
            st.error(f"❌ Input Error: {str(e)}")


# -----------------------------
# BP Category
# -----------------------------

elif tool == "Blood Pressure Category":
    st.title("Blood Pressure Category")

    st.markdown("""
    Classifies blood pressure using the
    [2017 ACC/AHA Guideline for High Blood Pressure in Adults](https://doi.org/10.1161/HYP.0000000000000065).
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        sbp = st.slider("Systolic BP (mmHg)", 50, 250, 120, step=1)
    with col2:
        dbp = st.slider("Diastolic BP (mmHg)", 40, 150, 80, step=1)

    if st.button("Classify BP"):
        try:
            validate_bp_input(sbp, dbp)
            category = bp_category(sbp, dbp)
            st.metric("Category", category)

            interpretations = {
                "Normal": "No antihypertensive medication indicated. Promote healthy lifestyle.",
                "Elevated": "Lifestyle modification recommended.",
                "Stage 1 Hypertension": "Lifestyle + consider medication based on ASCVD risk.",
                "Stage 2 Hypertension": "Lifestyle + initiate 2-drug therapy."
            }
            st.markdown(f"**Recommendation**: {interpretations.get(category, 'Monitor closely.')}")

            # Store result
            st.session_state.bp_category = category

            # Prepare report data
            report_data = {
                "Patient ID": patient_id or "N/A",
                "Blood Pressure": f"{sbp}/{dbp} mmHg",
                "Classification": category,
                "Recommendation": interpretations.get(category, "Monitor closely.")
            }

            # ✅ Generate PDF
            pdf_bytes = create_pdf_report(report_data, title="Blood Pressure")

            # ✅ Add download button
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name="bp_category_report.pdf",
                mime="application/pdf",
                key="bp_pdf"  # Unique key for this tool
            )

        except ValueError as e:
            st.error(f"❌ Input Error: {str(e)}")


# -----------------------------
# CHA₂DS₂-VASc
# -----------------------------

elif tool == "CHA₂DS₂-VASc Stroke Risk":
    st.title("CHA₂DS₂-VASc Stroke Risk Score")

    st.markdown("""
    Estimates stroke risk in atrial fibrillation patients.
    Based on [Lip et al, *Chest* 2010](https://www.sciencedirect.com/science/article/abs/pii/S0012369210600670).
    """)

    st.markdown("""
    **Scoring**:
    - **2 points**: Age ≥ 75, Prior stroke/TIA/thromboembolism
    - **1 point**: Age 65 - 74, Hypertension, Diabetes, CHF, Vascular disease, Female sex
    """)

    col1, col2 = st.columns(2)
    with col1:
        chf = st.checkbox("Congestive Heart Failure (1 pt)")
        hypertension = st.checkbox("Hypertension (1 pt)")
        age_ge_75 = st.checkbox("Age ≥75 (2 pts)")
        diabetes = st.checkbox("Diabetes (1 pt)")
    with col2:
        stroke = st.checkbox("Stroke/TIA/Thromboembolism (2 pts)")
        vascular = st.checkbox("Vascular Disease (1 pt)")
        age_65_74 = st.checkbox("Age 65-74 (1 pt)")
        female = st.checkbox("Female (1 pt)")

    if st.button("Calculate CHA₂DS₂-VASc Score"):
        data = {
            "chf": int(chf),
            "hypertension": int(hypertension),
            "age_ge_75": int(age_ge_75),
            "diabetes": int(diabetes),
            "stroke": int(stroke),
            "vascular": int(vascular),
            "age_65_74": int(age_65_74),
            "female": int(female),
        }

        try:
            validate_cha2ds2vasc_input(data)
            score = cha2ds2vasc(data)
            st.metric("CHA₂DS₂-VASc Score", score)

            if score == 0:
                risk_text = "Very Low Risk"
                recommendation = "Anticoagulation not recommended."
                st.success(f"**{risk_text}**: {recommendation}")
            elif score == 1:
                risk_text = "Low-Intermediate Risk"
                recommendation = "Shared decision making for anticoagulation."
                st.warning(f"**{risk_text}**: {recommendation}")
            else:
                risk_text = "High Risk"
                recommendation = "Oral anticoagulation recommended (Class I, LOE A)."
                st.error(f"**{risk_text}**: {recommendation}")

            # Store result
            st.session_state.cha2ds2vasc_score = score

            # Prepare report data
            factors = [f for f, checked in [
                ("Congestive Heart Failure", chf),
                ("Hypertension", hypertension),
                ("Age ≥75 years", age_ge_75),
                ("Diabetes", diabetes),
                ("Prior Stroke/TIA/Thromboembolism", stroke),
                ("Vascular Disease", vascular),
                ("Age 65-74 years", age_65_74),
                ("Female Sex", female)
            ] if checked]

            report_data = {
                "Patient ID": patient_id or "N/A",
                "CHA2DS2-VASc Score": str(score),
                "Risk Level": risk_text,
                "Risk Factors Present": factors if factors else ["None"],
                "Recommendation": recommendation
            }

            # Generate PDF
            pdf_bytes = create_pdf_report(report_data, title="CHA2DS2-VASc")  # ✅ Plain text

            # Download button
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name="cha2ds2vasc_report.pdf",
                mime="application/pdf",
                key="cha2ds2vasc_pdf"
            )

        except ValueError as e:
            st.error(f"❌ Input Error: {str(e)}")


# -----------------------------
# ECG Interpretation
# -----------------------------

elif tool == "ECG Interpretation":
    st.title("ECG Interpretation")

    st.markdown("### Rhythm Analysis")
    col1, col2 = st.columns(2)
    with col1:
        rate = st.slider("Heart Rate (bpm)", 20, 250, 75, step=1)
        regular = st.checkbox("Rhythm Regular?")
    with col2:
        p_waves_present = st.checkbox("P-Waves Present?")

    st.markdown("---")
    st.markdown("### 12-Lead Findings")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ST & QT")
        st_elevation = st.checkbox("ST Elevation?")
        if st_elevation:
            st_elevation_leads = st.text_input("ST Elevation Leads", "V1-V4")
        else:
            st_elevation_leads = None

        qt_interval_ms = st.slider("QT Interval (ms)", 300, 700, 400, step=5)
        rr_interval_ms = st.slider("RR Interval (ms)", 300, 1200, 800, step=5)

    with col2:
        st.subheader("Other Findings")
        lvh_criteria_met = st.checkbox("LVH Criteria Met?")
        pathological_q_waves = st.checkbox("Pathological Q Waves?")
        if pathological_q_waves:
            q_wave_leads = st.text_input("Q Wave Leads", "II, III, aVF")
        else:
            q_wave_leads = None
        t_wave_inversion = st.checkbox("T-Wave Inversion?")
        pr_interval_ms = st.slider("PR Interval (ms)", 120, 300, 160, step=1)

    if st.button("Interpret ECG"):
        rhythm_data = {
            "rate": rate,
            "regular": regular,
            "p_waves_present": p_waves_present,
        }
        lead_data = {
            "st_elevation": st_elevation,
            **({"st_elevation_leads": st_elevation_leads} if st_elevation and st_elevation_leads else {}),
            "qt_interval_ms": qt_interval_ms,
            "rr_interval_ms": rr_interval_ms,
            "lvh_criteria_met": lvh_criteria_met,
            "pathological_q_waves": pathological_q_waves,
            **({"q_wave_leads": q_wave_leads} if pathological_q_waves and q_wave_leads else {}),
            "t_wave_inversion": t_wave_inversion,
            "pr_interval_ms": pr_interval_ms,
        }

        try:
            validate_ecg_rhythm_input(rhythm_data)
            validate_ecg_12lead_input(lead_data)

            rhythm = interpret_rhythm(rate, regular, p_waves_present)
            findings = interpret_12lead_findings(lead_data)
            comprehensive = interpret_ecg_comprehensive({**rhythm_data, **lead_data})

            # Store result
            st.session_state.ecg_rhythm = rhythm

            # Create tabs for better UX (New)
            tab1, tab2, tab3 = st.tabs(["Rhythm", "12-Lead Findings", "Comprehensive Report"])

            with tab1:
                st.subheader("Rhythm Interpretation")
                st.success(f"**{rhythm}**")
                st.write(f"Confidence: {comprehensive['rhythm']['confidence']}")

            with tab2:
                st.subheader("Findings")
                if findings["findings"]:
                    for f in findings["findings"]:
                        st.write(f"• {f}")
                else:
                    st.info("No significant findings.")

            with tab3:
                st.subheader("Overall Risk")
                st.metric("Risk Level", comprehensive["overall_risk"])
                st.subheader("Recommendations")
                for rec in comprehensive["recommendations"]:
                    st.write(f"• {rec}")

            # Prepare report data
            ecg_findings = findings["findings"] if findings["findings"] else ["No significant findings"]
            report_data = {
                "Patient ID": patient_id or "N/A",
                "Rhythm Interpretation": rhythm,
                "Confidence": comprehensive["rhythm"]["confidence"],
                "12-Lead Findings": ecg_findings,
                "Overall Risk": comprehensive["overall_risk"],
                "Recommendations": comprehensive["recommendations"]
            }

            # ✅ Generate PDF
            pdf_bytes = create_pdf_report(report_data, title="ECG Interpretation")

            # ✅ Add download button
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_bytes,
                file_name="ecg_interpretation_report.pdf",
                mime="application/pdf",
                key="ecg_pdf"
            )

        except ValueError as e:
            st.error(f"❌ Input Error: {str(e)}")
