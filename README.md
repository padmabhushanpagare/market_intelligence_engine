# Market Intelligence Engine 🧠📈
**Agentic AI & Quantitative Research Workflow Automation**

This repository contains a production-grade Market Intelligence Engine designed to automate the daily workflow of a macroeconomic research desk. By integrating quantitative data engineering, machine learning forecasting, and on-premise generative AI orchestration, this system synthesizes raw derivatives data into actionable, client-ready market intelligence briefs.

## 🏗️ System Architecture

The engine operates on a three-tier architecture:

1. **The Quantitative Data Pipeline (`pandas`, `numpy`)**
   - Ingests raw, institutional-grade options chain data (CSV).
   - Computes complex intraday risk metrics, specifically **Net Gamma Exposure (GEX)**, to identify dealer positioning and implied market volatility.
   - Dynamically calculates the **Zero Gamma Level (Gamma Flip)** using a strict liquidity window, identifying the exact strike price where market makers transition from volatility suppression to acceleration.

2. **The Predictive ML Model (`scikit-learn`)**
   - Utilizes a `RandomForestClassifier` trained on historical GEX, VIX, and macroeconomic sentiment data.
   - Incorporates **Historical Regime Memory** (Markov-inspired transition probabilities based on VIX velocity and T-1 regimes).
   - Outputs a statistical probability forecasting the daily market regime (High Volatility Trend vs. Mean-Reverting Chop).

3. **The Agentic Reasoning Loop (LangGraph, Ollama/Llama 3)**
   - Orchestrates a multi-agent workflow (Quant Analyst, Macro Economist, Head of Research).
   - Executes entirely **on-premise** via Ollama to ensure strict data privacy and model risk governance.
   - Synthesizes the data into a cohesive, professional intraday research thesis utilizing programmatic, deterministic guardrails to prevent LLM financial hallucination.

## 🛠️ Tech Stack
* **Data Engineering:** Python, Pandas, NumPy
* **Machine Learning:** Scikit-Learn, Joblib
* **Agentic AI:** LangGraph, LangChain, Ollama (Llama 3)
* **Frontend/Visualization:** Streamlit, Plotly
* **Environment:** Executed locally for enterprise data security.

## 🚀 Key Features
* **Automated Workflow Modernization:** Replaces manual data aggregation and thesis drafting with an intelligent, autonomous pipeline.
* **Microstructure Visualization:** Renders dynamic Plotly charts highlighting Call/Put walls and critical pinning levels.
* **Scenario Simulation Engine:** Allows users to stress-test the market by injecting a hypothetical spot price shock, forcing the math, the ML model, and the AI agents to dynamically recalculate and draft an emergency thesis.

## ⚙️ Execution Flow

1. **Setup:** Ensure you have a standard institutional options chain CSV (with `strike_price`, `option_type`, `open_interest`, `gamma`, and `active_underlying_price`) placed in the root directory.
2. **Train the ML Model:** `python ml_regime_model.py` (Generates the `.pkl` probability model with regime memory).
3. **Run the Dashboard:** `streamlit run app.py` (Launches the interactive visualization and Agentic AI reasoning loop).

---
*Architected for quantitative research modernization, advanced risk management, and AI-native financial analytics.*