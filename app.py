import streamlit as st
import pandas as pd
import joblib
import time
import plotly.graph_objects as go
from quant_signal_engine import QuantSignalEngine
from agentic_research_desk import research_app

st.set_page_config(page_title="Market Intelligence Engine", layout="wide", initial_sidebar_state="expanded")
st.markdown("<style>.main {background-color: #0e1117;} h1, h2, h3 {color: #00d2ff;}</style>", unsafe_allow_html=True)

st.title("🧠 Agentic Market Intelligence Engine")
st.markdown("Automated Quantitative Research Desk | Llama 3 & Scikit-Learn | Scenario Simulation Ready")
st.divider()

st.sidebar.header("Data Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload Options CSV", type=["csv"])

st.sidebar.header("Macro & ML Context")
vix_input = st.sidebar.slider("Current VIX", 10.0, 40.0, 24.5)
vix_vel = st.sidebar.slider("VIX Velocity (1-Day Change)", -5.0, 5.0, 0.0)
prev_regime = st.sidebar.selectbox("Previous Day Regime", options=[("Chop", 0), ("Trend", 1)], format_func=lambda x: x[0])[1]
sentiment_input = st.sidebar.slider("Macro Sentiment", -1.0, 1.0, -0.5)
macro_text = st.sidebar.text_area("Live News Context", "Treasury yields remain stable.")

st.sidebar.header("⚠️ Scenario Simulation")
price_shock_pct = st.sidebar.slider("Spot Price Shock (%)", -5.0, 5.0, 0.0, step=0.5)

if uploaded_file is not None:
    with open("temp_chain.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    try:
        raw_df = pd.read_csv("temp_chain.csv")
        base_spot = raw_df['active_underlying_price'].iloc[0]
    except pd.errors.ParserError:
        st.error("🚨 CSV Format Error: Ensure headers are on row 1.")
        st.stop()
    except Exception:
        base_spot = 4576.00

    simulated_spot = base_spot * (1 + (price_shock_pct / 100))

    with st.spinner("Calculating Institutional Greeks..."):
        engine = QuantSignalEngine("temp_chain.csv", spot_price=simulated_spot)
        quant_signal = engine.calculate_net_gex()
    
    if price_shock_pct != 0.0:
        st.warning(f"🚨 SIMULATION ACTIVE: Spot Price Shifted by {price_shock_pct}% to {simulated_spot:.2f}")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Net GEX", f"${quant_signal.get('net_gex_billions', 0)}B")
    c2.metric("Dominant", quant_signal.get('dominant_exposure', 'N/A'))
    c3.metric("Gamma Flip", quant_signal.get('gamma_flip_strike', 'N/A'))
    c4.metric("Regime", quant_signal.get('implied_regime', 'N/A'))

    st.divider()
    st.subheader("📊 Strike-Level Gamma Exposure (GEX) Profile")
    profile_df = quant_signal['strike_profile']
    chart_df = profile_df[(profile_df['strike_price'] >= simulated_spot * 0.85) & (profile_df['strike_price'] <= simulated_spot * 1.15)]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=chart_df[chart_df['gex']>0]['strike_price'], y=chart_df[chart_df['gex']>0]['gex'], name='Call GEX', marker_color='#00FA9A'))
    fig.add_trace(go.Bar(x=chart_df[chart_df['gex']<0]['strike_price'], y=chart_df[chart_df['gex']<0]['gex'], name='Put GEX', marker_color='#FF4500'))
    fig.add_vline(x=simulated_spot, line_dash="dash", line_color="white", annotation_text="Spot")
    fig.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', font_color='white', barmode='relative')
    st.plotly_chart(fig, use_container_width=True)

    with st.spinner("Running ML Forecasting Engine..."):
        try:
            model = joblib.load("regime_model.pkl")
            features = pd.DataFrame([{'net_gex': quant_signal['net_gex_billions'], 'vix': vix_input, 'macro_sentiment': sentiment_input, 'vix_velocity': vix_vel, 'prev_regime': prev_regime}])
            prob = round(model.predict_proba(features)[0][1] * 100, 2)
        except:
            prob = 50.0 
    
    st.subheader(f"🤖 ML Forecast: {prob}% Probability of Volatility Expansion")
    st.progress(int(prob))

    if st.button("Generate Institutional Briefing"):
        with st.spinner("LangGraph Agents Synthesizing..."):
            sim_context = f"[SCENARIO SIMULATION ACTIVE: Spot shocked by {price_shock_pct}%. Evaluate as a stress test.] " if price_shock_pct != 0 else ""
            result = research_app.invoke({
                "quant_signal": quant_signal, "ml_forecast": prob,
                "macro_context": sim_context + macro_text,
                "quant_summary": "", "final_thesis": ""
            })
            st.success("Brief Generation Complete")
            st.info(result['final_thesis'])
else:
    st.warning("👈 Upload an options chain CSV in the sidebar.")