import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

from config import FEATURES
from data import generate_dummy_data, feature_bounds
from model import build_models
from validation import in_range_flags, pass_fail, status_badge
from visual import (
    indicator_chart, bar_compare, strength_histogram,
    roi_stacked_bar, shap_local_bar
)
from roi import cement_roi
from pdf_export import pdf_bytes

st.set_page_config(page_title="Cement 28-Day Strength Predictor", page_icon="https://github.com/MiariHub/cement_prediction/blob/main/electro-pi.png" ,layout="wide")


# --- App State ---
spec_min = 42.5
bounds = feature_bounds()
df = generate_dummy_data()
model = build_models().fit(df[FEATURES], df["Strength"])
baseline = df["Strength"].mean()

# --- Sidebar Inputs ---
with st.sidebar:
    st.title("🔧 Input Controls")
    user_inputs = {}
    for f in FEATURES:
        lo, hi = bounds[f]
        default = (lo + hi) / 2
        user_inputs[f] = st.slider(f, lo, hi, value=float(round(default, 2)))

    st.markdown("---")
    st.subheader("📉 ROI Assumptions")
    monthly_batches = st.number_input("Monthly Batches", value=500)
    volume_per_batch = st.number_input("Volume per Batch (m³)", value=5.0)
    cement_content = st.number_input("Cement Content (kg/m³)", value=300.0)
    reduction_pct = st.slider("Overdesign Reduction (%)", 0.0, 10.0, 2.0)
    cement_cost = st.number_input("Cement Cost ($/ton)", value=110.0)
    scrap_before = st.slider("Scrap Before (%)", 0.0, 10.0, 5.0)
    scrap_after = st.slider("Scrap After (%)", 0.0, 10.0, 2.0)
    batch_cost = st.number_input("Cost per Batch ($)", value=500.0)
    lab_tests = st.number_input("Lab Tests / Month", value=50)
    hours_per_test = st.number_input("Hours per Test", value=1.0)
    labor_rate = st.number_input("Labor Rate ($/h)", value=40.0)
    impl_cost = st.number_input("One-time Implementation Cost ($)", value=20000.0)

# --- Main Layout ---
st.title("🧪 Cement 28-Day Strength Predictor")

col1, col2 = st.columns([1, 3])
with col1:
    p, lo, hi = model.predict(pd.DataFrame([user_inputs]))  # prediction
    p, lo, hi = float(p[0]), float(lo[0]), float(hi[0])
    badge = status_badge(p, spec_min)
    st.markdown(f"### Prediction: {p:.2f} MPa {badge}")
    st.plotly_chart(indicator_chart(p, spec_min), use_container_width=True)

    flags = in_range_flags(user_inputs, bounds)
    oob = [k for k, ok in flags.items() if not ok]
    if oob:
        st.warning("⚠️ Some values are out of bounds:")
        for k in oob:
            v = user_inputs[k]
            lo, hi = bounds[k]
            st.markdown(f"🟥 **{k}** = {v:.2f} (Expected: {lo}–{hi})")

    if p < spec_min:
        st.info("Try adjusting inputs to meet the minimum strength requirement.")

with col2:
    st.plotly_chart(bar_compare(p, baseline), use_container_width=True)
    st.plotly_chart(strength_histogram(df["Strength"]), use_container_width=True)

# --- SHAP & ROI ---
shap_col, roi_col = st.columns(2)

with shap_col:
    st.subheader("🔍 SHAP Explanation")
    shap_fig = shap_local_bar(model.rf, pd.DataFrame([user_inputs]))
    st.plotly_chart(shap_fig, use_container_width=True)
    st.info("Some SHAP values may be zero if the feature was not used in the decision path.")

with roi_col:
    st.subheader("💰 ROI Summary")
    roi = cement_roi(
        monthly_batches, volume_per_batch, cement_content,
        reduction_pct, cement_cost, scrap_before, scrap_after,
        batch_cost, lab_tests, hours_per_test, labor_rate, impl_cost
    )

    st.plotly_chart(roi_stacked_bar(roi["cement_saved_cost"], roi["scrap_savings"], roi["lab_savings"]), use_container_width=True)

    st.markdown(f"**Total Savings:** ${roi['total_savings']:,.0f}")
    if roi["roi"] is not None:
        st.markdown(f"**ROI:** {roi['roi'] * 100:.1f}%")
    else:
        st.markdown("ROI: Insufficient savings for ROI computation.")
    if roi["payback_months"]:
        st.markdown(f"**Payback:** {roi['payback_months']:.1f} months")

    if roi["total_savings"] <= 0:
        st.info("Try increasing cement reduction % or lowering scrap rate to see ROI impact.")

# --- Export Buttons ---
st.markdown("---")
st.subheader("📤 Export Report")
pdf = pdf_bytes(user_inputs, p, lo, hi, spec_min, badge, roi)
if pdf:
    st.download_button("📄 Download PDF", data=pdf, file_name="cement_strength_report.pdf", mime="application/pdf")
else:
    st.error("PDF generation failed. Try reducing input fields or refresh.")





