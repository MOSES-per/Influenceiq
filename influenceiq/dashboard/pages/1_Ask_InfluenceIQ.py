import sys
from pathlib import Path

# Make `influenceiq` importable when Streamlit runs this page
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import streamlit as st

from influenceiq.agent.agent import run_agent
from influenceiq.config import settings

st.set_page_config(page_title="Ask InfluenceIQ", page_icon="💬", layout="wide")
st.title("💬 Ask InfluenceIQ")
st.caption(
    "Chat with an AI agent that analyzes YouTube and Reddit creators using InfluenceIQ's "
    "scoring engine. It calls tools for real data instead of guessing."
)

if not settings.GEMINI_API_KEY:
    st.error("GEMINI_API_KEY is missing. Create a .env file in the project root (see .env.example).")
    st.stop()

EXAMPLES = [
    "Analyze the YouTube channel MrBeast",
    "Compare YouTube creators MKBHD and Linus Tech Tips. Who is safer to partner with?",
    "How is the Authenticity Index calculated?",
]

if "chat" not in st.session_state:
    st.session_state.chat = []  # each item: {"role", "content", "trace"}

with st.sidebar:
    st.header("Try asking")
    for example in EXAMPLES:
        if st.button(example, use_container_width=True):
            st.session_state.pending = example
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.chat = []
        st.rerun()
    st.caption(f"Model: {settings.GEMINI_MODEL}")

for item in st.session_state.chat:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])
        if item.get("trace"):
            with st.expander(f"🔧 Tools used ({len(item['trace'])})"):
                for step in item["trace"]:
                    st.code(f"{step['tool']}({step['args']})  [{step['seconds']}s]", language="python")

prompt = st.chat_input("Ask about a creator...") or st.session_state.pop("pending", None)

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat]
    st.session_state.chat.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = run_agent(history, prompt)
        st.markdown(result["answer"])
        if result["trace"]:
            with st.expander(f"🔧 Tools used ({len(result['trace'])})"):
                for step in result["trace"]:
                    st.code(f"{step['tool']}({step['args']})  [{step['seconds']}s]", language="python")

    st.session_state.chat.append(
        {"role": "assistant", "content": result["answer"], "trace": result["trace"]}
    )
