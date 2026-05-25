from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

class ResearchState(TypedDict):
    quant_signal: dict
    ml_forecast: float
    macro_context: str
    quant_summary: str
    final_thesis: str

llm = ChatOllama(model="llama3", temperature=0.1)

def quant_analyst(state: ResearchState):
    data, prob = state['quant_signal'], state['ml_forecast']
    prompt = f"Quant data: GEX {data.get('net_gex_billions', 0)}B, Dominant {data.get('dominant_exposure', 'Unknown')}. Zero Gamma Level at {data.get('gamma_flip_strike', 'N/A')}. ML probability of High Volatility is {prob}%. Write a 2-sentence structural summary citing the Zero Gamma Level."
    return {"quant_summary": llm.invoke([HumanMessage(content=prompt)]).content}

def macro_economist(state: ResearchState):
    return {"macro_context": state['macro_context']} 

def head_of_research(state: ResearchState):
    prob, flip_strike = state['ml_forecast'], state['quant_signal'].get('gamma_flip_strike', 'N/A')
    
    # Strict Guardrails
    if prob > 50:
        guardrail = f"HIGH volatility probability. Advise caution. Cite {flip_strike} as the critical pivot for acceleration. DO NOT mention mean-reversion."
    else:
        guardrail = f"LOW volatility probability. Advise chop/mean-reversion. Cite {flip_strike} as a heavy magnet/pin. DO NOT suggest high volatility."

    sys_prompt = SystemMessage(content="You are the Head of Global Research. Synthesize an intraday market thesis.")
    hum_prompt = HumanMessage(content=f"Quant: {state['quant_summary']}\nMacro: {state['macro_context']}\nCRITICAL RULE: {guardrail}\nDraft a 1-paragraph brief strictly following the rule.")
    
    return {"final_thesis": llm.invoke([sys_prompt, hum_prompt]).content}

workflow = StateGraph(ResearchState)
workflow.add_node("Quant", quant_analyst)
workflow.add_node("Macro", macro_economist)
workflow.add_node("Head", head_of_research)
workflow.set_entry_point("Quant")
workflow.add_edge("Quant", "Macro")
workflow.add_edge("Macro", "Head")
workflow.add_edge("Head", END)
research_app = workflow.compile()