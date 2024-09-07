import streamlit as st
from api import run_llm_api_test
from chatbot_ui import chatbot_ui

def show_api_page():
    st.title("API Page")
    st.write("This is the API page content.")

    if st.button("Run LLM API Test"):
        with st.spinner("Running LLM API test..."):
            result = run_llm_api_test()
        st.success(result)

    if st.button("Go to Chatbot"):
        st.session_state.page = "chatbot"
        st.rerun()

    if st.button("Go back to Main Page"):
        st.session_state.page = "upload"
        st.rerun()

def show_chatbot_page():
    st.title("Readme-png chatbot")
    chatbot_ui()

    if st.button("Go back to API Page"):
        st.session_state.page = "api"
        st.rerun()