import streamlit as st
import pandas as pd
import joblib
import random
from datetime import date

# =========================
# CONFIG & CSS
# =========================
st.set_page_config(page_title="Liver Trace", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Custom Font and Global Colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Result Banner Positive */
    .banner-positive {
        background: linear-gradient(135deg, #1e3a8a, #172554); /* Deep Medical Blue */
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border: 1px solid #1e40af;
        position: relative;
        overflow: hidden;
    }
    .banner-negative {
        background: linear-gradient(135deg, #0369a1, #075985); /* Calming Sky/Medical Blue */
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border: 1px solid #0284c7;
        position: relative;
        overflow: hidden;
    }
    
    .status-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 0.375rem;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
    }
    .badge-elevated { background-color: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
    .badge-normal { background-color: #d1fae5; color: #047857; border: 1px solid #6ee7b7; }
    .badge-low { background-color: #fef3c7; color: #b45309; border: 1px solid #fcd34d; }
    
    /* Card Style */
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        height: 320px; /* Fixed height for absolute symmetry */
        display: flex;
        flex-direction: column;
        overflow-y: auto;
    }
    
    /* Custom Scrollbar for Cards */
    .card::-webkit-scrollbar { width: 6px; }
    .card::-webkit-scrollbar-track { background: transparent; }
    .card::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD MODEL
# =========================
@st.cache_resource
def load_model():
    return joblib.load("models/liver_pipeline.joblib")

try:
    model = load_model()
except Exception as e:
    st.error(f"Failed to load model: {e}")
    model = None

# =========================
# REFERENCE RANGES LOGIC
# =========================
def check_status(val, min_val, max_val):
    if val < min_val:
        return "Low", "badge-low"
    elif val > max_val:
        return "Elevated", "badge-elevated"
    return "Normal", "badge-normal"

references = {
    "TB": {"name": "Total Bilirubin", "range": "0.1 - 1.2", "min": 0.1, "max": 1.2, "unit": "mg/dL"},
    "DB": {"name": "Direct Bilirubin", "range": "0.0 - 0.3", "min": 0.0, "max": 0.3, "unit": "mg/dL"},
    "Alkphos": {"name": "Alk. Phosphatase", "range": "44 - 147", "min": 44, "max": 147, "unit": "U/L"},
    "Sgpt": {"name": "SGPT (ALT)", "range": "7 - 56", "min": 7, "max": 56, "unit": "U/L"},
    "Sgot": {"name": "SGOT (AST)", "range": "8 - 45", "min": 8, "max": 45, "unit": "U/L"},
    "TP": {"name": "Total Protein", "range": "6.0 - 8.3", "min": 6.0, "max": 8.3, "unit": "g/dL"},
    "ALB": {"name": "Albumin", "range": "3.4 - 5.4", "min": 3.4, "max": 5.4, "unit": "g/dL"},
    "A/G Ratio": {"name": "A/G Ratio", "range": "1.0 - 2.5", "min": 1.0, "max": 2.5, "unit": ""}
}

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("<h2 style='font-weight: 800; color: #2563eb; margin-bottom: 0;'>Liver Trace</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color: #64748b; font-size: 0.875rem; margin-top: 0;'>Enter patient details and laboratory results</p>", unsafe_allow_html=True)
st.sidebar.divider()

with st.sidebar.expander("1. Demographics", expanded=True):
    patient_id_input = st.text_input("Patient ID (Optional)", placeholder="Auto-generated if empty")
    age = st.number_input("Age", min_value=0, max_value=120, value=0)
    gender = st.selectbox("Gender", ["Male", "Female"])

with st.sidebar.expander("2. Bilirubin Panel", expanded=False):
    tb = st.number_input("Total Bilirubin (mg/dL)", value=0.0, step=0.1)
    db = st.number_input("Direct Bilirubin (mg/dL)", value=0.0, step=0.1)

with st.sidebar.expander("3. Hepatic Enzymes", expanded=False):
    alkphos = st.number_input("Alk. Phosphatase (U/L)", value=0, step=1)
    sgpt = st.number_input("SGPT (ALT) (U/L)", value=0, step=1)
    sgot = st.number_input("SGOT (AST) (U/L)", value=0, step=1)

with st.sidebar.expander("4. Proteins", expanded=False):
    tp = st.number_input("Total Protein (g/dL)", value=0.0, step=0.1)
    alb = st.number_input("Albumin (g/dL)", value=0.0, step=0.1)
    ag_ratio = st.number_input("A/G Ratio", value=0.0, step=0.1)

st.sidebar.write("")
predict_clicked = st.sidebar.button("Generate Report", use_container_width=True, type="primary")

# =========================
# MAIN CONTENT
# =========================
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<h1 style='font-weight: 800; color: #1e3a8a; margin-bottom: 0; padding-top: 0;'>Liver Function Assessment</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 1.125rem; font-weight: 500; margin-top: 0;'>AI-Assisted Diagnostic Tool</p>", unsafe_allow_html=True)
with col2:
    if 'id_suffix' not in st.session_state:
        st.session_state.id_suffix = f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}-{random.randint(1000, 9999)}"
    
    auto_id = f"#{int(age)}{st.session_state.id_suffix}"
    display_patient_id = patient_id_input.strip() if patient_id_input.strip() else auto_id

    st.markdown(f"""
    <div style='background-color: white; padding: 0.75rem; border-radius: 0.5rem; border: 1px solid #e2e8f0; text-align: right; font-size: 0.875rem; color: #64748b; margin-top: 1rem;'>
        <div>Date: <span style='font-weight: 700; color: #1e293b;'>{date.today().strftime("%b %d, %Y")}</span></div>
        <div>Patient ID: <span style='font-weight: 700; color: #1e293b; font-family: monospace;'>{display_patient_id}</span></div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

if predict_clicked and model is not None:
    # 0. Input Validation
    if age == 0 or tb == 0.0 or tp == 0.0:
        st.error("⚠️ **Invalid Data:** Please enter real laboratory values. Parameters like Age, Bilirubin, and Protein cannot be 0 for a real patient.")
        st.stop()

    # 1. Prepare Data
    input_data = pd.DataFrame([{
        "Age": age,
        "Gender": gender,
        "TB": tb,
        "DB": db,
        "Alkphos": alkphos,
        "Sgpt": sgpt,
        "Sgot": sgot,
        "TP": tp,
        "ALB": alb,
        "A/G Ratio": ag_ratio
    }])

    # 2. Predict
    try:
        pred = model.predict(input_data)[0]
        prob = model.predict_proba(input_data)[0][1]
        
        is_disease = (pred == 1)
        prob_pct = int(prob * 100) if is_disease else int((1 - prob) * 100)
        
        banner_class = "banner-positive" if is_disease else "banner-negative"
        title_text = "Positive for Liver Disease" if is_disease else "Negative for Liver Disease"
        desc_text = "The model indicates a high probability of hepatic complications. Immediate clinical review is recommended." if is_disease else "The model indicates a low probability of hepatic complications. Routine monitoring is suggested."
        circle_color = "#ef4444" if is_disease else "#10b981"
        
        # 3. Top Banner
        st.markdown(f"""
        <div class="{banner_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span style="height: 0.75rem; width: 0.75rem; background-color: {circle_color}; border-radius: 50%; display: inline-block;"></span>
                        <span style="font-size: 0.75rem; font-weight: 700; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.1em;">Diagnosis Prediction</span>
                    </div>
                    <div style="font-size: 2.25rem; font-weight: 800; line-height: 1.2;">{title_text}</div>
                    <div style="color: #94a3b8; margin-top: 0.5rem; max-width: 600px;">{desc_text}</div>
                </div>
                <div style="background-color: rgba(255,255,255,0.1); backdrop-filter: blur(8px); padding: 1.25rem; border-radius: 0.75rem; border: 1px solid rgba(255,255,255,0.2); text-align: center; min-width: 140px;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: #cbd5e1; font-weight: 600; margin-bottom: 0.25rem;">Confidence</div>
                    <div style="font-size: 3rem; font-weight: 800; line-height: 1;">{prob_pct}<span style="font-size: 1.5rem; color: #cbd5e1;">%</span></div>
                </div>
            </div>
        </div>
        <br>
        """, unsafe_allow_html=True)

        # Calculate Statuses
        vals = {"TB": tb, "DB": db, "Alkphos": alkphos, "Sgpt": sgpt, "Sgot": sgot, "TP": tp, "ALB": alb, "A/G Ratio": ag_ratio}
        
        abnormal_factors = []
        for key, val in vals.items():
            status, badge = check_status(val, references[key]["min"], references[key]["max"])
            if status != "Normal":
                abnormal_factors.append((references[key]["name"], status, badge))

        # 4. Summary Cards
        col1, col2 = st.columns(2)
        
        with col1:
            risk_li = ""
            if not abnormal_factors:
                risk_li = "<li><span style='color: #64748b;'>No significant abnormal biomarkers detected.</span></li>"
            else:
                for name, status, badge in abnormal_factors:
                    risk_li += f"<li style='display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; background-color: #f8fafc; border-radius: 0.5rem; border: 1px solid #f1f5f9; margin-bottom: 0.5rem;'><span style='font-weight: 500; color: #334155;'>{name}</span><span class='status-badge {badge}'>{status}</span></li>"
            
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <h3 style="font-size: 1.125rem; font-weight: 700; color: #1e3a8a; margin: 0;">Key Risk Factors</h3>
                </div>
                <ul style="list-style-type: none; padding: 0; margin: 0;">
                    {risk_li}
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <h3 style="font-size: 1.125rem; font-weight: 700; color: #1e3a8a; margin: 0;">Patient Summary</h3>
                </div>
                <ul style="list-style-type: none; padding: 0; margin: 0; color: #475569; font-size: 1.05rem; display: flex; flex-direction: column; flex: 1; justify-content: space-evenly; padding-bottom: 0.5rem; margin-top: 1rem;">
                    <li style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 1rem; border-bottom: 1px dashed #e2e8f0;">
                        <span style="font-weight: 500;">Age / Gender</span>
                        <span style="font-weight: 700; color: #1e3a8a; background-color: #eff6ff; padding: 0.35rem 0.85rem; border-radius: 9999px; font-size: 0.95rem;">{age} <span style="color: #94a3b8; margin: 0 0.25rem;">|</span> {gender}</span>
                    </li>
                    <li style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 1rem; border-bottom: 1px dashed #e2e8f0;">
                        <span style="font-weight: 500;">A/G Ratio</span>
                        <span style="font-family: monospace; font-weight: 700; color: #1e3a8a; font-size: 1.15rem;">{round(ag_ratio, 2)}</span>
                    </li>
                    <li style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 0.5rem;">
                        <span style="font-weight: 500;">Total Protein</span>
                        <span style="font-family: monospace; font-weight: 700; color: #1e3a8a; font-size: 1.15rem;">{round(tp, 2)} <span style="font-size: 0.9rem; color: #94a3b8;">g/dL</span></span>
                    </li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("")
        st.write("")

        # 5. Biomarker Analysis Grid
        st.markdown("<h3 style='font-size: 1.25rem; font-weight: 700; color: #1e3a8a; margin-bottom: 1rem;'>Biomarker Analysis</h3>", unsafe_allow_html=True)
        
        table_rows = ""
        for key, val in vals.items():
            ref = references[key]
            status, badge = check_status(val, ref["min"], ref["max"])
            
            bg_color = "rgba(254, 226, 226, 0.3)" if status == "Elevated" else ("rgba(254, 243, 199, 0.3)" if status == "Low" else "transparent")
            val_color = "#dc2626" if status == "Elevated" else ("#d97706" if status == "Low" else "#475569")
            display_val = round(val, 2) if isinstance(val, float) else val
            
            table_rows += f"<div style='display: flex; flex-wrap: wrap; padding: 1rem; border-bottom: 1px solid #f1f5f9; align-items: center; background-color: {bg_color};'><div style='flex: 1; min-width: 120px; font-weight: 600; color: #1e3a8a; padding-left: 0.5rem;'>{ref['name']}</div><div style='flex: 1; min-width: 100px; text-align: right; font-family: monospace; font-weight: 700; color: {val_color}; font-size: 1rem;'>{display_val} <span style='font-size: 0.75rem; font-weight: 400; color: #94a3b8;'>{ref['unit']}</span></div><div style='flex: 1; min-width: 100px; text-align: center; font-size: 0.875rem; color: #94a3b8;'>{ref['range']}</div><div style='flex: 1; min-width: 100px; text-align: right;'><span class='status-badge {badge}'>{status}</span></div></div>"

        st.markdown(f"""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 1rem; overflow: hidden; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);">
            <div style="display: flex; flex-wrap: wrap; background-color: #eff6ff; padding: 1rem; border-bottom: 1px solid #bfdbfe; font-size: 0.75rem; font-weight: 700; color: #1e40af; text-transform: uppercase; letter-spacing: 0.05em;">
                <div style="flex: 1; min-width: 120px; padding-left: 0.5rem;">Biomarker</div>
                <div style="flex: 1; min-width: 100px; text-align: right;">Input Value</div>
                <div style="flex: 1; min-width: 100px; text-align: center;">Ref. Range</div>
                <div style="flex: 1; min-width: 100px; text-align: right; padding-right: 1rem;">Status</div>
            </div>
            {table_rows}
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error during prediction: {e}")

else:
    if not predict_clicked:
        st.info("👋 Welcome to Liver Trace! Please enter the patient's lab results in the sidebar and click 'Generate Report' to see the diagnosis prediction.")
