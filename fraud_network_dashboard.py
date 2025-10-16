import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from tensorflow.keras.models import load_model
import plotly.graph_objects as go

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Cybersecurity Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# CUSTOM CSS
# ===============================
st.markdown("""
<style>
body {
    background-color:#1f2233; 
    color:#f5f5f5; 
    font-family:'Helvetica',sans-serif;
}
h1,h2,h3,h4 {
    font-weight:700; 
    color:#000000;
}
.stButton button {
    background-color:#ff6f61; 
    color:white; 
    border-radius:10px; 
    height:45px; 
    font-weight:bold;
}
.stButton button:hover {
    background-color:#e0554f;
}
.metric-card {
    padding:25px; 
    border-radius:15px; 
    box-shadow:0 6px 12px rgba(0,0,0,0.5); 
    text-align:center;
}
.section-title {
    background: linear-gradient(90deg,#ff6f61,#ffb88c); 
    padding:10px; 
    border-radius:8px; 
    color:white; 
    margin-bottom:15px;
    text-align:center;
}
.sidebar .sidebar-content {
    background-color:#2b2f4a;
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# HEADER
# ===============================
st.markdown("<h1 style='text-align:center;'>Cybersecurity Monitoring Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#aaaaaa;'>Enterprise-grade Transaction & Network Threat Analytics</p>", unsafe_allow_html=True)
st.markdown("---")

# ===============================
# LOAD MODELS
# ===============================
MODEL_DIR = Path("models")
rf_fraud = joblib.load(MODEL_DIR / "rf_fraud.pkl")
scaler_amount = joblib.load(MODEL_DIR / "scaler_amount.pkl")
iso_network = joblib.load(MODEL_DIR / "iso_network.pkl")
scaler_network = joblib.load(MODEL_DIR / "scaler_network.pkl")
autoencoder = load_model(MODEL_DIR / "autoencoder_network.keras")

# ===============================
# FUNCTIONS
# ===============================
def predict_transaction(input_data):
    df = pd.DataFrame([input_data])
    df["Amount_scaled"] = scaler_amount.transform(df[["Amount"]])
    df.drop(columns=["Amount"], inplace=True)
    for v in [f"V{i}" for i in range(1,29)]:
        if v not in df.columns:
            df[v]=0
    df = df[[f"V{i}" for i in range(1,29)] + ["Hour","Amount_scaled"]]
    prob = rf_fraud.predict_proba(df)[0][1]
    pred = rf_fraud.predict(df)[0]
    return {"prediction": int(pred), "probability": float(prob)}

def predict_network(input_data):
    df = pd.DataFrame([input_data])
    df_scaled = scaler_network.transform(df)
    score = iso_network.decision_function(df_scaled)[0]
    pred = iso_network.predict(df_scaled)[0]
    status = "Anomaly Detected" if pred==-1 else "Normal"
    return {"score": float(score), "status": status}

# ===============================
# SIDEBAR
# ===============================
st.sidebar.header("Select Dashboard")
dashboard_type = st.sidebar.radio("", ["Transaction Dashboard", "Network Dashboard"])

# ===============================
# TRANSACTION DASHBOARD
# ===============================
if dashboard_type=="Transaction Dashboard":
    st.markdown("<div class='section-title'><h3>Transaction Fraud Analysis</h3></div>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns([1,1])
        with col1:
            time = st.number_input("Transaction Time",0,100000,500)
            amount = st.number_input("Transaction Amount",0.0,100000.0,120.5)
            hour = st.slider("Hour of Transaction",0,23,14)
        with col2:
            v_inputs = {f"V{i}": st.number_input(f"V{i}", -10.0, 10.0, 0.0) for i in range(1,6)}
    
    # Predict button
    st.markdown("<div style='text-align:center; margin-top:10px;'>", unsafe_allow_html=True)
    if st.button("Predict Transaction"):
        input_data = {"Time":time,"Amount":amount,"Hour":hour, **v_inputs}
        result = predict_transaction(input_data)

        # Risk colors
        if result['probability'] < 0.4:
            risk_color="#4CAF50"; risk_label="Low Risk"
        elif result['probability'] < 0.7:
            risk_color="#FF9800"; risk_label="Medium Risk"
        else:
            risk_color="#F44336"; risk_label="High Risk"

        # Metric cards
        st.markdown(f"""
        <div style='display:flex; gap:20px; margin-top:20px; margin-bottom:20px;'>
            <div class='metric-card' style='background-color:{risk_color}; flex:1;'>
                <h3>Fraud Risk</h3>
                <h1>{risk_label}</h1>
            </div>
            <div class='metric-card' style='background-color:#2196F3; flex:1;'>
                <h3>Fraud Probability</h3>
                <h1>{result['probability']*100:.2f}%</h1>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Plotly gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=result['probability']*100,
            title={'text': "Fraud Probability Gauge"},
            gauge={'axis': {'range':[0,100]},
                   'bar': {'color': risk_color},
                   'steps': [{'range':[0,40],'color':'#A5D6A7'},
                             {'range':[40,70],'color':'#FFCC80'},
                             {'range':[70,100],'color':'#EF9A9A'}]}))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# NETWORK DASHBOARD
# ===============================
else:
    st.markdown("<div class='section-title'><h3>Network Anomaly Analysis</h3></div>", unsafe_allow_html=True)
    with st.container():
        col1, col2 = st.columns([1,1])
        with col1:
            conn_count = st.number_input("Connection Count",0,10000,75)
            avg_bytes = st.number_input("Average Bytes",0,1000000,55000)
            max_bytes = st.number_input("Max Bytes",0,1000000,120000)
            unique_dst = st.number_input("Unique Destinations",0,1000,60)
        with col2:
            avg_duration = st.number_input("Average Duration(s)",0.1,10000.0,30.5)
            TCP = st.number_input("TCP Count",0,10000,50)
            UDP = st.number_input("UDP Count",0,10000,20)
            ICMP = st.number_input("ICMP Count",0,10000,5)

    # Predict button
    st.markdown("<div style='text-align:center; margin-top:10px;'>", unsafe_allow_html=True)
    if st.button("Predict Network"):
        payload = {"conn_count":conn_count,"avg_bytes":avg_bytes,"max_bytes":max_bytes,
                   "avg_duration":avg_duration,"unique_dst":unique_dst,
                   "TCP":TCP,"UDP":UDP,"ICMP":ICMP}
        result = predict_network(payload)
        status_color = "#F44336" if "Anomaly" in result['status'] else "#4CAF50"

        # Metric cards
        st.markdown(f"""
        <div style='display:flex; gap:20px; margin-top:20px; margin-bottom:20px;'>
            <div class='metric-card' style='background-color:{status_color}; flex:1;'>
                <h3>Network Status</h3>
                <h1>{result['status']}</h1>
            </div>
            <div class='metric-card' style='background-color:#2196F3; flex:1;'>
                <h3>Anomaly Score</h3>
                <h1>{result['score']:.3f}</h1>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Protocol counts bar chart
        protocols = ['TCP','UDP','ICMP']
        counts = [TCP, UDP, ICMP]
        fig = go.Figure([go.Bar(x=protocols, y=counts, marker_color=['#2196F3','#FF9800','#F44336'])])
        fig.update_layout(title_text='Protocol Counts', yaxis_title='Count', xaxis_title='Protocol')
        st.plotly_chart(fig, use_container_width=True)

        # Anomaly score gauge
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=result['score'],
            title={'text': "Anomaly Score"},
            gauge={'axis': {'range': [-1,1]},
                   'bar': {'color': status_color},
                   'steps': [{'range':[-1,0],'color':'#EF9A9A'},
                             {'range':[0,1],'color':'#A5D6A7'}]}))
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.markdown("<p style='text-align:center;color:#aaaaaa'>© 2025 Cybersecurity Dashboard | Enterprise Monitoring</p>", unsafe_allow_html=True)
