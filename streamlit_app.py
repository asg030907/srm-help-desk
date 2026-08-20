"""
streamlit_app.py
A single-file Streamlit UI for demoing the agent live — no separate API
deployment needed. Talks directly to AgentExecutor in-process.

Run locally:   streamlit run streamlit_app.py
Deploy free:   push this repo to GitHub, then create an app at
               share.streamlit.io pointing at streamlit_app.py.
"""

import streamlit as st

from src.agent.executor import AgentExecutor
from src.utils.config import get_settings

st.set_page_config(page_title="AI Agent Prototype", page_icon="🤖", layout="centered")


@st.cache_resource
def get_executor() -> AgentExecutor:
    """
    Build the executor once per app instance (not per user session) — the
    underlying agent/LLM client is stateless and expensive to rebuild.
    Conversation memory is still tracked per session_id below.
    """
    return AgentExecutor()


def main() -> None:
    st.title("🤖 AI Agent Prototype")
    st.caption("CrewAI agent with search, calculator, and weather tools.")

    settings = get_settings()
    if not settings.anthropic_api_key:
        st.warning(
            "No ANTHROPIC_API_KEY configured. Set it in `.env` locally, or in "
            "your Streamlit Cloud app's Settings → Secrets before deploying.",
            icon="⚠️",
        )

    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask the agent something...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                executor = get_executor()
                result = executor.run(
                    message=user_input,
                    session_id=st.session_state.session_id,
                )
                st.session_state.session_id = result["session_id"]
                st.markdown(result["response"])

        st.session_state.messages.append({"role": "assistant", "content": result["response"]})

    with st.sidebar:
        st.subheader("Session")
        st.text(f"ID: {st.session_state.session_id or '(new)'}")
        if st.button("Reset conversation"):
            st.session_state.session_id = None
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()
