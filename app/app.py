import streamlit as st
import pandas as pd
import joblib

# =========================
# LOAD MODEL (PIPELINE)
# =========================
model = joblib.load("models/liver_pipeline.joblib")


# =========================
# TITLE
# =========================
st.set_page_config(page_title="Liver Disease Prediction")
st.title("🩺 Liver Disease Prediction")

st.write("Masukkan data pasien:")


# =========================
# INPUT FORM
# =========================
age = st.number_input("Age", min_value=0, max_value=100, value=30)

gender = st.selectbox("Gender", ["Male", "Female"])

tb = st.number_input("Total Bilirubin", value=1.0)
db = st.number_input("Direct Bilirubin", value=0.3)
alkphos = st.number_input("Alkaline Phosphotase", value=200)
sgpt = st.number_input("SGPT", value=30)
sgot = st.number_input("SGOT", value=40)
tp = st.number_input("Total Protein", value=6.5)
alb = st.number_input("Albumin", value=3.2)
ag_ratio = st.number_input("A/G Ratio", value=0.9)


# =========================
# PREDICTION
# =========================
if st.button("🔍 Predict"):

    # ✅ input dalam format RAW (pipeline akan handle semuanya)
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

    try:
        # ✅ prediksi
        pred = model.predict(input_data)[0]
        prob = model.predict_proba(input_data)[0][1]

        # =========================
        # OUTPUT
        # =========================
        if pred == 1:
            st.error(f"⚠️ Liver Disease (Probability: {prob:.2%})")
        else:
            st.success(f"✅ No Liver Disease (Probability: {1 - prob:.2%})")

    except Exception as e:
        st.error(f"Error: {e}")
